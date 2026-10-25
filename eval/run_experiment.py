"""Run interleaved A/B/C evaluations; use --question-id t01 for a single-question smoke."""

import argparse
import asyncio
import json
import os
from pathlib import Path
import sys
from time import perf_counter

from agent import loop
from agent.context import REFERENCE_DATE, lookup_glossary, shared_context, tool_payload, c2_date_context
from eval.grader import grade_run


PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_PATH = PROJECT_ROOT / "eval/github_test_questions.jsonl"
GLOSSARY_PATH = PROJECT_ROOT / "eval/glossary.md"
RESULTS_DIR = PROJECT_ROOT / "eval/results"
DEVELOPMENT_QUESTIONS_PATH = PROJECT_ROOT / "eval/github_dev_questions.jsonl"


async def run_config(config, client, session, question, shared, glossary, api_key):
    if config in ("A", "B"):
        context = shared + "\n\nFULL GLOSSARY\n" + glossary
    else:
        context = shared + ("\n\nUse lookup_glossary for definitions. Available topics include new_stars, "
                            "collaboration_events, active_contributors, time conventions, dataset scope, event types.")
    if config == "C2":
        context += "\n\n" + await c2_date_context(session, glossary)
    trace = await loop.run_loop(
        client, session, loop.new_trace(question, REFERENCE_DATE), api_key, config="C" if config == "C2" else config, system_context=context,
        lookup_glossary=(lambda term: lookup_glossary(glossary, term)) if config in ("C", "C2") else None,
    )
    if config == "C2":
        trace["config"] = "C2"
    return trace


