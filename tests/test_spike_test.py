"""Offline checks with mock HTTP responses and real in-memory DuckDB."""

import gzip
import importlib.util
import json
from pathlib import Path

import pytest
import requests


SPEC = importlib.util.spec_from_file_location(
    "spike_test", Path(__file__).resolve().parents[1] / "scripts" / "spike_test.py"
)
spike = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(spike)


@pytest.fixture(autouse=True)
def prevent_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Tests must not access the network")
    monkeypatch.setattr(spike.requests, "get", forbidden)


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
        for start in range(0, len(self.content), 13):
            yield self.content[start:start + 13]


def test_missing_repo_list_creates_twenty_examples(tmp_path):
    path = tmp_path / "repos.txt"
    repos = spike.load_repos(path)
    assert len(repos) == len(set(repos)) == 20
    assert len(path.read_text().splitlines()) == 20
    assert all(len(repo.split("/")) == 2 for repo in repos)
    assert "python/cpython" in repos


def test_existing_repo_list_is_preserved(tmp_path):
    path = tmp_path / "repos.txt"
    original = b"custom/repository\n\npython/cpython\ncustom/repository\n"
    path.write_bytes(original)
    assert spike.load_repos(path) == ["custom/repository", "python/cpython"]
    assert path.read_bytes() == original


def test_complete_run_downloads_once_and_computes_real_statistics(tmp_path, monkeypatch, capsys):
    events = [
        {"type": "PushEvent", "repo": {"name": "python/cpython"}, "payload": {"commits": [{"sha": "abc"}]}},
        {"type": "IssuesEvent", "repo": {"name": "outside/repo"}, "payload": {"issue": {"number": 1}}},
        {"type": "PushEvent", "repo": {"name": "torvalds/linux"}, "payload": "different shape"},
        {"type": "WatchEvent", "payload": [1, 2]},
        {"type": "PushEvent", "repo": None, "payload": {"commits": "different type"}},
        {"repo": {"name": "python/cpython"}, "payload": None},
    ]
    compressed = gzip.compress("\n".join(map(json.dumps, events)).encode())
    response = MockResponse(compressed)
    calls = []

    def get(url, **kwargs):
        calls.append((url, kwargs))
        return response

    project = tmp_path / "project"
    project.mkdir()
    temporary = tmp_path / "temporary"
    temporary.mkdir()
    monkeypatch.setattr(spike, "PROJECT_ROOT", project)
    monkeypatch.setattr(spike.tempfile, "tempdir", str(temporary))
    monkeypatch.setattr(spike.requests, "get", get)
    ticks = iter([10.0, 12.0, 20.0, 23.0])
    monkeypatch.setattr(spike, "perf_counter", lambda: next(ticks))
    monkeypatch.chdir(tmp_path)

    assert spike.main(["--date", "2026-10-21", "--hour", "10"]) == 0
    assert calls == [("https://data.gharchive.org/2026-10-21-10.json.gz", {
        "stream": True, "timeout": (10, 120), "allow_redirects": False,
    })]
    assert response.closed
    assert (project / "data/raw/2026-10-21-10.json.gz").read_bytes() == compressed
    assert not (tmp_path / "repos.txt").exists()
    assert list(temporary.iterdir()) == []
    assert not list(tmp_path.rglob("*.duckdb"))
    captured = capsys.readouterr()
    output = captured.out
    assert output.isascii()
    assert "Downloading" in captured.err
    assert "| type | count |" in output
    assert "| PushEvent | 3 |" in output
    assert "| IssuesEvent | 1 |" in output
    assert "| WatchEvent | 1 |" in output
    assert "| (missing) | 1 |" in output
    assert "Total events: 6" in output
    assert "Events in repos.txt: 3" in output
    assert "1 MB = 1,000,000 bytes" in output
    assert output.split("| Metric | Value |\n", 1)[1].splitlines() == [
        "| --- | ---: |",
        f"| Compressed file size (MB) | {len(compressed) / 1_000_000:.6f} |",
        "| Download time (seconds) | 2.000 |",
        "| Decompression + load time (seconds) | 3.000 |",
        "| Retention rate (%) | 50.00 |",
    ]


