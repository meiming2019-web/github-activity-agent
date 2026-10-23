"""Answer one question and append one complete, sanitized trace to JSONL."""

import argparse
import asyncio
import json
from pathlib import Path
import sys

from agent.loop import answer_question


TRACE_PATH = Path(__file__).resolve().parents[1] / "eval/traces.jsonl"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", help="Natural-language question about the GitHub activity snapshot")
    args = parser.parse_args(argv)
    if not args.question.strip():
        parser.error("question must not be empty")
    try:
        trace = asyncio.run(answer_question(args.question))
        TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with TRACE_PATH.open("a", encoding="utf-8") as output:
            output.write(json.dumps(trace, ensure_ascii=False, allow_nan=False) + "\n")
        print(trace["final_answer"])
        return 0 if trace["status"] == "completed" else 1
    except Exception:
        print("Agent execution or trace writing failed.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
