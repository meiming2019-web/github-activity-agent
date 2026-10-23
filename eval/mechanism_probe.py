"""Declared config C mechanism probes; never part of the frozen main experiment."""

import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import sys
from time import perf_counter

from agent import loop
from agent.context import REFERENCE_DATE, lookup_glossary, shared_context
from eval.grader import grade_run


ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_PATH = ROOT / "eval/github_test_questions_v2.jsonl"
GLOSSARY_PATH = ROOT / "eval/glossary.md"
FROZEN_PATH = ROOT / "eval/results/runs.jsonl"
CORRECTED_PATH = ROOT / "eval/results/runs_v2.jsonl"
OUTPUT_PATH = ROOT / "eval/results/mechanism_probe.jsonl"
DECLARATION = "declared mechanism probe, separate from frozen results"
CONTROLS = frozenset({"t01", "t06", "t14", "u06", "u24"})


def select_questions(questions):
    ids = [q["id"] for q in questions]
    if len(ids) != len(set(ids)):
        raise ValueError("Question IDs must be unique.")
    glossary = [q for q in questions if q.get("needs_glossary") is True]
    counts = {prefix: sum(q["id"].startswith(prefix) for q in glossary) for prefix in ("t", "u")}
    controls = [q for q in questions if q["id"] in CONTROLS]
    if (len(glossary) != 21 or counts != {"t": 8, "u": 13} or len(controls) != 5
            or any(q.get("needs_glossary") is not False for q in controls)):
        raise ValueError(f"Probe selection mismatch: glossary={len(glossary)}, batches={counts}, controls={len(controls)}; expected 21 (8 t, 13 u) plus 5 false controls.")
    selected = [q for q in questions if q.get("needs_glossary") is True or q["id"] in CONTROLS]
    if len(selected) != 26:
        raise ValueError("Probe selection must contain exactly 26 distinct questions.")
    return selected


def select_remaining_controls(questions, records):
    original = {(q["id"], "C") for q in select_questions(questions)}
    universe = {(f"{prefix}{number:02}", "C") for prefix in ("t", "u") for number in range(1, 31)}
    keys = [(r["question_id"], r["config"]) for r in records]
    if (len(questions) != 60 or {(q["id"], "C") for q in questions} != universe
            or len(records) < 26 or set(keys[:26]) != original or len(keys) != len(set(keys))
            or not set(keys).issubset(universe)):
        raise ValueError("Control extension requires the original 26 unique terminal pairs and the exact 60-question universe.")
    pending = [q for q in questions if (q["id"], "C") not in set(keys)]
    if len(pending) > 34 or any(q.get("needs_glossary") is not False for q in pending):
        raise ValueError("Only the remaining 34 non-glossary pairs may extend the probe.")
    return questions


async def probe_question(question, client, session, shared, glossary, api_key):
    trace = loop.new_trace(question["question"], REFERENCE_DATE)
    lookups = []

    def observed_lookup(term):
        returned = lookup_glossary(glossary, term)
        lookups.append({"call_id": trace["tool_calls"][-1]["call_id"], "arguments": {"term": term},
                        "returned_text": returned,
                        "retrieval_hit": returned != "No glossary sections matched the requested term."})
        return returned

    system_context = shared + ("\n\nUse lookup_glossary for definitions. Available topics include new_stars, "
                               "collaboration_events, active_contributors, time conventions, dataset scope, event types.")
    started = perf_counter()
    trace = await loop.run_loop(client, session, trace, api_key, config="C", system_context=system_context,
                                lookup_glossary=observed_lookup)
    grade = grade_run(question, trace)
    return loop.sanitize({**trace, **grade, "question_id": question["id"], "config": "C",
                          "needs_glossary": question["needs_glossary"], "declaration": DECLARATION,
                          "tool_names": [entry["name"] for entry in trace["tool_calls"]],
                          "lookup_calls": lookups, "rounds": len(trace["api_responses"]),
                          "latency_ms": (perf_counter() - started) * 1000}, api_key)


async def run_probes(questions, client, session, glossary, output_path, source_hashes, api_key=""):
    output_path = Path(output_path)
    if output_path.resolve() in {FROZEN_PATH.resolve(), CORRECTED_PATH.resolve()}:
        raise ValueError("Probe output cannot target a frozen result file.")
    records = [json.loads(line) for line in output_path.read_text().splitlines() if line.strip()] if output_path.exists() else []
    allowed = {(q["id"], "C") for q in questions}
    seen = set()
    for record in records:
        key = (record["question_id"], record["config"])
        if (key not in allowed or key in seen or record.get("declaration") != DECLARATION
                or record.get("source_hashes") != source_hashes or "status" not in record):
            raise ValueError("Existing probe evidence has duplicate/unexpected pairs, different provenance, or invalid terminal records; refusing to overwrite it.")
        seen.add(key)
    pending = [q for q in questions if (q["id"], "C") not in seen]
    print(json.dumps({"declaration": DECLARATION, "recorded": len(records), "pending": len(pending)}), flush=True)
    shared = await shared_context(session) if pending else None
    for question in pending:
        print(f"Starting independent probe {question['id']}-C", flush=True)
        record = await probe_question(question, client, session, shared, glossary, api_key)
        record["source_hashes"] = source_hashes
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        records.append(record)
        print(json.dumps({key: record[key] for key in ("question_id", "status", "pass", "fail_category", "tool_names", "rounds", "prompt_tokens", "completion_tokens", "latency_ms")}), flush=True)
    return records


