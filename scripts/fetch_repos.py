"""Fetch repository metadata from GitHub into the local repos table."""

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import sys
import time

import duckdb
import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_NAME = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?/[A-Za-z0-9_.-]+")


def load_token(path):
    """Read plain KEY=value assignments; quotes and comments are supported, not shell syntax."""
    if not path.is_file():
        raise ValueError("Missing .env file. Add GITHUB_TOKEN to the project .env before running.")
    token = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        key, separator, value = line.partition("=")
        if not separator or key.strip() != "GITHUB_TOKEN":
            continue
        value = value.strip()
        if value[:1] in ("'", '"'):
            end = value.find(value[0], 1)
            if end < 0 or (value[end + 1:].strip() and not value[end + 1:].strip().startswith("#")):
                raise ValueError("Invalid GITHUB_TOKEN assignment: use matching quotes on a single line.")
            token = value[1:end].strip()
        else:
            token = value.split("#", 1)[0].strip()
    if not token:
        raise ValueError("GITHUB_TOKEN is missing or empty in the project .env.")
    if any(character.isspace() for character in token):
        raise ValueError("GITHUB_TOKEN must be a single token without whitespace.")
    return token


def load_repos(path):
    if not path.is_file():
        raise ValueError("Missing repos.txt. Add one owner/repo per line before running.")
    repos = list(dict.fromkeys(line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()))
    if not repos:
        raise ValueError("repos.txt is empty. Add at least one owner/repo.")
    for repo in repos:
        if not REPO_NAME.fullmatch(repo) or repo.rsplit("/", 1)[-1] in {".", ".."}:
            raise ValueError("Invalid repository name in repos.txt. Use owner/repo, without URLs or extra paths.")
    return repos


def fetch_repo(repo, token):
    headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}"}
    retried = False
    while True:
        try:
            with requests.get(
                f"https://api.github.com/repos/{repo}", headers=headers,
                timeout=(10, 60), allow_redirects=False,
            ) as response:
                if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining", "").strip() == "0":
                    if retried:
                        raise RuntimeError("Rate limit is still exhausted after one retry; rerun after the next reset.")
                    try:
                        reset = int(response.headers["X-RateLimit-Reset"])
                        if reset < 0:
                            raise ValueError
                        datetime.fromtimestamp(reset, timezone.utc)
                    except (KeyError, ValueError, OverflowError, OSError):
                        raise RuntimeError("Rate limit reset header is missing or invalid; no retry performed.") from None
                    wait_seconds = max(0, math.ceil(reset - time.time())) + 1
                else:
                    if response.status_code != 200:
                        raise RuntimeError(
                            f"GitHub returned HTTP {response.status_code}; check repository access and token permissions. "
                            "Redirects are not followed."
                        )
                    try:
                        metadata = response.json()
                    except ValueError:
                        raise RuntimeError("GitHub returned invalid JSON.") from None
                    return metadata, datetime.now(timezone.utc).replace(tzinfo=None)
        except requests.RequestException as error:
            # Request exceptions can contain credentials; never print their original text.
            raise RuntimeError(f"GitHub request failed ({type(error).__name__}); check connectivity and access.") from None
        print(f"Rate limit reached for {repo}; waiting {wait_seconds} seconds before retrying.", flush=True)
        time.sleep(wait_seconds)
        retried = True


def metadata_row(metadata, fetched_at):
    if not isinstance(metadata, dict):
        raise ValueError("GitHub metadata must be a JSON object.")
    created_at = datetime.fromisoformat(metadata["created_at"])
    if created_at.tzinfo is None:
        raise ValueError("Repository created_at must include a UTC offset.")
    return (
        metadata["id"], metadata["full_name"], metadata.get("language"),
        json.dumps(metadata.get("topics"), ensure_ascii=True, separators=(",", ":")),
        metadata["stargazers_count"], metadata["forks_count"], metadata["open_issues_count"],
        created_at.astimezone(timezone.utc).replace(tzinfo=None), fetched_at,
    )


def prepare_table(connection):
    connection.execute("""
        CREATE TABLE IF NOT EXISTS repos (
            repo_id BIGINT PRIMARY KEY, name TEXT, language TEXT, topics TEXT,
            stars BIGINT, forks BIGINT, open_issues BIGINT,
            created_at TIMESTAMP, fetched_at TIMESTAMP
        )
    """)
    actual = [(row[1], row[2], bool(row[5])) for row in connection.execute("PRAGMA table_info('repos')").fetchall()]
    expected = [
        ("repo_id", "BIGINT", True), ("name", "VARCHAR", False), ("language", "VARCHAR", False),
        ("topics", "VARCHAR", False), ("stars", "BIGINT", False), ("forks", "BIGINT", False),
        ("open_issues", "BIGINT", False), ("created_at", "TIMESTAMP", False), ("fetched_at", "TIMESTAMP", False),
    ]
    if actual != expected:
        raise ValueError("Existing repos schema is incompatible with the required columns and repo_id primary key; no migration performed.")


def main(argv=None):
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    successful = failed = 0
    try:
        token = load_token(PROJECT_ROOT / ".env")
        repos = load_repos(PROJECT_ROOT / "repos.txt")
        database = PROJECT_ROOT / "data/github.duckdb"
        database.parent.mkdir(parents=True, exist_ok=True)
        # This metadata-writing task needs writable SQL; the query agent remains out of scope.
        with duckdb.connect(str(database), config={"memory_limit": "512MB"}) as connection:
            prepare_table(connection)
            for index, repo in enumerate(repos, 1):
                print(f"[{index}/{len(repos)}] Fetching {repo}", flush=True)
                try:
                    metadata, fetched_at = fetch_repo(repo, token)
                    row = metadata_row(metadata, fetched_at)
                    connection.execute("""
                        INSERT INTO repos (repo_id, name, language, topics, stars, forks, open_issues, created_at, fetched_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(repo_id) DO UPDATE SET
                            name = excluded.name, language = excluded.language, topics = excluded.topics,
                            stars = excluded.stars, forks = excluded.forks, open_issues = excluded.open_issues,
                            created_at = excluded.created_at, fetched_at = excluded.fetched_at
                    """, row)
                    successful += 1
                    print(f"Updated {repo}.")
                except (RuntimeError, ValueError, KeyError, TypeError, OverflowError, duckdb.Error) as error:
                    failed += 1
                    message = str(error).replace(token, "[REDACTED]")
                    print(f"Failed {repo}: {message}", file=sys.stderr)
    except (OSError, ValueError, duckdb.Error) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(f"Summary: successful={successful}, failed={failed}.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
