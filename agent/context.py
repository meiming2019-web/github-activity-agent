"""Shared experiment/demo context and keyword glossary lookup."""

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