def summarize(records, corrected):
    glossary = [r for r in records if r["needs_glossary"]]
    controls = [r for r in records if not r["needs_glossary"]]
    called = lambda record: bool(record["lookup_calls"])
    retrieved = lambda record: any(call["retrieval_hit"] for call in record["lookup_calls"])
    fn = [r for r in glossary if not called(r)]
    matrix = {"TP": sum(called(r) for r in glossary), "FN": len(fn),
              "FN_pass": sum(r["pass"] for r in fn), "FN_fail": sum(not r["pass"] for r in fn),
              "FP": sum(called(r) for r in controls), "TN": sum(not called(r) for r in controls),
              "glossary_questions": len(glossary), "control_questions": len(controls),
              "glossary_successful_retrieval": sum(retrieved(r) for r in glossary),
              "control_successful_retrieval": sum(retrieved(r) for r in controls)}
    frozen = {}
    for record in corrected:
        frozen.setdefault((record["question_id"], record["config"]), record)
    comparisons = []
    for record in glossary:
        if record["question_id"].startswith("t"):
            old = frozen[(record["question_id"], "C")]
            comparisons.append({"question_id": record["question_id"], "frozen_v2_pass": old["pass"],
                                "probe_pass": record["pass"], "same": old["pass"] == record["pass"]})
    return {"declaration": DECLARATION, "matrix": matrix,
            "t_comparisons": comparisons, "t_consistent": sum(row["same"] for row in comparisons),
            "t_total": len(comparisons), "comparison_source": "eval/results/runs_v2.jsonl (frozen corrected v2)",
            "per_question": [{"question_id": r["question_id"], "needs_glossary": r["needs_glossary"],
                              "lookup_called": called(r), "retrieval_hit": retrieved(r), "pass": r["pass"],
                              "fail_category": r["fail_category"]} for r in records]}


async def main(remaining_controls=False):
    api_key = ""
    try:
        paths = {"questions": QUESTIONS_PATH, "glossary": GLOSSARY_PATH,
                 "frozen_runs": FROZEN_PATH, "corrected_v2": CORRECTED_PATH}
        raw = {name: path.read_bytes() for name, path in paths.items()}
        hashes = {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()}
        questions = [json.loads(line) for line in raw["questions"].splitlines() if line.strip()]
        selected = select_questions(questions)
        if remaining_controls:
            existing = [json.loads(line) for line in OUTPUT_PATH.read_text().splitlines() if line.strip()]
            selected = select_remaining_controls(questions, existing)
        frozen = [json.loads(line) for line in raw["frozen_runs"].splitlines() if line.strip()]
        corrected = [json.loads(line) for line in raw["corrected_v2"].splitlines() if line.strip()]
        universe = {(q["id"], config) for q in questions for config in ("A", "B", "C")}
        for label, records in (("frozen", frozen), ("corrected v2", corrected)):
            if len(records) != 180 or {(r["question_id"], r["config"]) for r in records} != universe:
                raise ValueError(f"The {label} file must contain exactly the 180 frozen pairs.")
        glossary = raw["glossary"].decode("utf-8")
        loop.load_dotenv(ROOT / ".env", override=False)
        api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY is missing or empty.")
        parameters = loop.StdioServerParameters(command=sys.executable, args=["-B", str(ROOT / "agent/mcp_server.py")],
                                                cwd=str(ROOT), env=loop.get_default_environment())
        async with loop.AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com", max_retries=0, timeout=60.0) as client:
            async with loop.stdio_client(parameters) as (reader, writer):
                async with loop.ClientSession(reader, writer, read_timeout_seconds=20) as session:
                    await session.initialize()
                    records = await run_probes(selected, client, session, glossary, OUTPUT_PATH, hashes, api_key)
        for name, path in paths.items():
            if path.read_bytes() != raw[name]:
                raise ValueError(f"Protected probe input changed during execution: {name}")
        print(json.dumps(summarize(records, corrected), ensure_ascii=False), flush=True)
        return 0
    except Exception as error:
        print(f"Mechanism probe stopped: {loop.sanitize(str(error), api_key)}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remaining-controls", action="store_true", help="Append only missing non-glossary controls to the original 26 probe records.")
    raise SystemExit(asyncio.run(main(parser.parse_args().remaining_controls)))
