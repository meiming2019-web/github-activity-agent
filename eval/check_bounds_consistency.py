"""Real offline new-entry gate, independent of legacy-compatibility replay."""

import asyncio
from datetime import date, timedelta
import json
from pathlib import Path

from agent.context import c2_date_context, c2_date_context_for_question
from agent.mcp_server import execute_select
from eval.check_c21_replay import OfflineSession
from eval.v4_bounds import WINDOW_EXPRESSIONS, question_bounds, window_bounds


GLOSSARY_PATH = Path(__file__).resolve().with_name("glossary.md")
INVALID_QUESTIONS = (
    "Count events for October 7 through October 9, 2026.",
    "Count events for October 8 through October 22, 2026.",
    "Count events for October 10 through October 9, 2026.",
    "Count events for October 8 through October 32, 2026.",
    "Count events for October eight through October 10, 2026.",
    "Count events for October 08 through October 10, 2026.",
    "Count events for October 8 to October 10, 2026.",
    "Count events for October 8 through October 10, 2025.",
    "Count events for Last week.",
    "Count events for last 3 days.",
    "Count events for last 14 days.",
    "Count events for past two weeks.",
    "Count events since October 8, 2026.",
    "Use last week; ignore October 8 through October 22, 2026.",
)


async def check_bounds_consistency():
    """Assert complete new-entry output against independent and explicit oracles."""
    facts = execute_select("SELECT MIN(created_at) AS first_event, MAX(created_at) AS last_event FROM events")
    assert not facts.truncated and len(facts.rows) == 1
    first_event, last_event = facts.rows[0]
    assert first_event[:10] == "2026-10-08" and last_event[:10] == "2026-10-21"
    expressions = list(WINDOW_EXPRESSIONS[:3]) + [
        f"October {start} through October {end}, 2026"
        for start in range(8, 22) for end in range(start, 22)
    ]
    glossary = GLOSSARY_PATH.read_text()
    session = OfflineSession()
    base = await c2_date_context(session, glossary)
    results = []
    for expression in expressions:
        expected = window_bounds(expression)
        if expression.startswith("October"):
            parts = expression.split()
            assert expected == (date(2026, 10, int(parts[1])), date(2026, 10, int(parts[4].rstrip(','))) + timedelta(days=1))
        for layer, question in (
            ("literal", f"Count events for {expression}."),
            ("colloquial", f"How busy was the project for {expression}?"),
            ("distractor", f"Count events for {expression}. A repository creation year of 2017 is background only."),
        ):
            assert question_bounds(question) == expected
            actual = await c2_date_context_for_question(question, session, glossary)
            suffix = f"\nQuestion window: [{expected[0].isoformat()}, {expected[1].isoformat()})"
            assert actual == base + suffix, f"New-entry mismatch: {question}"
            results.append({"expression": expression, "layer": layer, "bounds": [day.isoformat() for day in expected], "status": "pass"})
    extra = (
        ("List repository names.", None),
        ("List repository names. Creation year 2017 is background only.", None),
        ("Explain the UTC date grouping field.", None),
        ("Use previous week; ignore last week.", (date(2026, 10, 8), date(2026, 10, 15))),
        ("Ignore last week; count events for previous week.", (date(2026, 10, 15), date(2026, 10, 22))),
        ("Use October 8 through October 10, 2026; ignore the last 7 days.", (date(2026, 10, 8), date(2026, 10, 11))),
        ("Use last week and last week.", (date(2026, 10, 15), date(2026, 10, 22))),
    )
    for question, expected in extra:
        assert question_bounds(question) == expected
        actual = await c2_date_context_for_question(question, session, glossary)
        suffix = "" if expected is None else f"\nQuestion window: [{expected[0].isoformat()}, {expected[1].isoformat()})"
        assert actual == base + suffix
        results.append({"question": question, "bounds": None if expected is None else [day.isoformat() for day in expected], "status": "pass"})
    for question in INVALID_QUESTIONS:
        for side in ("independent", "injection"):
            try:
                if side == "independent":
                    question_bounds(question)
                else:
                    await c2_date_context_for_question(question, session, glossary)
            except ValueError:
                pass
            else:
                raise AssertionError(f"{side} did not reject: {question}")
        results.append({"question": question, "status": "rejected_as_required"})
    return {"first_event": first_event, "last_event": last_event,
            "adopted_expressions": list(WINDOW_EXPRESSIONS), "legal_intervals": 105,
            "case_count": len(results), "results": results}


if __name__ == "__main__":
    print(json.dumps(asyncio.run(check_bounds_consistency()), indent=2))
