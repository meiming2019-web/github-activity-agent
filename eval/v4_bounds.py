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


def question_bounds(question_text):
    """Independently locate canonical mentions and select the earliest valid span."""
    if not isinstance(question_text, str):
        raise ValueError("Question text must be a string.")
    spans = []
    for expression in WINDOW_EXPRESSIONS[:3]:
        cursor = 0
        while True:
            index = question_text.find(expression, cursor)
            if index < 0:
                break
            stop = index + len(expression)
            left_ok = index == 0 or not (question_text[index - 1].isalnum() or question_text[index - 1] == "_")
            right_ok = stop == len(question_text) or not (question_text[stop].isalnum() or question_text[stop] == "_")
            if left_ok and right_ok:
                spans.append((index, stop, window_bounds(expression)))
            cursor = stop
    for token in re.finditer(r"\bOctober\b", question_text):
        if any(left <= token.start() < right for left, right, _ in spans):
            continue
        year = question_text.find("2026", token.end())
        if year < 0:
            raise ValueError("Incomplete explicit date range.")
        expression = question_text[token.start():year + 4]
        canonical = re.fullmatch(r"October ([1-9]|[12][0-9]|3[01]) through October ([1-9]|[12][0-9]|3[01]), 2026", expression)
        if canonical is None:
            raise ValueError("Noncanonical explicit range.")
        spans.append((token.start(), year + 4, window_bounds(expression)))
    reserved = {"january", "february", "march", "april", "may", "june", "july", "august",
                "september", "october", "november", "december", "through", "since"}
    tokens = list(re.finditer(r"\b\w+\b", question_text))
    for index, token in enumerate(tokens):
        value = token.group().lower()
        nearby = [item.group().lower() for item in tokens[index:index + 3]]
        marker = value in reserved or nearby[:2] in (["last", "week"], ["previous", "week"])
        marker = marker or nearby == ["past", "two", "weeks"]
        marker = marker or (len(nearby) == 3 and nearby[0] == "last" and nearby[1].isdigit() and nearby[2] == "days")
        if marker and not any(left <= token.start() < right for left, right, _ in spans):
            raise ValueError("Unauthorized or malformed window syntax.")
    return min(spans, key=lambda item: item[0])[2] if spans else None
