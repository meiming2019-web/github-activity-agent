"""Independent generator-side boundaries for the adjudicated v4 vocabulary."""

from datetime import date, timedelta
import re


# Adopted before generation: 10 windows x 3 metrics x 2 scopes x 3 paraphrases.
# An unsupported entry is a hard failure, never a reason to shrink this inventory.
WINDOW_EXPRESSIONS = (
    "the last 7 days",
    "last week",
    "previous week",
    "October 8 through October 9, 2026",
    "October 8 through October 10, 2026",
    "October 8 through October 12, 2026",
    "October 8 through October 14, 2026",
    "October 8 through October 17, 2026",
    "October 8 through October 21, 2026",
    "October 15 through October 21, 2026",
)


def window_bounds(expression):
    """Return UTC date bounds without importing or invoking injection-side code."""
    named = {
        "the last 7 days": (date(2026, 10, 15), date(2026, 10, 22)),
        "last week": (date(2026, 10, 15), date(2026, 10, 22)),
        "previous week": (date(2026, 10, 8), date(2026, 10, 15)),
    }
    if expression in named:
        return named[expression]
    match = re.fullmatch(r"October (\d{1,2}) through October (\d{1,2}), 2026", expression)
    if match is None:
        raise ValueError(f"Unauthorized v4 window expression: {expression}")
    first, last = (int(value) for value in match.groups())
    if not 8 <= first <= last <= 21:
        raise ValueError("Explicit v4 ranges must lie within October 8–21, 2026.")
    return date(2026, 10, first), date(2026, 10, last) + timedelta(days=1)
