"""Download, filter, and ingest an inclusive UTC range of GH Archive hours."""

import argparse
from datetime import datetime, timedelta, timezone
import gzip
import json
from pathlib import Path
import re
import sys

import duckdb
import requests
from tqdm import tqdm


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BATCH_SIZE = 1000
INSERT_EVENTS = """
    INSERT INTO events (event_id, repo_id, repo_name, type, actor, created_at, payload_json)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(event_id) DO NOTHING
"""


def parse_hour(value):
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}", value):
        raise argparse.ArgumentTypeError("hour must use YYYY-MM-DD-HH in UTC")
    try:
        return datetime.strptime(value, "%Y-%m-%d-%H").replace(tzinfo=timezone.utc)
    except ValueError as error:
        raise argparse.ArgumentTypeError("hour must be a valid UTC date and hour (00-23)") from error


def iter_hours(start, end):
    while start <= end:
        yield start
        start += timedelta(hours=1)


def load_repos(path):
    if not path.is_file():
        raise ValueError(f"Repository list not found: {path}. Create it with one owner/repo per line.")
    repos = {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}
    if not repos:
        raise ValueError(f"Repository list is empty: {path}. Add at least one owner/repo.")
    if any(not re.fullmatch(r"[^/\s]+/[^/\s]+", repo) for repo in repos):
        raise ValueError(f"Invalid repository list: {path}. Use one owner/repo per nonempty line.")
    return repos


def download_archive(source_file, raw_dir):
    destination = raw_dir / source_file
    if destination.is_file():
        print(f"Using cached archive: {source_file}")
        return destination
    raw_dir.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(destination.name + ".part")
    if partial.exists():
        print(f"Restarting incomplete download: {partial.name}")
    try:
        # Each file gets one request; incomplete downloads restart from byte zero.
        with requests.get(
            f"https://data.gharchive.org/{source_file}",
            stream=True, timeout=(10, 120), allow_redirects=False,
        ) as response:
            response.raise_for_status()
            if response.status_code != 200:
                raise ValueError(f"Expected HTTP 200, received HTTP {response.status_code}")
            total = int(response.headers["Content-Length"]) if "Content-Length" in response.headers else None
            written = 0
            with partial.open("wb") as output:
                with tqdm(total=total, unit="B", unit_scale=True, desc=source_file) as progress:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            output.write(chunk)
                            written += len(chunk)
                            progress.update(len(chunk))
            if total is not None and written != total:
                raise ValueError("Incomplete download: size does not match Content-Length")
        partial.replace(destination)
    except Exception:
        partial.unlink(missing_ok=True)
        raise
    return destination


