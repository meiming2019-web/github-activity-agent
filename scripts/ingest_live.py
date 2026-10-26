"""Explicit live ingestion; never run on import and never write the frozen database."""

import argparse
from datetime import datetime, timedelta, timezone
import fcntl
import gzip
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import duckdb
import requests

from agent.live_context import utc_now
from agent.live_server import FROZEN_DATABASE, LIVE_DATABASE, isolated_server, live_path
from scripts.ingest import load_repos


def download_hour(hour, destination):
    """Always refetch requested public archives; no cached late-data blind spot."""
    name = f'{hour:%Y-%m-%d}-{hour.hour}.json.gz'
    with requests.get(f'https://data.gharchive.org/{name}', stream=True,
                      timeout=(10, 120), allow_redirects=False) as response:
        response.raise_for_status()
        if response.status_code != 200:
            raise ValueError('Archive response was not HTTP 200.')
        written = 0
        with Path(destination).open('wb') as output:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    output.write(chunk)
                    written += len(chunk)
        if 'Content-Length' in response.headers and written != int(response.headers['Content-Length']):
            raise ValueError('Incomplete archive download.')


def seed_catalog(connection, source, repos):
    """Read the frozen catalog without a writable ATTACH or metadata API call."""
    if connection.execute('SELECT COUNT(*) FROM repos').fetchone()[0]:
        actual = {row[0] for row in connection.execute('SELECT name FROM repos').fetchall()}
        if actual != repos:
            raise ValueError('Existing live catalog does not match repos.txt.')
        return
    server = isolated_server(source, live=False)
    result = server.execute_select('SELECT repo_id, name, language, topics, stars, forks, open_issues, created_at, fetched_at FROM repos ORDER BY name',
                                   row_cap=101)
    if result.truncated or len(result.rows) != 100 or {r[1] for r in result.rows} != repos:
        raise ValueError('Frozen catalog must contain exactly the 100 names in repos.txt.')
    connection.executemany('INSERT INTO repos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', result.rows)


def ingest_archive(connection, archive, repos, start, cutoff):
    """Insert validated matching events; the caller owns the hourly transaction."""
    batch, seen, kept = [], 0, 0
    with gzip.open(archive, 'rt', encoding='utf-8') as source:
        for line in source:
            event = json.loads(line)
            if not isinstance(event, dict):
                raise ValueError('Archive contains a non-object event.')
            seen += 1
            repo = event.get('repo')
            if not isinstance(repo, dict) or repo.get('name') not in repos:
                continue
            if repo.get('id') != repos[repo['name']]:
                raise ValueError('Event repo_id disagrees with the frozen catalog.')
            if not isinstance(event.get('id'), str) or not event['id']:
                raise ValueError('Matching event requires a nonempty string id.')
            created = datetime.fromisoformat(event['created_at'])
            if created.tzinfo is None:
                raise ValueError('Event timestamp requires a timezone.')
            created = created.astimezone(timezone.utc)
            if not start <= created < cutoff:
                continue
            actor = event.get('actor') or {}
            batch.append((event['id'], repo['id'], repo['name'], event.get('type'), actor.get('login'),
                          created.replace(tzinfo=None), json.dumps(event.get('payload'), separators=(',', ':'))))
            kept += 1
            if len(batch) == 1000:
                connection.executemany('INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT(event_id) DO NOTHING', batch)
                batch.clear()
    if batch:
        connection.executemany('INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT(event_id) DO NOTHING', batch)
    return seen, kept


