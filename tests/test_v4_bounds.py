"""Offline unit tests for the independent bounds and fail-closed comparison gate."""

from datetime import date
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from eval import check_bounds_consistency as checker
from eval.v4_bounds import WINDOW_EXPRESSIONS, window_bounds


EXPECTED = (
    (15, 22), (15, 22), (8, 15), (8, 10), (8, 11),
    (8, 13), (8, 15), (8, 18), (8, 22), (15, 22),
)


@pytest.mark.parametrize("expression,days", zip(WINDOW_EXPRESSIONS, EXPECTED))
def test_independent_bounds_match_adjudication(expression, days):
    assert window_bounds(expression) == tuple(date(2026, 10, day) for day in days)


@pytest.mark.parametrize("expression", (
    "last 3 days", "last 14 days", "past two weeks", "since October 8, 2026",
    "October 7 through October 9, 2026", "October 8 through October 22, 2026",
    "October 10 through October 9, 2026", "UTC date",
))
def test_unauthorized_or_outside_snapshot_windows_are_rejected(expression):
    with pytest.raises(ValueError):
        window_bounds(expression)


@pytest.mark.parametrize("fault", (None, "unrecognized", "mismatch"))
def test_gate_checks_every_adopted_expression_and_fails_closed(monkeypatch, capsys, fault):
    execute = Mock(return_value=SimpleNamespace(
        truncated=False, rows=[["2026-10-08T00:02:49", "2026-10-21T23:58:01"]]
    ))
    windows = {}
    for expression, (start, end) in zip(WINDOW_EXPRESSIONS, EXPECTED):
        key = "last 7 days" if expression == "the last 7 days" else (
            f'explicit range "{expression}"' if expression.startswith("October ") else expression
        )
        windows[key] = {"start_inclusive": f"2026-10-{start:02d}",
                        "end_exclusive": f"2026-10-{end:02d}"}
    target = 'explicit range "October 8 through October 10, 2026"'
    if fault == "unrecognized":
        del windows[target]
    elif fault == "mismatch":
        windows[target]["end_exclusive"] = "2026-10-12"
    injection = Mock(return_value="BOUNDARIES\n" + json.dumps({"windows": windows}))
    monkeypatch.setattr(checker, "execute_select", execute)
    monkeypatch.setattr(checker, "frozen_date_boundaries", injection)
    if fault is None:
        report = checker.check_bounds_consistency()
        assert all(item["status"] == "pass" for item in report["results"])
    else:
        with pytest.raises(AssertionError, match=f"October 8 through October 10, 2026: {fault}"):
            checker.check_bounds_consistency()
    evidence = json.loads(capsys.readouterr().out)
    assert len(evidence["results"]) == len(WINDOW_EXPRESSIONS) == 10
    assert evidence["snapshot_start_inclusive"] == "2026-10-08"
    assert evidence["snapshot_end_exclusive"] == "2026-10-22"
    assert evidence["results"][4]["status"] == (fault or "pass")
    execute.assert_called_once_with(
        "SELECT MIN(created_at) AS first_event, MAX(created_at) AS last_event FROM events"
    )
    injection.assert_called_once()
