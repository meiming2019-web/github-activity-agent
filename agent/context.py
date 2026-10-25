"""Shared experiment/demo context and keyword glossary lookup."""

from datetime import date, datetime, timedelta
import json
import re


REFERENCE_DATE = "2026-10-22"


def lookup_glossary(glossary, term):
    needle = term.strip().casefold()
    headings = list(re.finditer(r"^(#{2,6})[ \t]+(.+)$", glossary, flags=re.MULTILINE))
    matches = []
    for index, heading in enumerate(headings):
        if not needle or needle not in heading.group(2).casefold():
            continue
        end = next((other.start() for other in headings[index + 1:]
                    if len(other.group(1)) <= len(heading.group(1))), len(glossary))
        matches.append(glossary[heading.start():end].strip())
    return "\n\n".join(matches) if matches else "No glossary sections matched the requested term."


def tool_payload(result):
    if result.is_error:
        raise RuntimeError("\n".join(block.text for block in result.content if block.type == "text"))
    if result.structured_content is not None:
        return result.structured_content
    return json.loads("\n".join(block.text for block in result.content if block.type == "text"))


async def shared_context(session):
    tables = {}
    for table in ("events", "repos"):
        description = tool_payload(await session.call_tool("describe_table", arguments={"table": table}))
        sample = tool_payload(await session.call_tool("sample_values", arguments={"table": table}))
        tables[table] = {"columns": description["columns"], "sample_rows": sample["rows"]}
    return "SHARED STATIC CONTEXT\n" + json.dumps({
        "reference_date": REFERENCE_DATE,
        "time_conventions": "All timestamps are UTC; created_at is stored as a UTC timestamp. Use half-open windows: created_at >= start AND created_at < end. Use literal dates, never CURRENT_DATE or CURRENT_TIMESTAMP.",
        "tables": tables,
    }, ensure_ascii=False, allow_nan=False)



DATE_BOUNDS_SQL = "SELECT MIN(created_at) AS first_event, MAX(created_at) AS last_event FROM events"


def frozen_date_boundaries(glossary, first_event, last_event):
    """Instantiate only the dated definitions at the existing frozen anchor."""
    conventions = lookup_glossary(glossary, "Time conventions")
    scope = lookup_glossary(glossary, "Dataset scope")
    reference = date.fromisoformat(REFERENCE_DATE)
    declared = re.search(r"`reference_date` = \*\*([0-9-]+)\*\*", conventions)
    if declared is None or date.fromisoformat(declared.group(1)) != reference:
        raise ValueError("The frozen reference date does not match the glossary.")

    def span(text):
        days = re.findall(r"([0-9]{4}-[0-9]{2}-[0-9]{2}) 00:00:00", text)
        if len(days) != 2:
            raise ValueError("Expected explicit full-UTC-day bounds in the frozen glossary.")
        return tuple(date.fromisoformat(day) for day in days)

    def named_date(month, day, month_format):
        return datetime.strptime(f"{reference.year} {month} {day}", f"%Y {month_format} %d").date()

    last = re.search(r'"The last (\d+) days" means the (\d+) full UTC days before `reference_date`:\s*`([^`]+)`', conventions)
    if last is None or last.group(1) != last.group(2):
        raise ValueError("The glossary's last-days definition is unavailable or inconsistent.")
    last_days = (reference - timedelta(days=int(last.group(2))), reference)
    if span(last.group(3)) != last_days:
        raise ValueError("The computed last-days bounds disagree with the frozen glossary.")

    weeks = re.search(r"previous = ([A-Za-z]+) (\d+)–(\d+), last = ([A-Za-z]+) (\d+)–(\d+)", conventions)
    if weeks is None:
        raise ValueError("The frozen, explicitly dated week definitions are unavailable.")
    previous = (named_date(weeks.group(1), weeks.group(2), "%b"),
                named_date(weeks.group(1), weeks.group(3), "%b") + timedelta(days=1))
    last_week = (named_date(weeks.group(4), weeks.group(5), "%b"),
                 named_date(weeks.group(4), weeks.group(6), "%b") + timedelta(days=1))
    # These are the glossary's fixed dated weeks, not generic rolling/calendar rules.
    if last_week != last_days or previous[1] != last_week[0]:
        raise ValueError("The frozen week definitions disagree with the declared reference.")

    example = re.search(r'An explicit range like "([^"]+)" means\s*`([^`]+)`', conventions)
    phrase = re.fullmatch(r"([A-Za-z]+) (\d+) through ([A-Za-z]+) (\d+), (\d{4})", example.group(1)) if example else None
    if phrase is None or int(phrase.group(5)) != reference.year:
        raise ValueError("The glossary's explicit-range example cannot be resolved at the frozen anchor.")
    explicit = (named_date(phrase.group(1), phrase.group(2), "%B"),
                named_date(phrase.group(3), phrase.group(4), "%B") + timedelta(days=1))
    if explicit != span(example.group(2)):
        raise ValueError("The inclusive-end example disagrees with the glossary's half-open bounds.")

    coverage = re.search(r"Coverage: (\d+) full UTC days, `([^`]+)`", scope)
    if coverage is None or not isinstance(first_event, str) or not isinstance(last_event, str):
        raise ValueError("Frozen snapshot coverage or observed event bounds are unavailable.")
    # Full UTC-day envelope comes from events, never reference_date minus a duration.
    snapshot = (datetime.fromisoformat(first_event).date(),
                datetime.fromisoformat(last_event).date() + timedelta(days=1))
    if snapshot != span(coverage.group(2)) or (snapshot[1] - snapshot[0]).days != int(coverage.group(1)):
        raise ValueError("Observed snapshot UTC dates disagree with glossary Dataset scope.")

    windows = {f"last {last.group(1)} days": last_days, "last week": last_week,
               "previous week": previous, f'explicit range "{example.group(1)}"': explicit,
               "full snapshot window": snapshot}
    return "PRECOMPUTED FROZEN DATE BOUNDARIES\n" + json.dumps({
        "reference_date": reference.isoformat(),
        "convention": "UTC half-open date windows: start inclusive, end exclusive.",
        "snapshot_source": "UTC day envelope of MIN/MAX(events.created_at), checked against Dataset scope; not reference-date subtraction.",
        "windows": {name: {"start_inclusive": start.isoformat(), "end_exclusive": end.isoformat()}
                    for name, (start, end) in windows.items()},
    }, ensure_ascii=False, sort_keys=True, allow_nan=False)


async def c2_date_context(session, glossary):
    payload = tool_payload(await session.call_tool("run_query", arguments={"sql": DATE_BOUNDS_SQL}))
    if payload.get("truncated") or len(payload.get("rows", [])) != 1 or len(payload["rows"][0]) != 2:
        raise ValueError("Expected one complete frozen snapshot bounds row.")
    return frozen_date_boundaries(glossary, *payload["rows"][0])
