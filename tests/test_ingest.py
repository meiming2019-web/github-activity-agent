"""Offline ingestion tests with real temporary DuckDB databases."""

from datetime import datetime, timezone
import gzip
import importlib.util
import json
from pathlib import Path

import duckdb
import pytest
import requests


SPEC = importlib.util.spec_from_file_location(
    "ingest", Path(__file__).resolve().parents[1] / "scripts/ingest.py"
)
ingest = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ingest)


@pytest.fixture(autouse=True)
def forbid_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Tests must not access the network")
    monkeypatch.setattr(ingest.requests, "get", forbidden)


@pytest.fixture
def project(tmp_path, monkeypatch):
    root = tmp_path / "project"
    root.mkdir()
    (root / "repos.txt").write_text("python/cpython\ntorvalds/linux\n", encoding="utf-8")
    monkeypatch.setattr(ingest, "PROJECT_ROOT", root)
    return root


def event(event_id="1", **changes):
    record = {
        "id": event_id, "repo": {"id": 42, "name": "python/cpython"},
        "type": "PushEvent", "actor": {"login": "octocat"},
        "created_at": "2026-10-08T00:00:00Z",
        "payload": {"commits": [{"sha": "abc", "message": "Example"}]},
    }
    record.update(changes)
    return record


def archive_bytes(records):
    return gzip.compress(b"".join(json.dumps(record).encode() + b"\n" for record in records))


def cache_archive(project, hour, content):
    path = project / "data/raw" / f"2026-10-08-{hour}.json.gz"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def run_range(end="01", *extra):
    return ingest.main(["--start", "2026-10-08-00", "--end", f"2026-10-08-{end}", *extra])


class MockResponse:
    status_code = 200

    def __init__(self, content, error=None):
        self.content = content
        self.error = error
        self.headers = {"Content-Length": str(len(content))}
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True

    def raise_for_status(self):
        if self.error:
            raise self.error

    def iter_content(self, chunk_size):
        for offset in range(0, len(self.content), 17):
            yield self.content[offset:offset + 17]


def test_inclusive_range_has_336_utc_hours():
    start = ingest.parse_hour("2026-10-08-00")
    end = ingest.parse_hour("2026-10-21-23")
    hours = list(ingest.iter_hours(start, end))
    assert len(hours) == 336
    assert hours[0] == datetime(2026, 10, 8, tzinfo=timezone.utc)
    assert hours[-1] == datetime(2026, 10, 21, 23, tzinfo=timezone.utc)
    assert all(hour.tzinfo is timezone.utc for hour in hours)
    assert hours[24] == datetime(2026, 10, 9, tzinfo=timezone.utc)
    assert list(ingest.iter_hours(start, start)) == [start]
    assert ingest.parse_hour("2024-02-29-23").day == 29


@pytest.mark.parametrize("start,end", [
    ("2026-10-08-01", "2026-10-08-00"),
    ("2026-02-30-00", "2026-10-08-00"),
    ("2026-10-08-24", "2026-10-09-00"),
    ("2026-10-08-0", "2026-10-09-00"),
])
def test_invalid_range_creates_no_data(project, start, end, capsys):
    with pytest.raises(SystemExit) as error:
        ingest.main(["--start", start, "--end", end])
    assert error.value.code == 2
    assert not (project / "data").exists()
    assert "error:" in capsys.readouterr().err


@pytest.mark.parametrize("contents", [None, "\n", "invalid-repository\n"])
def test_missing_empty_or_invalid_repo_list_fails_clearly(project, contents, capsys):
    path = project / "repos.txt"
    if contents is None:
        path.unlink()
    else:
        path.write_text(contents)
    assert run_range("00") == 1
    assert not (project / "data").exists()
    assert "Error:" in capsys.readouterr().err