def ingest(*, database=LIVE_DATABASE, catalog=FROZEN_DATABASE, repos_file=ROOT / 'repos.txt', clock=None, fetch=download_hour):
    """Refresh 24 completed hours and every retained gap, with atomic hour commits."""
    database = live_path(database, catalog)
    # Also guard the actual frozen database when a test or caller supplies another catalog.
    database = live_path(database)
    if Path(catalog).resolve() == database or (Path(catalog).exists() and database.exists() and Path(catalog).samefile(database)):
        raise ValueError('Catalog source and live output must differ.')
    repos = load_repos(Path(repos_file))
    if len(repos) != 100:
        raise ValueError('Live ingestion requires the unchanged 100-repository universe.')
    now = utc_now(clock)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start, cutoff = today - timedelta(days=14), now.replace(minute=0, second=0, microsecond=0)
    database.parent.mkdir(parents=True, exist_ok=True)
    lock_path = str(database) + '.ingest.lock'
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    summary = {'succeeded': [], 'failed': [], 'skipped': 0, 'as_of': now.isoformat()}
    with os.fdopen(fd, 'a') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        live_path(database, catalog)
        with duckdb.connect(str(database), config={'memory_limit': '512MB', 'threads': 2,
                            'enable_external_access': False, 'autoinstall_known_extensions': False,
                            'autoload_known_extensions': False}) as connection:
            connection.execute('BEGIN TRANSACTION')
            try:
                connection.execute('CREATE TABLE IF NOT EXISTS repos (repo_id BIGINT PRIMARY KEY, name TEXT UNIQUE, language TEXT, topics TEXT, stars BIGINT, forks BIGINT, open_issues BIGINT, created_at TIMESTAMP, fetched_at TIMESTAMP)')
                connection.execute('CREATE TABLE IF NOT EXISTS events (event_id TEXT PRIMARY KEY, repo_id BIGINT, repo_name TEXT, type TEXT, actor TEXT, created_at TIMESTAMP, payload_json TEXT)')
                connection.execute('CREATE TABLE IF NOT EXISTS ingest_log (source_file TEXT PRIMARY KEY, ingested_at TIMESTAMP, rows_seen BIGINT, rows_kept BIGINT)')
                seed_catalog(connection, catalog, repos)
                connection.execute('DELETE FROM events WHERE created_at < ?', [start.replace(tzinfo=None)])
                # Archive names sort lexically by date, independently of the unpadded hour.
                connection.execute('DELETE FROM ingest_log WHERE substr(source_file, 1, 10) < ?', [start.date().isoformat()])
                connection.execute('COMMIT')
            except Exception:
                connection.execute('ROLLBACK')
                raise
            known = {r[0] for r in connection.execute('SELECT source_file FROM ingest_log').fetchall()}
            repo_ids = dict(connection.execute('SELECT name, repo_id FROM repos').fetchall())
            hour = start
            with tempfile.TemporaryDirectory(prefix='github-live-hour-') as temporary:
                archive = Path(temporary) / 'hour.json.gz'
                while hour < cutoff:
                    name = f'{hour:%Y-%m-%d}-{hour.hour}.json.gz'
                    if name in known and hour < cutoff - timedelta(hours=24):
                        summary['skipped'] += 1
                    else:
                        try:
                            archive.unlink(missing_ok=True)
                            fetch(hour, archive)
                            connection.execute('BEGIN TRANSACTION')
                            try:
                                seen, kept = ingest_archive(connection, archive, repo_ids, start, cutoff)
                                connection.execute('INSERT INTO ingest_log VALUES (?, ?, ?, ?) ON CONFLICT(source_file) DO UPDATE SET ingested_at=excluded.ingested_at, rows_seen=excluded.rows_seen, rows_kept=excluded.rows_kept',
                                                   [name, now.replace(tzinfo=None), seen, kept])
                                connection.execute('COMMIT')
                            except Exception:
                                connection.execute('ROLLBACK')
                                raise
                            summary['succeeded'].append(name)
                        except Exception as error:
                            # Keep earlier committed data on refresh failure; never mark failed gaps complete.
                            summary['failed'].append({'hour': name, 'error': type(error).__name__})
                    hour += timedelta(hours=1)
    return summary


def main(argv=None):
    """Production paths are fixed; this command alone enables real ingestion."""
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    try:
        result = ingest()
        print(json.dumps(result, sort_keys=True))
        return 1 if result['failed'] else 0
    except Exception as error:
        print(f'Live ingestion stopped ({type(error).__name__}). Check paths, catalog, permissions, and archive availability.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
