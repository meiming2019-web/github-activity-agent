"""Replay legacy contexts offline using real read-only tools and preserved code."""

import argparse
import asyncio
import hashlib
import json
from pathlib import Path
from types import ModuleType, SimpleNamespace

from agent import context, mcp_server


ROOT = Path(__file__).resolve().parents[1]
BEFORE_SHA256 = "688b90977e398fc34ee1f2e4e89928977e6e6f2ac51bb747cd6c7524e20cbe63"


class OfflineSession:
    """In-process transport adapter; every result comes from an actual SQL tool."""

    async def call_tool(self, name, arguments):
        allowed = {"describe_table": mcp_server.describe_table,
                   "sample_values": mcp_server.sample_values,
                   "run_query": mcp_server.run_query}
        result = allowed[name](**arguments)
        return SimpleNamespace(is_error=False, structured_content=result.model_dump(), content=[])


async def replay(before_path, report_path):
    """Compare both real legacy entry points over all 86 unique historical IDs."""
    original = Path(before_path).read_bytes()
    assert hashlib.sha256(original).hexdigest() == BEFORE_SHA256
    current_path = ROOT / "agent/context.py"
    assert current_path.read_bytes().startswith(original), "Original code is not an exact prefix."
    old = ModuleType("context_before_c21")
    exec(compile(original, str(before_path), "exec"), old.__dict__)
    groups = []
    for path, expected in (("eval/github_test_questions_v2.jsonl", 60), ("eval/v3_questions.jsonl", 26)):
        rows = [json.loads(line) for line in (ROOT / path).read_text().splitlines() if line.strip()]
        assert len(rows) == expected
        assert all(isinstance(row["question"], str) and row["question"] for row in rows)
        groups.extend((path, row) for row in rows)
    assert len({row["id"] for _, row in groups}) == len(groups) == 86
    glossary = (ROOT / "eval/glossary.md").read_text()
    session = OfflineSession()
    old_shared = await old.shared_context(session)
    new_shared = await context.shared_context(session)
    topics = ("\n\nUse lookup_glossary for definitions. Available topics include new_stars, "
              "collaboration_events, active_contributors, time conventions, dataset scope, event types.")
    lines = ["# C2.1 Legacy-Entry Replay", "", "Both versions call their real legacy entry point on the same frozen glossary and live read-only database. The question is inventoried but is not an argument to that entry point. No Agent, runner, model client, or substitute context is used.", "",
             f"Original context.py SHA-256: `{BEFORE_SHA256}`.",
             f"Current context.py SHA-256: `{hashlib.sha256(current_path.read_bytes()).hexdigest()}`.", "",
             "The compared UTF-8 bytes include the real shared schema/sample context, unchanged lookup instructions, and legacy date-injection block, assembled in the order used by run_config. This is not a replay of model responses or scores.", "",
             "| Source | ID | Question SHA-256 | Old context SHA-256 | New context SHA-256 | Byte equality |",
             "| --- | --- | --- | --- | --- | --- |"]
    failures = []
    for source, row in groups:
        before = (old_shared + topics + "\n\n" + await old.c2_date_context(session, glossary)).encode()
        after = (new_shared + topics + "\n\n" + await context.c2_date_context(session, glossary)).encode()
        same = before == after
        if not same:
            failures.append(row["id"])
        lines.append(f"| {source} | {row['id']} | {hashlib.sha256(row['question'].encode()).hexdigest()} | {hashlib.sha256(before).hexdigest()} | {hashlib.sha256(after).hexdigest()} | {'PASS' if same else 'FAIL'} |")
        if not same:
            current_path.write_bytes(original)
            lines += ["", f"FAIL: {row['id']}; context.py immediately restored to original bytes. No further questions or downstream checks executed."]
            Path(report_path).write_text("\n".join(lines) + "\n")
            raise AssertionError(f"Legacy replay changed {row['id']}; context.py restored.")
    lines += ["", "Result: 86/86 byte-identical; 60 v2 + 26 v3, 86 unique IDs. This result validates only the old entry point. New-entry validation is separate."]
    Path(report_path).write_text("\n".join(lines) + "\n")
    return {"compared": 86, "identical": 86, "failures": failures}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=ROOT / "eval/v4_c21_replay.md")
    args = parser.parse_args()
    print(json.dumps(asyncio.run(replay(args.before, args.out))))
