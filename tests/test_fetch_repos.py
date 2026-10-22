"""Offline metadata tests using fake tokens and temporary DuckDB files."""

from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path

import duckdb
import pytest
import requests
from requests.structures import CaseInsensitiveDict


SPEC = importlib.util.spec_from_file_location(
    "fetch_repos", Path(__file__).resolve().parents[1] / "scripts/fetch_repos.py"
)
fetch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fetch)
FAKE_TOKEN = "ghp_example_only_for_tests"


@pytest.fixture(autouse=True)
def forbid_network_and_sleep(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Unexpected network request or real sleep")
    monkeypatch.setattr(fetch.requests, "get", forbidden)
    monkeypatch.setattr(fetch.time, "sleep", forbidden)


@pytest.fixture
def project(tmp_path, monkeypatch):
    root = tmp_path / "project"
    root.mkdir()
    (root / ".env").write_text(f"GITHUB_TOKEN={FAKE_TOKEN}\n", encoding="utf-8")
    (root / "repos.txt").write_text("owner/first\nowner/second\n", encoding="utf-8")
    monkeypatch.setattr(fetch, "PROJECT_ROOT", root)
    return root


class MockResponse:
    def __init__(self, status=200, metadata=None, headers=None):
        self.status_code = status
        self.metadata = metadata
        self.headers = CaseInsensitiveDict(headers or {})
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True

    def json(self):
        if isinstance(self.metadata, Exception):
            raise self.metadata
        return self.metadata


def metadata(repo_id=1, **changes):
    result = {
        "id": repo_id, "full_name": "owner/first", "language": "Python", "topics": ["data", "agent"],
        "stargazers_count": 100, "forks_count": 12, "open_issues_count": 3,
        "created_at": "2020-01-02T01:30:00+02:00",
    }
    result.update(changes)
    return result


@pytest.mark.parametrize("assignment", [
    f"GITHUB_TOKEN = {FAKE_TOKEN} # comment",
    f'GITHUB_TOKEN="{FAKE_TOKEN}" # comment',
    f"GITHUB_TOKEN = '{FAKE_TOKEN}'",
])
def test_token_parser_supports_plain_values_quotes_and_comments(tmp_path, assignment):
    path = tmp_path / ".env"
    path.write_text("# ignored\nOTHER=value\n" + assignment + "\n")
    assert fetch.load_token(path) == FAKE_TOKEN


@pytest.mark.parametrize("contents", [None, "OTHER=value\n", "GITHUB_TOKEN='' # empty\n"])
def test_missing_or_empty_token_fails_before_side_effects(project, contents, monkeypatch, capsys):
    path = project / ".env"
    if contents is None:
        path.unlink()
    else:
        path.write_text(contents)
    monkeypatch.setenv("GITHUB_TOKEN", FAKE_TOKEN)
    assert fetch.main([]) == 1
    assert not (project / "data").exists()
    captured = capsys.readouterr()
    assert "Error:" in captured.err
    assert "GITHUB_TOKEN" in captured.err
    assert FAKE_TOKEN not in captured.out + captured.err


def test_invalid_token_quotes_do_not_echo_credentials(project, capsys):
    (project / ".env").write_text(f'GITHUB_TOKEN="{FAKE_TOKEN}\n')
    assert fetch.main([]) == 1
    assert not (project / "data").exists()
    output = capsys.readouterr()
    assert "matching quotes" in output.err
    assert FAKE_TOKEN not in output.err + output.out


@pytest.mark.parametrize("name", ["https://evil.example/repo", "owner/repo/issues", "owner/.."])
def test_invalid_repository_paths_fail_before_network_or_database(project, name, capsys):
    (project / "repos.txt").write_text(name)
    assert fetch.main([]) == 1
    assert not (project / "data").exists()
    assert "Invalid repository name" in capsys.readouterr().err


def test_mapping_upsert_refresh_and_events_preservation(project, monkeypatch, capsys):
    database = project / "data/github.duckdb"
    database.parent.mkdir()
    with duckdb.connect(str(database)) as connection:
        connection.execute("""
            CREATE TABLE events (
                event_id TEXT PRIMARY KEY, repo_id BIGINT, repo_name TEXT, type TEXT,
                actor TEXT, created_at TIMESTAMP, payload_json TEXT
            )
        """)
        connection.execute("INSERT INTO events VALUES ('kept', 1, 'owner/first', 'PushEvent', 'actor', TIMESTAMP '2026-10-08 00:00:00', '{}')")
        original_events = connection.execute("SELECT * FROM events").fetchall()
        original_schema = connection.execute("DESCRIBE events").fetchall()
    responses = [
        MockResponse(metadata=metadata()),
        MockResponse(metadata=metadata(2, full_name="owner/second", language=None, topics=None)),
    ]
    calls = []

    def get(url, **kwargs):
        calls.append((url, kwargs))
        return responses.pop(0)

    monkeypatch.setattr(fetch.requests, "get", get)
    monkeypatch.chdir(project.parent)
    before = datetime.now(timezone.utc).replace(tzinfo=None)
    assert fetch.main([]) == 0
    after = datetime.now(timezone.utc).replace(tzinfo=None)
    with duckdb.connect(str(database), read_only=True) as connection:
        rows = connection.execute("SELECT * FROM repos ORDER BY repo_id").fetchall()
        assert rows[0][:3] == (1, "owner/first", "Python")
        assert json.loads(rows[0][3]) == ["data", "agent"]
        assert rows[0][4:8] == (100, 12, 3, datetime(2020, 1, 1, 23, 30))
        assert rows[1][2] is None
        assert json.loads(rows[1][3]) is None
        assert all(before <= row[8] <= after and row[8].tzinfo is None for row in rows)
    responses.extend([
        MockResponse(metadata=metadata(full_name="owner/renamed", language="Go", topics=[],
                                       stargazers_count=150, forks_count=20, open_issues_count=4,
                                       created_at="2021-01-01T00:00:00Z")),
        MockResponse(metadata=metadata(2, full_name="owner/second", language=None, topics=None)),
    ])
    assert fetch.main([]) == 0
    with duckdb.connect(str(database), read_only=True) as connection:
        refreshed = connection.execute("SELECT * FROM repos ORDER BY repo_id").fetchall()
        assert len(refreshed) == 2
        assert refreshed[0][:8] == (1, "owner/renamed", "Go", "[]", 150, 20, 4, datetime(2021, 1, 1))
        assert refreshed[0][8] > rows[0][8]
        assert connection.execute("SELECT * FROM events").fetchall() == original_events
        assert connection.execute("DESCRIBE events").fetchall() == original_schema
    (project / "repos.txt").write_text("owner/first\nowner/first\n")
    responses.append(MockResponse(metadata=metadata(stargazers_count="invalid count")))
    assert fetch.main([]) == 1
    with duckdb.connect(str(database), read_only=True) as connection:
        assert connection.execute("SELECT * FROM repos ORDER BY repo_id").fetchall() == refreshed
        assert connection.execute("SELECT * FROM events").fetchall() == original_events
    assert [call[0] for call in calls] == [
        "https://api.github.com/repos/owner/first", "https://api.github.com/repos/owner/second",
        "https://api.github.com/repos/owner/first", "https://api.github.com/repos/owner/second",
        "https://api.github.com/repos/owner/first",
    ]
    for _, kwargs in calls:
        assert kwargs == {"headers": {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {FAKE_TOKEN}"},
                          "timeout": (10, 60), "allow_redirects": False}
    output = capsys.readouterr()
    assert "Summary: successful=2, failed=0." in output.out
    assert "Summary: successful=0, failed=1." in output.out
    assert FAKE_TOKEN not in output.out + output.err


@pytest.mark.parametrize("reset,expected_wait", [("1005", 6), ("900", 1)])
def test_rate_limit_waits_then_retries_same_request(monkeypatch, reset, expected_wait, capsys):
    limited = MockResponse(403, headers={"x-ratelimit-remaining": "0", "x-ratelimit-reset": reset})
    success = MockResponse(metadata=metadata())
    responses = iter([limited, success])
    calls = []
    waits = []

    def get(url, **kwargs):
        calls.append((url, kwargs))
        return next(responses)

    def sleep(seconds):
        assert limited.closed
        waits.append(seconds)

    monkeypatch.setattr(fetch.requests, "get", get)
    monkeypatch.setattr(fetch.time, "time", lambda: 1000.2)
    monkeypatch.setattr(fetch.time, "sleep", sleep)
    result, fetched_at = fetch.fetch_repo("owner/first", FAKE_TOKEN)
    assert result["id"] == 1
    assert isinstance(fetched_at, datetime) and fetched_at.tzinfo is None
    assert len(calls) == 2 and calls[0] == calls[1]
    assert waits == [expected_wait]
    assert success.closed
    assert f"waiting {expected_wait} seconds" in capsys.readouterr().out


@pytest.mark.parametrize("reset", [None, "not-an-epoch", "-1"])
def test_invalid_reset_header_fails_without_sleep_or_retry(monkeypatch, reset):
    headers = {"X-RateLimit-Remaining": "0"}
    if reset is not None:
        headers["X-RateLimit-Reset"] = reset
    response = MockResponse(403, headers=headers)
    calls = []

    def get(*args, **kwargs):
        calls.append(args)
        return response

    monkeypatch.setattr(fetch.requests, "get", get)
    with pytest.raises(RuntimeError, match="reset header is missing or invalid"):
        fetch.fetch_repo("owner/first", FAKE_TOKEN)
    assert len(calls) == 1
    assert response.closed


def test_repeated_exhaustion_is_bounded(monkeypatch):
    calls = []
    waits = []

    def get(*args, **kwargs):
        calls.append(args)
        return MockResponse(403, headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1005"})

    monkeypatch.setattr(fetch.requests, "get", get)
    monkeypatch.setattr(fetch.time, "time", lambda: 1000.2)
    monkeypatch.setattr(fetch.time, "sleep", waits.append)
    with pytest.raises(RuntimeError, match="after one retry"):
        fetch.fetch_repo("owner/first", FAKE_TOKEN)
    assert len(calls) == 2
    assert waits == [6]


def test_failures_continue_without_general_retries_or_secret_output(project, monkeypatch, capsys):
    (project / "repos.txt").write_text("\n".join(f"owner/repo{index}" for index in range(7)))
    responses = iter([
        MockResponse(403, headers={"X-RateLimit-Remaining": "7"}),
        MockResponse(404),
        MockResponse(302, headers={"Location": "https://evil.example/collect"}),
        requests.ConnectionError(f"Authorization: Bearer {FAKE_TOKEN}"),
        MockResponse(metadata=ValueError(FAKE_TOKEN)),
        MockResponse(metadata=metadata(created_at=FAKE_TOKEN)),
        MockResponse(metadata=metadata(7, full_name="owner/repo6")),
    ])
    calls = []

    def get(url, **kwargs):
        calls.append(url)
        assert kwargs["allow_redirects"] is False
        response = next(responses)
        if isinstance(response, Exception):
            raise response
        return response

    monkeypatch.setattr(fetch.requests, "get", get)
    assert fetch.main([]) == 1
    assert calls == [f"https://api.github.com/repos/owner/repo{index}" for index in range(7)]
    with duckdb.connect(str(project / "data/github.duckdb"), read_only=True) as connection:
        assert connection.execute("SELECT repo_id, name FROM repos").fetchall() == [(7, "owner/repo6")]
    output = capsys.readouterr()
    assert "Summary: successful=1, failed=6." in output.out
    assert "HTTP 403" in output.err and "HTTP 404" in output.err and "HTTP 302" in output.err
    assert "ConnectionError" in output.err
    assert FAKE_TOKEN not in output.out + output.err
    assert "Authorization" not in output.out + output.err


@pytest.mark.parametrize("conflict", ["wrong_columns", "missing_primary_key"])
def test_schema_conflict_is_reported_without_migration_or_network(project, conflict, capsys):
    database = project / "data/github.duckdb"
    database.parent.mkdir()
    with duckdb.connect(str(database)) as connection:
        if conflict == "wrong_columns":
            connection.execute("CREATE TABLE repos (repo_id BIGINT PRIMARY KEY, original TEXT)")
            connection.execute("INSERT INTO repos VALUES (1, 'preserve me')")
        else:
            connection.execute("""
                CREATE TABLE repos (repo_id BIGINT, name TEXT, language TEXT, topics TEXT,
                                    stars BIGINT, forks BIGINT, open_issues BIGINT,
                                    created_at TIMESTAMP, fetched_at TIMESTAMP)
            """)
            connection.execute("INSERT INTO repos (repo_id, name) VALUES (1, 'preserve me')")
        rows = connection.execute("SELECT * FROM repos").fetchall()
        schema = connection.execute("DESCRIBE repos").fetchall()
    assert fetch.main([]) == 1
    with duckdb.connect(str(database), read_only=True) as connection:
        assert connection.execute("SELECT * FROM repos").fetchall() == rows
        assert connection.execute("DESCRIBE repos").fetchall() == schema
    assert "schema is incompatible" in capsys.readouterr().err