def ingest_file(connection, archive, repos):
    source_file = archive.name
    if connection.execute(
        "SELECT 1 FROM ingest_log WHERE source_file = ?", [source_file]
    ).fetchone():
        return None
    rows_seen = rows_kept = 0
    batch = []
    connection.execute("BEGIN TRANSACTION")
    try:
        with archive.open("rb") as compressed:
            if compressed.read(2) != b"\x1f\x8b":
                raise gzip.BadGzipFile("Invalid gzip header; the archive may be empty or corrupt")
        with gzip.open(archive, "rt", encoding="utf-8") as source:
            for line_number, line in enumerate(source, 1):
                event = json.loads(line)
                if not isinstance(event, dict):
                    raise ValueError(f"Line {line_number}: expected a JSON event object")
                rows_seen += 1
                repo = event.get("repo")
                if not isinstance(repo, dict) or repo.get("name") not in repos:
                    continue
                event_id = event.get("id")
                if not isinstance(event_id, str) or not event_id:
                    raise ValueError(f"Line {line_number}: matched event requires a nonempty string id")
                created_at = datetime.fromisoformat(event["created_at"])
                if created_at.tzinfo is None:
                    raise ValueError(f"Line {line_number}: created_at must include a UTC offset")
                created_at = created_at.astimezone(timezone.utc).replace(tzinfo=None)
                actor = event.get("actor") or {}
                batch.append((
                    event_id, repo.get("id"), repo["name"], event.get("type"),
                    actor.get("login"), created_at,
                    json.dumps(event.get("payload"), ensure_ascii=True, separators=(",", ":")),
                ))
                rows_kept += 1
                if len(batch) >= BATCH_SIZE:
                    connection.executemany(INSERT_EVENTS, batch)
                    batch.clear()
        if batch:
            connection.executemany(INSERT_EVENTS, batch)
        connection.execute(
            "INSERT INTO ingest_log (source_file, ingested_at, rows_seen, rows_kept) VALUES (?, ?, ?, ?)",
            [source_file, datetime.now(timezone.utc).replace(tzinfo=None), rows_seen, rows_kept],
        )
        connection.execute("COMMIT")
    except Exception:
        connection.execute("ROLLBACK")
        raise
    return rows_seen, rows_kept


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", required=True, type=parse_hour, help="First UTC hour: YYYY-MM-DD-HH")
    parser.add_argument("--end", required=True, type=parse_hour, help="Last UTC hour, inclusive: YYYY-MM-DD-HH")
    parser.add_argument("--repos", type=Path, default=PROJECT_ROOT / "repos.txt", help="Fixed repository list for this dataset")
    parser.add_argument("--raw-dir", type=Path, default=PROJECT_ROOT / "data/raw", help="Downloaded hourly archives")
    parser.add_argument("--database", type=Path, default=PROJECT_ROOT / "data/github.duckdb", help="Destination DuckDB file")
    args = parser.parse_args(argv)
    if args.start > args.end:
        parser.error("--start must be earlier than or equal to --end")
    total = int((args.end - args.start).total_seconds() // 3600) + 1
    succeeded = skipped = failed = seen = kept = 0
    try:
        repos = load_repos(args.repos)
        args.database.parent.mkdir(parents=True, exist_ok=True)
        # This write-only ingestion task requires writable tables, unlike the query agent.
        with duckdb.connect(str(args.database), config={"memory_limit": "512MB"}) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY, repo_id BIGINT, repo_name TEXT, type TEXT,
                    actor TEXT, created_at TIMESTAMP, payload_json TEXT
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS ingest_log (
                    source_file TEXT PRIMARY KEY, ingested_at TIMESTAMP,
                    rows_seen BIGINT, rows_kept BIGINT
                )
            """)
            print(f"Processing {total} hourly files in UTC, sequentially.")
            print("Resume assumes the same repository list. rows_kept counts matches, including duplicate IDs.")
            for index, hour in enumerate(iter_hours(args.start, args.end), 1):
                source_file = f"{hour:%Y-%m-%d}-{hour.hour}.json.gz"
                print(f"[{index}/{total}] {source_file}", flush=True)
                try:
                    if connection.execute(
                        "SELECT 1 FROM ingest_log WHERE source_file = ?", [source_file]
                    ).fetchone():
                        skipped += 1
                        print("Already ingested; skipped download and ingestion.")
                        continue
                    archive = download_archive(source_file, args.raw_dir)
                    result = ingest_file(connection, archive, repos)
                    if result is None:
                        skipped += 1
                        continue
                    rows_seen, rows_kept = result
                    succeeded += 1
                    seen += rows_seen
                    kept += rows_kept
                    print(f"Committed: rows_seen={rows_seen}, rows_kept={rows_kept} (matched records).")
                except Exception as error:
                    failed += 1
                    print(
                        f"Failed {source_file}: {error}. No rows committed for this file. "
                        "Check the source and permissions; remove a corrupt cached archive before rerunning.",
                        file=sys.stderr, flush=True,
                    )
        print(f"Summary: files={total}, ingested={succeeded}, skipped={skipped}, failed={failed}.")
        print(f"Newly processed files: rows_seen={seen}, rows_kept={kept} (matches, not newly inserted rows).")
    except (OSError, ValueError, duckdb.Error) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
