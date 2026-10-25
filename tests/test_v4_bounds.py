"""Independent oracle tests and real offline checks for both C2.1 entry paths."""

import asyncio
from datetime import date
import hashlib
from pathlib import Path

import pytest

from agent import context
from eval import check_bounds_consistency as checker
from eval.check_c21_replay import BEFORE_SHA256, OfflineSession, replay
from eval.v4_bounds import WINDOW_EXPRESSIONS, question_bounds, window_bounds


EXPECTED = ((15, 22), (15, 22), (8, 15), (8, 10), (8, 11),
            (8, 13), (8, 15), (8, 18), (8, 22), (15, 22))
ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("expression,days", tuple(zip(WINDOW_EXPRESSIONS, EXPECTED)))
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


@pytest.mark.parametrize("question", checker.INVALID_QUESTIONS)
def test_real_new_entry_and_independent_parser_reject_invalid_questions(question):
    glossary = (ROOT / "eval/glossary.md").read_text()
    with pytest.raises(ValueError):
        question_bounds(question)
    with pytest.raises(ValueError):
        asyncio.run(context.c2_date_context_for_question(question, OfflineSession(), glossary))


def test_new_entry_real_offline_gate_all_105_intervals_and_adversarial_cases():
    report = asyncio.run(checker.check_bounds_consistency())
    assert report["legal_intervals"] == 105
    assert report["case_count"] == 345
    assert all(row["status"] in {"pass", "rejected_as_required"} for row in report["results"])


def test_legacy_full_context_replay_uses_original_source_and_real_database(tmp_path):
    current = (ROOT / "agent/context.py").read_bytes()
    marker = b"\n\nasync def c2_date_context_for_question"
    original = current[:current.index(marker)]
    assert hashlib.sha256(original).hexdigest() == BEFORE_SHA256
    before = tmp_path / "before.py"
    before.write_bytes(original)
    report = tmp_path / "replay.md"
    result = asyncio.run(replay(before, report))
    assert result == {"compared": 86, "identical": 86, "failures": []}
    assert report.read_text().count("| PASS |") == 86


def test_non_text_questions_are_rejected_without_a_session():
    with pytest.raises(ValueError):
        question_bounds(None)
    with pytest.raises(ValueError):
        asyncio.run(context.c2_date_context_for_question(None, None, ""))