def test_cached_files_filter_preserve_fields_and_resume_idempotently(project, monkeypatch, capsys):
    first = event(created_at="2026-10-08T01:15:00+02:00")
    second = event("2", repo={"id": 84, "name": "torvalds/linux"}, actor=None, payload=[1, {"key": True}])
    records = [first, first, event("outside", repo={"name": "other/repo"}),
               event("missing", repo=None), {"type": "WatchEvent"}, second]
    first_archive = cache_archive(project, 0, archive_bytes(records))
    second_archive = cache_archive(project, 1, archive_bytes([second, event("3", payload="different shape")]))
    original_list = (project / "repos.txt").read_bytes()
    monkeypatch.setattr(ingest, "BATCH_SIZE", 2)
    monkeypatch.chdir(project.parent)
    assert run_range() == 0
    with duckdb.connect(str(project / "data/github.duckdb")) as connection:
        rows = connection.execute("SELECT * FROM events ORDER BY event_id").fetchall()
        assert len(rows) == 3
        assert rows[0][:6] == ("1", 42, "python/cpython", "PushEvent", "octocat", datetime(2026, 10, 7, 23, 15))
        assert json.loads(rows[0][6]) == first["payload"]
        assert rows[1][1:3] == (84, "torvalds/linux")
        assert rows[1][4] is None
        assert json.loads(rows[1][6]) == second["payload"]
        assert json.loads(rows[2][6]) == "different shape"
        assert [(column[0], column[1]) for column in connection.execute("DESCRIBE events").fetchall()] == [
            ("event_id", "VARCHAR"), ("repo_id", "BIGINT"), ("repo_name", "VARCHAR"),
            ("type", "VARCHAR"), ("actor", "VARCHAR"), ("created_at", "TIMESTAMP"), ("payload_json", "VARCHAR"),
        ]
        logs = connection.execute("SELECT * FROM ingest_log ORDER BY source_file").fetchall()
        assert [row[2:] for row in logs] == [(6, 3), (2, 2)]
        assert all(isinstance(row[1], datetime) and row[1].tzinfo is None for row in logs)
        assert ingest.ingest_file(connection, first_archive, {"python/cpython"}) is None
    first_archive.unlink()
    second_archive.unlink()
    assert run_range() == 0
    with duckdb.connect(str(project / "data/github.duckdb"), read_only=True) as connection:
        assert connection.execute("SELECT * FROM events ORDER BY event_id").fetchall() == rows
        assert connection.execute("SELECT * FROM ingest_log ORDER BY source_file").fetchall() == logs
    assert (project / "repos.txt").read_bytes() == original_list
    output = capsys.readouterr().out
    assert output.isascii()
    assert "rows_seen=8, rows_kept=5 (matches, not newly inserted rows)" in output
    assert "ingested=0, skipped=2, failed=0" in output


def test_partial_download_is_restarted_and_published_atomically_with_custom_paths(project, monkeypatch, capsys):
    raw = project.parent / "downloads"
    raw.mkdir()
    source_file = "2026-10-08-0.json.gz"
    destination = raw / source_file
    partial = raw / (source_file + ".part")
    partial.write_bytes(b"incomplete old bytes")
    repos = project.parent / "list.txt"
    repos.write_text("python/cpython\n")
    database = project.parent / "output/events.duckdb"
    compressed = archive_bytes([event()])
    response = MockResponse(compressed)
    calls = []

    def chunks(chunk_size):
        for offset in range(0, len(compressed), 17):
            assert not destination.exists()
            assert partial.exists()
            yield compressed[offset:offset + 17]

    def get(url, **kwargs):
        calls.append((url, kwargs))
        return response

    monkeypatch.setattr(response, "iter_content", chunks)
    monkeypatch.setattr(ingest.requests, "get", get)
    assert run_range("00", "--repos", str(repos), "--raw-dir", str(raw), "--database", str(database)) == 0
    assert calls == [("https://data.gharchive.org/2026-10-08-0.json.gz", {
        "stream": True, "timeout": (10, 120), "allow_redirects": False,
    })]
    assert response.closed
    assert destination.read_bytes() == compressed
    assert not partial.exists()
    assert not (project / "data").exists()
    with duckdb.connect(str(database), read_only=True) as connection:
        assert connection.execute("SELECT COUNT(*) FROM events").fetchone() == (1,)
    assert "Restarting incomplete download" in capsys.readouterr().out


