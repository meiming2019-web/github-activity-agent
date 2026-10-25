"""Offline hard gate comparing independent v4 bounds with frozen injection output.

Run from the repository root: python -m eval.check_bounds_consistency
No experimental Agent, MCP session, or model client is started.
"""

from datetime import datetime, timedelta
import json
from pathlib import Path

from agent.context import frozen_date_boundaries
from agent.mcp_server import execute_select
from eval.v4_bounds import WINDOW_EXPRESSIONS, window_bounds


GLOSSARY_PATH = Path(__file__).resolve().with_name("glossary.md")


def check_bounds_consistency():
    """Print complete per-expression evidence and assert recognition and equality."""
    facts = execute_select(
        "SELECT MIN(created_at) AS first_event, MAX(created_at) AS last_event FROM events"
    )
    assert not facts.truncated and len(facts.rows) == 1 and len(facts.rows[0]) == 2
    first_event, last_event = facts.rows[0]
    snapshot = (
        datetime.fromisoformat(first_event).date(),
        datetime.fromisoformat(last_event).date() + timedelta(days=1),
    )
    injected = json.loads(
        frozen_date_boundaries(GLOSSARY_PATH.read_text(), first_event, last_event).split("\n", 1)[1]
    )["windows"]
    results = []
    for expression in WINDOW_EXPRESSIONS:
        start, end = window_bounds(expression)
        assert snapshot[0] <= start < end <= snapshot[1]
        expected = {"start_inclusive": start.isoformat(), "end_exclusive": end.isoformat()}
        # These are the existing output labels, not new injection semantics.
        if expression == "the last 7 days":
            key = "last 7 days"
        elif expression.startswith("October "):
            key = f'explicit range "{expression}"'
        else:
            key = expression
        actual = injected.get(key)
        status = "unrecognized" if actual is None else "pass" if actual == expected else "mismatch"
        results.append({"expression": expression, "injection_key": key,
                        "generator": expected, "injection": actual, "status": status})
    report = {
        "first_event": first_event, "last_event": last_event,
        "snapshot_start_inclusive": snapshot[0].isoformat(),
        "snapshot_end_exclusive": snapshot[1].isoformat(),
        "results": results,
        "grouping_only": {"UTC date": "CAST(created_at AS DATE); not a window or boundary check"},
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    failures = [item for item in results if item["status"] != "pass"]
    assert not failures, "Boundary hard gate failed: " + "; ".join(
        f'{item["expression"]}: {item["status"]}' for item in failures
    )
    return report


if __name__ == "__main__":
    check_bounds_consistency()
