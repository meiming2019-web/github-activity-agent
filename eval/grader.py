"""Offline result-set grading against the read-only MCP query executor."""

from datetime import date, datetime, time
from itertools import permutations
import math

from agent import mcp_server


def same_value(left, right):
    if isinstance(left, (date, datetime, time)):
        left = left.isoformat()
    if isinstance(right, (date, datetime, time)):
        right = right.isoformat()
    if type(left) in (int, float) and type(right) in (int, float):
        if isinstance(left, float) or isinstance(right, float):
            return math.isclose(left, right, rel_tol=1e-6, abs_tol=0.0)
    return type(left) is type(right) and left == right


def same_multiset(expected, actual):
    """Use bipartite matching so tolerant duplicate rows cannot consume each other."""
    if len(expected) != len(actual):
        return False
    edges = [[index for index, row in enumerate(actual)
              if len(gold) == len(row) and all(same_value(a, b) for a, b in zip(gold, row))]
             for gold in expected]
    matched = {}

    def assign(index, seen):
        for target in edges[index]:
            if target in seen:
                continue
            seen.add(target)
            if target not in matched or assign(matched[target], seen):
                matched[target] = index
                return True
        return False

    return all(assign(index, set()) for index in range(len(expected)))


def grade_run(question, run):
    """Return a decision without accessing a model or rewriting any SQL."""
    def decision(category, diagnostic, matched_by=None):
        return {"pass": category is None, "fail_category": category, "diagnostic": diagnostic,
                "matched_by": matched_by if category is None else None}

    try:
        reference = mcp_server.execute_select(question["reference_sql"])
        if reference.truncated:
            return decision("configuration_error", "TRUNCATED_REFERENCE: reference exceeds the MCP result limit.")
        if not reference.rows:
            return decision("configuration_error", "EMPTY_REFERENCE: reference SQL returned zero rows.")
        expected = question["expected_columns"]
        reference_columns = [column.name for column in reference.columns]
        if not isinstance(expected, list) or not all(isinstance(name, str) for name in expected):
            return decision("configuration_error", "expected_columns must be a list of column names.")
        missing = [name for name in expected if name not in reference_columns]
        if missing:
            return decision("configuration_error", f"REFERENCE_COLUMNS_MISSING: {missing}")
    except Exception as error:
        return decision("configuration_error", f"REFERENCE_ERROR: {error}")

    if run.get("status") != "completed" or run.get("submitted") is not True:
        message = run.get("final_answer", "")
        if run.get("status") == "budget_exceeded" or "limit of 12 tool calls" in message or "Answer already submitted." in message:
            category = "budget_exceeded"
        elif run.get("status") == "sql_error_exhausted" or "3 consecutive SQL errors" in message:
            category = "sql_error_exhausted"
        else:
            category = "no_submission"
        return decision(category, f"Run status={run.get('status')}; submitted={run.get('submitted')}. {message}"[:500])
    if run.get("answer_truncated", run.get("truncated", False)):
        return decision("truncated_answer", "The submitted answer omitted rows.")
    columns = run.get("answer_columns", run.get("columns")) or []
    rows = run.get("answer_rows", run.get("rows"))
    if not isinstance(rows, list) or any(not isinstance(row, (list, tuple)) or len(row) != len(columns) for row in rows):
        return decision("wrong_result_set", "Answer rows do not match the reported columns.")
    if len(columns) < len(expected):
        return decision("missing_columns", f"Expected {len(expected)} columns; answer has {len(columns)}.")
    gold_indexes = [reference_columns.index(name) for name in expected]
    gold = [[row[index] for index in gold_indexes] for row in reference.rows]
    pinned = {}
    used = set()
    # Resolve case/duplicate collisions by first unused actual position, in expected order.
    for index, name in enumerate(expected):
        match = next((actual for actual, column in enumerate(columns)
                      if actual not in used and column.casefold() == name.casefold()), None)
        if match is not None:
            pinned[index] = match
            used.add(match)
    remaining = [index for index in range(len(expected)) if index not in pinned]
    unused = sorted(set(range(len(columns))) - used)
    candidates = permutations(unused, len(remaining)) if len(remaining) <= 4 else [tuple(unused[:len(remaining)])]
    tried = 0
    for candidate in candidates:
        indexes = dict(pinned)
        indexes.update(zip(remaining, candidate))
        answer = [[row[indexes[index]] for index in range(len(expected))] for row in rows]
        tried += 1
        if same_multiset(gold, answer):
            matched_by = "column_names" if not remaining else "name_plus_values" if pinned else "column_values"
            return decision(None, f"Pinned {len(pinned)}/{len(expected)} case-insensitive name matches; actual positions {[indexes[i] for i in range(len(expected))]} match the reference multiset.", matched_by)
    route = "injective value mappings" if len(remaining) <= 4 else "remaining-column positional pairing"
    return decision("wrong_result_set", f"Pinned {len(pinned)}/{len(expected)} case-insensitive name matches; {tried} {route} tried; unordered multisets differ: reference has {len(gold)} rows; answer has {len(rows)} rows.")
