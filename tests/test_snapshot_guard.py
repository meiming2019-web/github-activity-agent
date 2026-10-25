"""The missing-snapshot policy must not hide corrupt files or unrelated tests."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import conftest as policy


def test_only_missing_snapshot_is_optional(tmp_path):
    snapshot = tmp_path / "github.duckdb"
    assert policy._snapshot_missing(snapshot)
    snapshot.write_bytes(b"existing but deliberately invalid DuckDB bytes")
    assert not policy._snapshot_missing(snapshot)
    assert not policy._snapshot_missing(tmp_path)
    unreadable = Mock()
    unreadable.stat.side_effect = PermissionError("synthetic permission failure")
    with pytest.raises(PermissionError, match="synthetic"):
        policy._snapshot_missing(unreadable)


@pytest.mark.parametrize("present", [False, True])
def test_collection_guards_only_exact_snapshot_dependent_functions(tmp_path, monkeypatch, present):
    snapshot = tmp_path / "github.duckdb"
    if present:
        snapshot.write_bytes(b"present; validity must be checked by the original tests")
    monkeypatch.setattr(policy, "SNAPSHOT_PATH", snapshot)
    items = []
    for filename, names in policy.FROZEN_SNAPSHOT_TESTS.items():
        for name in names:
            items.append(SimpleNamespace(path=Path(filename), originalname=name,
                                         name=name + "[parameterized-case]", add_marker=Mock()))
    unrelated = [SimpleNamespace(path=Path("test_mcp_server.py"), originalname="test_metadata_is_bounded_to_three_known_tables",
                                 name="test_metadata_is_bounded_to_three_known_tables", add_marker=Mock()),
                 SimpleNamespace(path=Path("test_v4_generation.py"), originalname="test_item8_assertions_reject_invalid_references",
                                 name="test_item8_assertions_reject_invalid_references[empty]", add_marker=Mock())]
    policy.pytest_collection_modifyitems(items + unrelated)
    for item in items:
        assert item.add_marker.call_count == (0 if present else 1)
        if not present:
            marker = item.add_marker.call_args.args[0]
            assert marker.name == "skip"
            assert "data/github.duckdb is missing" in marker.kwargs["reason"]
            assert "does not validate" in marker.kwargs["reason"]
    assert all(item.add_marker.call_count == 0 for item in unrelated)