def write_summary(questions, configs, history, path):
    universe = {(question["id"], config) for question in questions for config in configs}
    first = {}
    for record in history:
        key = (record["question_id"], record["config"])
        if key in universe and key not in first:
            first[key] = record
    lines = ["# Experiment summary", "",
             "Each (question, config) pair was attempted exactly once; recorded outcomes are final.", "",
             f"Reference date: {REFERENCE_DATE} (UTC).", "",
             "| Config | Passed / questions | Prompt tokens | Completion tokens | Total tokens |",
             "|---|---:|---:|---:|---:|"]
    for config in configs:
        records = [row for row in history if (row["question_id"], row["config"]) in universe and row["config"] == config]
        passed = sum(bool(first.get((question["id"], config), {}).get("pass")) for question in questions)
        prompt = sum(row["prompt_tokens"] for row in records)
        completion = sum(row["completion_tokens"] for row in records)
        lines.append(f"| {config} | {passed}/{len(questions)} | {prompt} | {completion} | {prompt + completion} |")
    lines += ["", "Tokens include all recorded attempts; each question/config counts once in the pass matrix.", "",
              "| Question | " + " | ".join(configs) + " |", "|---|" + "---|" * len(configs)]
    for question in questions:
        cells = []
        for config in configs:
            record = first.get((question["id"], config))
            cells.append("NOT RUN" if record is None else "PASS" if record["pass"] else f"FAIL ({record['fail_category']})")
        lines.append(f"| {question['id']} | " + " | ".join(cells) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def pending_pairs(questions, configs, history, question_id=None):
    completed = {(row["question_id"], row["config"]) for row in history}
    return [(question, config) for question in questions if question_id is None or question["id"] == question_id
            for config in configs if (question["id"], config) not in completed]


async def run_experiments(questions, configs, client, session, glossary, results_dir, api_key="", question_id=None):
    # Phase 1 never scores C2; future approved collection needs runs_v3.jsonl, not frozen histories/summary.
    if "C2" in configs:
        raise ValueError("C2 formal experiments are disabled in Phase 1; future results require a separate runs_v3.jsonl and no main summary writes.")
    results_dir = Path(results_dir)
    runs_path = results_dir / "runs.jsonl"
    history = [json.loads(line) for line in runs_path.read_text(encoding="utf-8").splitlines() if line.strip()] if runs_path.exists() else []
    pending = pending_pairs(questions, configs, history, question_id)
    shared = await shared_context(session) if pending else None
    new_records = []
    for question, config in pending:
        started = perf_counter()
        trace = await run_config(config, client, session, question["question"], shared, glossary, api_key)
        grade = grade_run(question, trace)
        record = loop.sanitize({
            "question_id": question["id"], "config": config, "status": trace["status"],
            **grade, "prompt_tokens": trace["prompt_tokens"], "completion_tokens": trace["completion_tokens"],
            "tool_call_count": trace["tool_call_count"], "tool_names": [entry["name"] for entry in trace["tool_calls"]],
            "latency_ms": (perf_counter() - started) * 1000,
            "answer_sql": trace["answer_sql"], "answer_columns": trace["answer_columns"],
            "answer_rows": trace["answer_rows"], "answer_truncated": trace["answer_truncated"],
            "submitted": trace["submitted"],
        }, api_key)
        results_dir.mkdir(parents=True, exist_ok=True)
        with runs_path.open("a", encoding="utf-8") as output:
            output.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
        print(json.dumps(record, ensure_ascii=False, allow_nan=False))
        history.append(record)
        new_records.append(record)
    results_dir.mkdir(parents=True, exist_ok=True)
    write_summary(questions, configs, history, results_dir / "summary.md")
    return new_records


async def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", choices=("A", "B", "C", "C2", "all"), required=True)
    parser.add_argument("--question-id", help="Run only this question ID, retaining the full-set summary denominator")
    parser.add_argument("--questions", type=Path, default=QUESTIONS_PATH, help="Question JSONL file")
    parser.add_argument("--dry-run", action="store_true", help="List pending question/config pairs without starting services or writing results")
    args = parser.parse_args(argv)
    api_key = ""
    try:
        questions = [json.loads(line) for line in args.questions.read_text(encoding="utf-8").splitlines() if line.strip()]
        if args.question_id is not None and args.question_id not in {question["id"] for question in questions}:
            raise ValueError("The selected question ID does not exist.")
        if args.config == "C2" and (args.questions.resolve() != DEVELOPMENT_QUESTIONS_PATH.resolve()
                or args.question_id not in {f"d{index:02}" for index in range(1, 16)}):
            raise ValueError("Phase 1 C2 permits only one selected d01-d15 question from the existing development file; no formal experiment or unfrozen questions.")
        configs = ("A", "B", "C") if args.config == "all" else (args.config,)
        if args.dry_run:
            runs_path = RESULTS_DIR / "runs.jsonl"
            history = [json.loads(line) for line in runs_path.read_text(encoding="utf-8").splitlines() if line.strip()] if runs_path.exists() else []
            pending = pending_pairs(questions, configs, history, args.question_id)
            selected = sum(args.question_id is None or question["id"] == args.question_id for question in questions) * len(configs)
            print(json.dumps({"questions": len(questions), "skipped": selected - len(pending), "pending": len(pending)}))
            for question, config in pending:
                print(f"{question['id']}-{config}")
            return 0
        glossary = GLOSSARY_PATH.read_text(encoding="utf-8")
        loop.load_dotenv(PROJECT_ROOT / ".env", override=False)
        api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY is missing or empty.")
        parameters = loop.StdioServerParameters(
            command=sys.executable, args=["-B", str(PROJECT_ROOT / "agent/mcp_server.py")],
            cwd=str(PROJECT_ROOT), env=loop.get_default_environment(),
        )
        async with loop.AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com", max_retries=0, timeout=60.0) as client:
            async with loop.stdio_client(parameters) as (reader, writer):
                async with loop.ClientSession(reader, writer, read_timeout_seconds=20) as session:
                    await session.initialize()
                    if args.config == "C2":
                        question = next(q for q in questions if q["id"] == args.question_id)
                        shared = await shared_context(session)
                        trace = await run_config("C2", client, session, question["question"], shared, glossary, api_key)
                        print(json.dumps(loop.sanitize(trace, api_key), ensure_ascii=False, allow_nan=False))
                        return 0 if trace["status"] == "completed" else 1
                    records = await run_experiments(questions, configs, client, session, glossary,
                                                    RESULTS_DIR, api_key, args.question_id)
        return 0 if all(record["status"] == "completed" for record in records) else 1
    except Exception as error:
        print(f"Experiment failed: {loop.sanitize(str(error), api_key)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
