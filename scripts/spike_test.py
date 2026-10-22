"""Measure one GH Archive hourly file using an in-memory DuckDB database."""

import argparse
from datetime import date
import gzip
from pathlib import Path
import re
import shutil
import sys
import tempfile
from time import perf_counter

import duckdb
import requests
from tqdm import tqdm


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_REPOS = (
    "torvalds/linux",
    "python/cpython",
    "microsoft/vscode",
    "kubernetes/kubernetes",
    "tensorflow/tensorflow",
    "pytorch/pytorch",
    "facebook/react",
    "vuejs/core",
    "angular/angular",
    "nodejs/node",
    "golang/go",
    "rust-lang/rust",
    "apache/spark",
    "apache/airflow",
    "django/django",
    "pallets/flask",
    "scikit-learn/scikit-learn",
    "pandas-dev/pandas",
    "numpy/numpy",
    "duckdb/duckdb",
)


def parse_date(value):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD")
    try:
        date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("date must be a valid calendar date") from error
    return value


def parse_hour(value):
    try:
        hour = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("hour must be an integer from 0 to 23") from error
    if not 0 <= hour <= 23:
        raise argparse.ArgumentTypeError("hour must be an integer from 0 to 23")
    return hour


def load_repos(path):
    if not path.exists():
        with path.open("x", encoding="utf-8") as output:
            output.write("\n".join(EXAMPLE_REPOS) + "\n")
        print("Created repos.txt with 20 example repositories.")
    repos = {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}
    if any(not re.fullmatch(r"[^/\s]+/[^/\s]+", repo) for repo in repos):
        raise ValueError("repos.txt must contain one owner/repo per nonempty line")
    return sorted(repos)


def download_archive(url, destination):
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing archive: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    started = perf_counter()
    created = False
    try:
        # Redirects are disabled so this operation makes exactly one HTTP request.
        with requests.get(url, stream=True, timeout=(10, 120), allow_redirects=False) as response:
            response.raise_for_status()
            if response.status_code != 200:
                raise ValueError(f"Expected HTTP 200, received HTTP {response.status_code}")
            total = int(response.headers["Content-Length"]) if "Content-Length" in response.headers else None
            written = 0
            with destination.open("xb") as output:
                created = True
                with tqdm(total=total, unit="B", unit_scale=True, desc="Downloading") as progress:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            output.write(chunk)
                            written += len(chunk)
                            progress.update(len(chunk))
            if total is not None and written != total:
                raise ValueError("Downloaded size does not match Content-Length")
    except Exception:
        if created:
            destination.unlink(missing_ok=True)
        raise
    return destination.stat().st_size / 1_000_000, perf_counter() - started


def analyze_archive(archive, repos):
    started = perf_counter()
    with tempfile.TemporaryDirectory(prefix="gharchive-spike-") as temporary:
        unpacked = Path(temporary) / "events.json"
        with gzip.open(archive, "rb") as source, unpacked.open("wb") as output:
            shutil.copyfileobj(source, output)
        with duckdb.connect(":memory:") as connection:
            connection.execute("CREATE TABLE events (type VARCHAR, repo_name VARCHAR)")
            if unpacked.stat().st_size:
                # Explicit columns avoid inferring unrelated, heterogeneous payloads.
                connection.execute(
                    """
                    INSERT INTO events
                    SELECT type, json_extract_string(repo, '$.name')
                    FROM read_json(?, format='newline_delimited',
                                   columns={'type': 'VARCHAR', 'repo': 'JSON'})
                    """,
                    [str(unpacked)],
                )
            load_seconds = perf_counter() - started
            total, retained = connection.execute(
                "SELECT COUNT(*), COUNT(*) FILTER (WHERE repo_name = ANY(?)) FROM events",
                [repos],
            ).fetchone()
            distribution = connection.execute(
                """
                SELECT COALESCE(type, '(missing)') AS type, COUNT(*) AS count
                FROM events GROUP BY 1 ORDER BY count DESC, type ASC
                """
            ).fetchall()
    return {
        "load_seconds": load_seconds,
        "total": total,
        "retained": retained,
        "retention_percent": retained / total * 100 if total else 0.0,
        "distribution": distribution,
    }


def print_report(size_mb, download_seconds, statistics):
    print("\nEvent type distribution")
    print("| type | count |")
    print("| --- | ---: |")
    for event_type, count in statistics["distribution"]:
        print(f"| {event_type} | {count} |")
    print(f"\nTotal events: {statistics['total']}")
    print(f"Events in repos.txt: {statistics['retained']}")
    print("Missing repository names count toward the total but are not retained.")
    print("Repository names are matched exactly. Missing event types appear as (missing).")
    print("\nSummary (1 MB = 1,000,000 bytes)")
    print("| Metric | Value |")
    print("| --- | ---: |")
    print(f"| Compressed file size (MB) | {size_mb:.6f} |")
    print(f"| Download time (seconds) | {download_seconds:.3f} |")
    print(f"| Decompression + load time (seconds) | {statistics['load_seconds']:.3f} |")
    print(f"| Retention rate (%) | {statistics['retention_percent']:.2f} |")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True, type=parse_date, help="UTC date in YYYY-MM-DD format")
    parser.add_argument("--hour", required=True, type=parse_hour, help="UTC hour from 0 to 23")
    args = parser.parse_args(argv)
    filename = f"{args.date}-{args.hour}.json.gz"
    archive = PROJECT_ROOT / "data" / "raw" / filename
    try:
        repos = load_repos(PROJECT_ROOT / "repos.txt")
        size_mb, download_seconds = download_archive(f"https://data.gharchive.org/{filename}", archive)
        statistics = analyze_archive(archive, repos)
        print_report(size_mb, download_seconds, statistics)
    except (OSError, EOFError, ValueError, requests.RequestException, duckdb.Error) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