def test_http_failure_continues_to_next_file_without_retry(project, monkeypatch, capsys):
    failure = MockResponse(b"", requests.HTTPError("HTTP 503 Service Unavailable"))
    success = MockResponse(archive_bytes([event("later")]))
    responses = iter([failure, success])
    calls = []

    def get(url, **kwargs):
        calls.append(url)
        return next(responses)

    monkeypatch.setattr(ingest.requests, "get", get)
    assert run_range() == 1
    assert calls == [f"https://data.gharchive.org/2026-10-08-{hour}.json.gz" for hour in (0, 1)]
    assert failure.closed and success.closed
    assert not (project / "data/raw/2026-10-08-0.json.gz").exists()
    assert not list((project / "data/raw").glob("*.part"))
    with duckdb.connect(str(project / "data/github.duckdb"), read_only=True) as connection:
        assert connection.execute("SELECT event_id FROM events").fetchall() == [("later",)]
        assert connection.execute("SELECT source_file FROM ingest_log").fetchall() == [("2026-10-08-1.json.gz",)]
    output = capsys.readouterr()
    assert "Failed 2026-10-08-0.json.gz: HTTP 503" in output.err
    assert "ingested=1, skipped=0, failed=1" in output.out


@pytest.mark.parametrize("failure_kind", ["empty_file", "invalid_gzip", "truncated_gzip", "json", "event_insert", "log_insert"])
def test_failed_file_rolls_back_events_and_log_then_continues(project, monkeypatch, failure_kind, capsys):
    monkeypatch.setattr(ingest, "BATCH_SIZE", 1)
    first = event("rolled-back")
    if failure_kind == "empty_file":
        content = b""
    elif failure_kind == "invalid_gzip":
        content = b"not gzip"
    elif failure_kind == "truncated_gzip":
        content = archive_bytes([first])[:-8]
    elif failure_kind == "json":
        content = gzip.compress(json.dumps(first).encode() + b"\ninvalid json\n")
    elif failure_kind == "event_insert":
        content = archive_bytes([first, event("invalid", repo={"id": "not-an-integer", "name": "python/cpython"})])
    else:
        content = archive_bytes([first])
        (project / "data").mkdir()
        with duckdb.connect(str(project / "data/github.duckdb")) as connection:
            connection.execute("""
                CREATE TABLE ingest_log (
                    source_file TEXT PRIMARY KEY, ingested_at TIMESTAMP,
                    rows_seen BIGINT, rows_kept BIGINT CHECK (rows_kept = 0)
                )
            """)
    failed_archive = cache_archive(project, 0, content)
    later = [] if failure_kind == "log_insert" else [event("later")]
    cache_archive(project, 1, archive_bytes(later))
    assert run_range() == 1
    assert failed_archive.read_bytes() == content
    with duckdb.connect(str(project / "data/github.duckdb"), read_only=True) as connection:
        expected_ids = [] if failure_kind == "log_insert" else [("later",)]
        assert connection.execute("SELECT event_id FROM events").fetchall() == expected_ids
        assert connection.execute("SELECT source_file, rows_seen, rows_kept FROM ingest_log").fetchall() == [
            ("2026-10-08-1.json.gz", len(later), len(later)),
        ]
    output = capsys.readouterr()
    assert "Failed 2026-10-08-0.json.gz" in output.err
    assert "No rows committed for this file" in output.err
    assert "ingested=1, skipped=0, failed=1" in output.out


@pytest.mark.parametrize("failure_kind", ["short_response", "connection_lost"])
def test_incomplete_http_body_never_becomes_completed_archive(project, monkeypatch, failure_kind):
    response = MockResponse(b"partial")
    calls = []
    if failure_kind == "short_response":
        response.headers["Content-Length"] = "100"
    else:
        def chunks(chunk_size):
            yield b"part"
            raise requests.ConnectionError("Connection lost")
        monkeypatch.setattr(response, "iter_content", chunks)

    def get(url, **kwargs):
        calls.append(url)
        return response

    monkeypatch.setattr(ingest.requests, "get", get)
    assert run_range("00") == 1
    assert len(calls) == 1
    assert response.closed
    assert list((project / "data/raw").iterdir()) == []
    with duckdb.connect(str(project / "data/github.duckdb"), read_only=True) as connection:
        assert connection.execute("SELECT COUNT(*) FROM events").fetchone() == (0,)
        assert connection.execute("SELECT COUNT(*) FROM ingest_log").fetchone() == (0,)
