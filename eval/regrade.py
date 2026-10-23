"""Disclosed offline re-scoring of frozen first-write-wins experiment records."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

from agent import mcp_server
from eval.grader import grade_run


ROOT = Path(__file__).resolve().parents[1]
HEADING = "## Grader v2 re-score (post-hoc, disclosed)"
DISCLOSURE = """Agent attempts frozen first-write-wins; no agent re-runs. Re-scoring applied two disclosed corrections:
(1) answer-key errata — expected identifier repo_id replaced by repo name (1:1 isomorphic in catalog; questions ask "which repositories", never IDs);
(2) grader v2 column matching — partial name match + injective value matching, fixing v1's all-or-nothing positional fallback.
v1 results above remain the primary frozen record."""
T07_CLAIM = "t07 verified as genuine agent failure — EXTRACT(ISODOW) is available via the MCP whitelist (verified post-run); agents exhausted their SQL error budget on non-whitelisted dialect functions instead of using EXTRACT."


def t07_evidence(records):
    probe = mcp_server.run_query("SELECT EXTRACT(ISODOW FROM TIMESTAMP '2026-10-19') AS monday, EXTRACT(ISODOW FROM TIMESTAMP '2026-10-25') AS sunday")
    if "EXTRACT" not in mcp_server.SAFE_FUNCTIONS or probe.rows != [[1, 7]]:
        return "t07 evidence discrepancy: EXTRACT(ISODOW) whitelist/execution probe did not confirm Monday=1 and Sunday=7."
    found = {record["config"]: record for record in records if record["question_id"] == "t07"}
    supported = all(config in found and found[config].get("fail_category") == "sql_error_exhausted"
                    and "Function is not allowed:" in found[config].get("diagnostic", "") for config in ("B", "C"))
    if supported:
        return T07_CLAIM
    details = "; ".join(f"{config}: {record.get('diagnostic', '')}" for config, record in sorted(found.items()))
    return ("t07 evidence discrepancy: EXTRACT(ISODOW) is whitelisted and returned Monday=1, Sunday=7. "
            "Frozen records confirm the recorded failures below, but do not retain B/C's rejected SQL/functions; "
            "their exact dialect-function failure cause cannot be verified without inventing evidence. " + details)


def regrade(questions_path=ROOT / "eval/github_test_questions.jsonl", runs_path=ROOT / "eval/results/runs.jsonl",
            output_path=ROOT / "eval/results/runs_v2.jsonl", summary_path=ROOT / "eval/results/summary.md"):
    questions_raw = Path(questions_path).read_bytes()
    runs_raw = Path(runs_path).read_bytes()
    summary_raw = Path(summary_path).read_bytes()
    questions = {q["id"]: q for q in (json.loads(line) for line in questions_raw.splitlines() if line.strip())}
    first = {}
    for number, line in enumerate(runs_raw.splitlines(), 1):
        if not line.strip():
            continue
        record = json.loads(line)
        required = {"question_id", "config", "status", "submitted", "answer_sql", "answer_columns", "answer_rows", "answer_truncated", "pass", "fail_category"}
        missing = sorted(required - record.keys())
        if missing:
            raise ValueError(f"Stored answer data missing at source line {number}: {missing}")
        if record["status"] == "completed" and record["submitted"]:
            if (not isinstance(record["answer_columns"], list) or not isinstance(record["answer_rows"], list)
                    or not isinstance(record["answer_truncated"], bool) or not isinstance(record["answer_sql"], str)):
                raise ValueError(f"Stored submitted answer data invalid at source line {number}; no reconstruction is allowed.")
        first.setdefault((record["question_id"], record["config"]), (number, record))
    universe = {(qid, config) for qid in questions for config in ("A", "B", "C")}
    if set(first) != universe:
        raise ValueError(f"Frozen question/config universe mismatch: missing={sorted(universe - first.keys())}; unexpected={sorted(first.keys() - universe)}")
    source_hash = hashlib.sha256(runs_raw).hexdigest()
    key_hash = hashlib.sha256(questions_raw).hexdigest()
    outputs = []
    changes = []
    for (qid, config), (number, record) in first.items():
        grading_input = dict(record)
        grading_input.setdefault("final_answer", record.get("diagnostic", ""))
        grade = grade_run(questions[qid], grading_input)
        outputs.append({**record, "v1_pass": record["pass"], "v1_fail_category": record["fail_category"],
                        "v1_matched_by": record.get("matched_by"), "v1_diagnostic": record.get("diagnostic"),
                        **grade, "grader_version": 2, "source_record_line": number,
                        "source_runs_sha256": source_hash, "answer_key_sha256": key_hash})
        if record["pass"] != grade["pass"] or record["fail_category"] != grade["fail_category"]:
            changes.append({"question_id": qid, "config": config, "old_pass": record["pass"],
                            "old_fail_category": record["fail_category"], "new_pass": grade["pass"],
                            "new_fail_category": grade["fail_category"], "matched_by": grade["matched_by"]})
    lines = [HEADING, "", DISCLOSURE, "", "| Config | v1 | v2 | Delta |", "|---|---:|---:|---:|"]
    scores = {}
    for config in ("A", "B", "C"):
        old = sum(record["pass"] for _, record in first.values() if record["config"] == config)
        new = sum(record["pass"] for record in outputs if record["config"] == config)
        scores[config] = {"v1": old, "v2": new, "delta": new - old, "questions": len(questions)}
        lines.append(f"| {config} | {old}/{len(questions)} | {new}/{len(questions)} | {new - old:+d} |")
    lines += ["", "Changed verdicts (including changes between failure categories):", "",
              "| Question | Config | Old result/category | New result | matched_by |", "|---|---|---|---|---|"]
    for change in changes:
        old = "PASS" if change["old_pass"] else str(change["old_fail_category"])
        new = "PASS" if change["new_pass"] else f"FAIL ({change['new_fail_category']})"
        lines.append(f"| {change['question_id']} | {change['config']} | {old} | {new} | {change['matched_by'] or 'null'} |")
    if not changes:
        lines.append("| — | — | — | No verdict changes | — |")
    evidence = t07_evidence([record for _, record in first.values()])
    lines += ["", evidence]
    section = ("\n" + "\n".join(lines) + "\n").encode("utf-8")
    marker = ("\n" + HEADING + "\n").encode("utf-8")
    marker_index = summary_raw.find(marker)
    if marker_index >= 0 and summary_raw[marker_index:] != section:
        raise ValueError("An existing Grader v2 disclosure differs; refusing to rewrite frozen summary content.")
    output = b"".join((json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8") for record in outputs)
    destination = Path(output_path)
    if destination.exists() and destination.read_bytes() != output:
        raise ValueError("Existing v2 results differ; refusing to overwrite prior re-scoring.")
    if Path(runs_path).read_bytes() != runs_raw:
        raise ValueError("Frozen runs changed during offline re-scoring; outputs were not written.")
    if not destination.exists():
        destination.write_bytes(output)
    if marker_index < 0:
        with Path(summary_path).open("ab") as summary:
            summary.write(section)
    return {"records": len(outputs), "scores": scores, "changed_verdicts": changes,
            "runs_sha256": source_hash, "runs_v2_sha256": hashlib.sha256(output).hexdigest(),
            "original_summary_prefix_bytes": marker_index if marker_index >= 0 else len(summary_raw),
            "t07_evidence": evidence}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, default=ROOT / "eval/github_test_questions.jsonl", help="Question JSONL file")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(regrade(questions_path=args.questions), ensure_ascii=False, allow_nan=False))
        return 0
    except Exception as error:
        print(f"Offline re-scoring blocked: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
