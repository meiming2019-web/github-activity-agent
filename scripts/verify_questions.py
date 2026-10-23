"""Verify reference SQL against the local read-only GitHub activity database."""

import argparse
import json
from pathlib import Path
import sys
import threading

import duckdb
import sqlglot
from sqlglot import exp
from sqlglot.optimizer.scope import Scope, traverse_scope


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data/github.duckdb"
DEFAULT_QUESTIONS = PROJECT_ROOT / "eval/github_dev_questions.jsonl"
QUERY_TIMEOUT_SECONDS = 10.0
T12_PRECHECK_SQL = """
    SELECT COUNT(*) AS qualifying_repo_count FROM (
        SELECT repo_id FROM events
        WHERE type = 'PullRequestEvent'
          AND created_at >= TIMESTAMP '2026-10-15 00:00:00'
          AND created_at < TIMESTAMP '2026-10-22 00:00:00'
        GROUP BY repo_id HAVING COUNT(*) > 50
    ) AS qualifying_repositories
"""


def execute_query(connection, sql):
    # Keep reference SQL verbatim; do not apply the MCP tool's row cap or rewrite it.
    statements = sqlglot.parse(sql, read="duckdb", error_level=sqlglot.ErrorLevel.RAISE)
    if len(statements) != 1 or not isinstance(statements[0], (exp.Select, exp.Union, exp.Intersect, exp.Except)):
        raise ValueError("Only a single SELECT query is allowed.")
    tree = statements[0]
    if any(isinstance(node, (exp.DDL, exp.DML, exp.Into)) for node in tree.walk()):
        raise ValueError("Statements with side effects are not allowed.")
    for scope in traverse_scope(tree):
        for relation in scope.sources.values():
            if isinstance(relation, exp.Table):
                if relation.catalog or relation.db not in ("", "main"):
                    raise ValueError("External catalogs and schemas are not allowed.")
                if isinstance(relation.this, exp.GenerateSeries):
                    continue
                if not isinstance(relation.this, exp.Identifier) or relation.name.lower() not in {"events", "repos", "ingest_log"}:
                    raise ValueError(f"Relation is not allowed: {relation.sql(dialect='duckdb')}")
            elif not isinstance(relation, Scope):
                raise ValueError("Only known tables and SELECT subqueries are allowed.")
    finished = threading.Event()
    expired = threading.Event()

    def interrupt_after_deadline():
        if not finished.wait(QUERY_TIMEOUT_SECONDS):
            expired.set()
            while not finished.is_set():
                connection.interrupt()
                finished.wait(0.01)

    watchdog = threading.Thread(target=interrupt_after_deadline, daemon=True)
    watchdog.start()
    try:
        cursor = connection.execute(sql)
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
    except duckdb.Error as error:
        if expired.is_set():
            raise TimeoutError(f"Query timed out after {QUERY_TIMEOUT_SECONDS:g} seconds: {error}") from error
        raise
    finally:
        finished.set()
        watchdog.join()
    if expired.is_set():
        raise TimeoutError(f"Query timed out after {QUERY_TIMEOUT_SECONDS:g} seconds.")
    return columns, rows


def run_prechecks(connection, t06_question):
    t06_result = None
    t12_count = None
    failed = False
    checks = (("t06", t06_question.get("reference_sql") if t06_question else None),
              ("t12", T12_PRECHECK_SQL))
    for name, sql in checks:
        print(f"PRECHECK {name}")
        if sql is None:
            print("PRECHECK_UNAVAILABLE: no t06 reference SQL in the selected question file.")
            continue
        print(sql)
        try:
            columns, rows = execute_query(connection, sql)
            print(json.dumps({"columns": columns, "rows": rows, "row_count": len(rows)},
                             ensure_ascii=False, default=str))
            if name == "t06":
                t06_result = (columns, rows)
                if len(rows) != 3:
                    failed = True
                    print(f"T06_ROW_COUNT: expected exactly 3 rows; got {len(rows)}.")
            else:
                t12_count = rows[0][0]
                if t12_count == 0:
                    failed = True
                    print("t12 will fail: no repository has more than 50 PullRequestEvent records in [2026-10-15, 2026-10-22) UTC.")
        except Exception as error:
            failed = True
            if name == "t06":
                t06_result = error
            print(f"PRECHECK_ERROR {type(error).__name__}: {error}")
    return t06_result, t12_count, failed