def test_empty_archive_has_zero_retention(tmp_path):
    archive = tmp_path / "empty.json.gz"
    archive.write_bytes(gzip.compress(b""))
    statistics = spike.analyze_archive(archive, ["python/cpython"])
    assert statistics["total"] == statistics["retained"] == 0
    assert statistics["retention_percent"] == 0.0
    assert statistics["distribution"] == []


def test_empty_repo_list_retains_no_events(tmp_path):
    path = tmp_path / "repos.txt"
    path.write_text("\n")
    archive = tmp_path / "events.json.gz"
    archive.write_bytes(gzip.compress(b'{"type":"PushEvent","repo":{"name":"python/cpython"}}\n'))
    statistics = spike.analyze_archive(archive, spike.load_repos(path))
    assert statistics["total"] == 1
    assert statistics["retained"] == 0
    assert statistics["retention_percent"] == 0.0


@pytest.mark.parametrize("arguments", [
    [],
    ["--date", "2026-10-21"],
    ["--hour", "10"],
    ["--date", "2026-02-30", "--hour", "10"],
    ["--date", "2026-1-01", "--hour", "10"],
    ["--date", "20261021", "--hour", "10"],
    ["--date", "2026-10-21", "--hour", "-1"],
    ["--date", "2026-10-21", "--hour", "24"],
    ["--date", "2026-10-21", "--hour", "1.5"],
])
def test_invalid_arguments_fail_before_creating_files(arguments, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(spike, "PROJECT_ROOT", tmp_path)
    with pytest.raises(SystemExit) as error:
        spike.main(arguments)
    assert error.value.code == 2
    assert list(tmp_path.iterdir()) == []
    assert "error:" in capsys.readouterr().err


@pytest.mark.parametrize("hour", ["0", "23"])
def test_hour_boundaries_are_valid(hour):
    assert spike.parse_hour(hour) == int(hour)
    assert spike.parse_date("2024-02-29") == "2024-02-29"


def test_existing_archive_is_not_overwritten(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(spike, "PROJECT_ROOT", tmp_path)
    (tmp_path / "repos.txt").write_text("python/cpython\n")
    archive = tmp_path / "data/raw/2026-10-21-10.json.gz"
    archive.parent.mkdir(parents=True)
    archive.write_bytes(b"existing user file")
    assert spike.main(["--date", "2026-10-21", "--hour", "10"]) == 1
    assert archive.read_bytes() == b"existing user file"
    assert "Refusing to overwrite existing archive" in capsys.readouterr().err


def test_http_failure_is_not_retried(tmp_path, monkeypatch, capsys):
    calls = []
    response = MockResponse(b"", requests.HTTPError("HTTP 404 Not Found"))

    def get(*args, **kwargs):
        calls.append(args)
        return response

    monkeypatch.setattr(spike.requests, "get", get)
    monkeypatch.setattr(spike, "PROJECT_ROOT", tmp_path)
    assert spike.main(["--date", "2026-10-21", "--hour", "10"]) == 1
    assert len(calls) == 1
    assert response.closed
    assert list((tmp_path / "data/raw").iterdir()) == []
    assert "Error: HTTP 404 Not Found" in capsys.readouterr().err


def test_interrupted_download_removes_partial_file(tmp_path, monkeypatch):
    response = MockResponse(b"incomplete")
    calls = []

    def chunks(chunk_size):
        yield b"part"
        raise requests.ConnectionError("Connection interrupted")

    def get(*args, **kwargs):
        calls.append(args)
        return response

    monkeypatch.setattr(response, "iter_content", chunks)
    monkeypatch.setattr(spike.requests, "get", get)
    archive = tmp_path / "events.json.gz"
    with pytest.raises(requests.ConnectionError, match="Connection interrupted"):
        spike.download_archive("https://data.gharchive.org/2026-10-21-10.json.gz", archive)
    assert len(calls) == 1
    assert not archive.exists()
    assert response.closed


def test_invalid_gzip_cleans_up_temporary_files(tmp_path, monkeypatch):
    temporary = tmp_path / "temporary"
    temporary.mkdir()
    monkeypatch.setattr(spike.tempfile, "tempdir", str(temporary))
    archive = tmp_path / "invalid.json.gz"
    archive.write_bytes(b"not gzip")
    with pytest.raises(gzip.BadGzipFile):
        spike.analyze_archive(archive, [])
    assert list(temporary.iterdir()) == []
    assert archive.read_bytes() == b"not gzip"