def verify_question(connection, question, t12_count, prechecked=None):
    result = {"id": question.get("id", "UNKNOWN"), "status": "FAIL", "row_count": None, "reason": ""}
    reasons = []
    try:
        expected = question["expected_columns"]
        if not isinstance(expected, list) or not all(isinstance(column, str) for column in expected):
            raise ValueError("expected_columns must be a list of column names.")
        if isinstance(prechecked, Exception):
            raise prechecked
        columns, rows = prechecked if prechecked is not None else execute_query(connection, question["reference_sql"])
        result["row_count"] = len(rows)
        if not rows:
            reasons.append("EMPTY_RESULT")
        missing = [column for column in expected if column not in columns]
        if missing:
            reasons.append("MISSING_COLUMNS: " + json.dumps(
                {"missing": missing, "expected": expected, "actual": columns}, ensure_ascii=False))
    except duckdb.Error as error:
        reasons.append(f"DUCKDB_ERROR: {error}")
    except TimeoutError as error:
        reasons.append(f"TIMEOUT: {error}")
    except (sqlglot.errors.SqlglotError, ValueError) as error:
        reasons.append(f"VALIDATION_ERROR: {error}")
    except Exception as error:
        reasons.append(f"{type(error).__name__}: {error}")
    if result["id"] == "t06" and result["row_count"] is not None and result["row_count"] != 3:
        reasons.append(f"T06_ROW_COUNT: expected exactly 3 rows; got {result['row_count']}.")
    if result["id"] == "t12":
        if t12_count == 0:
            reasons.append("T12_PRECHECK_ZERO: no qualifying repository in [2026-10-15, 2026-10-22) UTC")
        elif t12_count is None:
            reasons.append("T12_PRECHECK_UNAVAILABLE")
    result["reason"] = "; ".join(reasons)
    if not reasons:
        result["status"] = "PASS"
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("questions", nargs="?", type=Path, default=DEFAULT_QUESTIONS,
                        help="Question JSONL file; defaults to the project development set")
    args = parser.parse_args(argv)
    total = passed = 0
    try:
        with duckdb.connect(str(DATABASE_PATH), read_only=True,
                            config={"memory_limit": "2GB", "threads": 2, "enable_external_access": False,
                                    "autoinstall_known_extensions": False, "autoload_known_extensions": False}) as connection:
            try:
                with args.questions.open(encoding="utf-8") as questions:
                    lines = list(enumerate(questions, 1))
            except OSError as error:
                print(f"Validation not run: question file unavailable: {args.questions}: {error}", file=sys.stderr)
                return 1
            t06_question = None
            for _, line in lines:
                try:
                    question = json.loads(line)
                    if isinstance(question, dict) and question.get("id") == "t06":
                        t06_question = question
                        break
                except ValueError:
                    pass
            t06_result, t12_count, precheck_failed = run_prechecks(connection, t06_question)
            for line_number, line in lines:
                if not line.strip():
                    continue
                total += 1
                try:
                    question = json.loads(line)
                    if not isinstance(question, dict):
                        raise ValueError("Each question must be a JSON object.")
                    prechecked = t06_result if question == t06_question else None
                    result = verify_question(connection, question, t12_count, prechecked)
                except (ValueError, TypeError) as error:
                    result = {"id": f"line-{line_number}", "status": "FAIL", "row_count": None,
                              "reason": f"QUESTION_ERROR: {error}"}
                print(json.dumps(result, ensure_ascii=False))
                passed += result["status"] == "PASS"
            print(f"Summary: {passed}/{total} passed; {total - passed} failed.")
            if not total:
                print("Validation failed: the question file contains no questions.", file=sys.stderr)
            return 1 if passed != total or precheck_failed or not total else 0
    except Exception as error:
        print(f"Validation failed: {type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
