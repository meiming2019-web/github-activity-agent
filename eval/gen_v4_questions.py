"""Generate the fixed-seed v4 offline evaluation set; never start an Agent."""

import argparse
import asyncio
from collections import Counter
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
import random
import re
import sys

# Support the explicitly requested direct script invocation as well as -m.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.context import c2_date_context_for_question
from agent.mcp_server import DATABASE_PATH, execute_select
from eval.check_bounds_consistency import check_bounds_consistency
from eval.check_c21_replay import OfflineSession
from eval.check_v4_dedup import check_dedup, normalized_text
from eval.grader import same_multiset
from eval.row_normalize import normalize_rows
from eval.v4_bounds import WINDOW_EXPRESSIONS, window_bounds


ROOT = Path(__file__).resolve().parents[1]
PARAPHRASES = ("literal", "colloquial", "distractor")
WINDOW_FAMILIES = ("window_new_stars", "window_collaboration_events", "window_active_contributors")
TARGETED_ADVANCED = ("daily_trend", "running_total", "day_over_day", "day_of_week")
ADJACENT = ("session_segmentation", "consecutive_day_runs")
CONTROLS = ("catalog_lookup", "language_composition")
EVENT_TYPES = ("WatchEvent", "PushEvent", "IssuesEvent", "PullRequestEvent", "IssueCommentEvent")
ADVANCED_WINDOWS = tuple(WINDOW_EXPRESSIONS[index] for index in (0, 2, 4, 7, 8))


class CandidateRejected(AssertionError):
    """Objective assertion failures drive the explicitly adjudicated fallback ladder."""


def sql_literal(value):
    """Quote a selected database string without introducing SQL syntax."""
    return "'" + value.replace("'", "''") + "'"


def reference_sql(family, params, start=None, end=None):
    """Build one concrete reference SELECT from fixed family and entity parameters."""
    entity = sql_literal(params["entity"])
    if family == "catalog_lookup":
        return f"SELECT name AS repo_name, stars, forks, open_issues FROM repos WHERE name = {entity}", ["stars", "forks", "open_issues"]
    if family == "language_composition":
        return f"SELECT COUNT(*) AS repo_count, SUM(stars) AS total_stars FROM repos WHERE language = {entity}", ["repo_count", "total_stars"]
    bounds = f"e.created_at >= TIMESTAMP '{start.isoformat()}' AND e.created_at < TIMESTAMP '{end.isoformat()}'"
    if family in WINDOW_FAMILIES:
        scope = f"e.repo_name = {entity}" if params["scope"] == "repo" else f"r.language = {entity}"
        source = f"FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE {bounds} AND {scope}"
        if family == "window_active_contributors":
            qualified = ("SELECT e.repo_name, e.actor " + source + " AND e.actor IS NOT NULL "
                         "AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN "
                         "('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') "
                         "GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3")
            if params["scope"] == "repo":
                return f"WITH qualified AS ({qualified}) SELECT COUNT(*) AS value FROM qualified", ["value"]
            aggregate = f"WITH qualified AS ({qualified}) SELECT repo_name, COUNT(*) AS value FROM qualified GROUP BY repo_name"
        else:
            metric = ("COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END)"
                      if family == "window_new_stars" else
                      "COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent'))")
            if params["scope"] == "repo":
                return f"SELECT {metric} AS value {source}", ["value"]
            aggregate = f"SELECT e.repo_name, {metric} AS value {source} GROUP BY e.repo_name"
        return (f"WITH metric AS ({aggregate}) SELECT repo_name, value FROM metric WHERE value > 0 "
                "ORDER BY value DESC, repo_name ASC LIMIT 5"), ["value"]
    event = sql_literal(params["event_type"])
    filtered = f"FROM events e WHERE {bounds} AND e.repo_name = {entity} AND e.type = {event}"
    if family == "session_segmentation":
        return ("WITH ordered AS (SELECT e.created_at, LAG(e.created_at) OVER "
                "(ORDER BY e.created_at, e.event_id) AS previous_at " + filtered + ") "
                "SELECT SUM(CASE WHEN previous_at IS NULL OR created_at - previous_at > INTERVAL '30 minutes' "
                "THEN 1 ELSE 0 END) AS session_count FROM ordered"), ["session_count"]
    if family == "consecutive_day_runs":
        return ("WITH active_days AS (SELECT DISTINCT CAST(e.created_at AS DATE) AS day " + filtered + "), "
                "numbered AS (SELECT day, day - CAST(ROW_NUMBER() OVER (ORDER BY day) AS INTEGER) AS island FROM active_days) "
                "SELECT MIN(day) AS first_date, MAX(day) AS last_date, COUNT(*) AS active_days "
                "FROM numbered GROUP BY island ORDER BY first_date ASC"), ["active_days"]
    last_date = end - timedelta(days=1)
    daily = (f"WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '{start.isoformat()}', "
             f"TIMESTAMP '{last_date.isoformat()}', INTERVAL '1 day') AS t(day)), "
             "counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count " + filtered + " GROUP BY 1), "
             "daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) ")
    if family == "daily_trend":
        return daily + "SELECT day, event_count FROM daily ORDER BY day ASC", ["event_count"]
    if family == "running_total":
        return daily + ("SELECT day, event_count, SUM(event_count) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING "
                        "AND CURRENT ROW) AS running_count FROM daily ORDER BY day ASC"), ["event_count"]
    if family == "day_over_day":
        return daily + (", compared AS (SELECT day, event_count, LAG(event_count) OVER (ORDER BY day) AS previous_count FROM daily) "
                        "SELECT day, event_count, previous_count, event_count - previous_count AS change FROM compared ORDER BY day ASC"), ["event_count"]
    if family == "day_of_week":
        return daily + "SELECT EXTRACT(DOW FROM day) AS weekday, SUM(event_count) AS event_count FROM daily GROUP BY 1 ORDER BY weekday ASC", ["event_count"]
    raise ValueError(f"Unknown template family: {family}")


def question_text(family, params, expression, layer):
    """Vary non-time wording while keeping every effective window verbatim."""
    entity = params["entity"]
    if family in WINDOW_FAMILIES:
        metric = family.removeprefix("window_")
        meaning = {"new_stars": "distinct non-null WatchEvent actors, including bots",
                   "collaboration_events": "IssuesEvent, PullRequestEvent, and IssueCommentEvent records",
                   "active_contributors": "non-null actors with at least three PushEvent, IssuesEvent, PullRequestEvent, or IssueCommentEvent records, excluding case-insensitive [bot] suffixes"}[metric]
        if params["scope"] == "repo":
            core = (f"For {expression}, report {metric} for repository '{entity}' as value."
                    if layer != "colloquial" else f"For {expression}, how much {metric} did '{entity}' register? Give one value.")
        else:
            core = (f"For {expression}, rank up to five '{entity}' repositories with positive {metric}; return repo_name and value."
                    if layer != "colloquial" else f"For {expression}, which up to five '{entity}' projects led on positive {metric}? Give repo_name and value.")
            core += " Order by value descending; break ties by repo_name ascending."
        core += f" Count {meaning}; apply the definition separately per repository within the window."
    elif family in TARGETED_ADVANCED + ADJACENT:
        requests = {
            "daily_trend": "return each UTC date as day and its event_count, including zero-count dates, ordered by day ascending",
            "running_total": "return each UTC date as day, event_count, and running_count accumulated from the window start, including zero-count dates, ordered by day ascending",
            "day_over_day": "return each UTC date as day, event_count, previous_count, and change (current minus previous); include zero-count dates and use NULL for previous_count and change on the first date; order by day ascending",
            "day_of_week": "sum daily counts by weekday (Sunday=0 and Saturday=6) for dates present in the window; return weekday and event_count, including zero-count groups, ordered by weekday ascending",
            "session_segmentation": "return session_count after ordering these records by created_at and event_id ascending; the first record starts a session, and a gap strictly greater than 30 minutes starts another session",
            "consecutive_day_runs": "return every maximal run of consecutive active UTC dates as first_date, last_date, and active_days; a date is active if it contains at least one matching record; order by first_date ascending",
        }
        prefix = "For" if layer != "colloquial" else "Help me review"
        core = f"{prefix} {expression}, using {params['event_type']} records for '{entity}', {requests[family]}."
    elif family == "catalog_lookup":
        core = (f"Read the catalog entry for '{entity}': return repo_name, stars, forks, and open_issues."
                if layer != "colloquial" else f"Give me the catalog numbers for '{entity}': repo_name, stars, forks, and open_issues.")
    else:
        core = (f"For catalog language '{entity}', return repo_count and total_stars summed across its repositories."
                if layer != "colloquial" else f"How large is the '{entity}' catalog group? Give repo_count and its combined total_stars.")
    if layer == "distractor":
        core += " A repository creation year of 2017 is background only and must not filter the answer."
    return core


def run_reference(sql):
    """Execute through the frozen read-only SQL allowlist and normalize JSON rows."""
    result = execute_select(sql)
    assert not result.truncated, "Reference exceeds the existing result cap; stop without regeneration."
    return [column.name for column in result.columns], normalize_rows(result.rows)


def assert_reference(sql, columns, rows, metric_columns, question):
    """Apply only item-8 nonempty/nonzero and deterministic Top-N assertions."""
    if not rows:
        raise CandidateRejected("empty_reference")
    indexes = [columns.index(column) for column in metric_columns]
    if not any(type(row[index]) in (int, float) and row[index] != 0 for row in rows for index in indexes):
        raise CandidateRejected("all_zero_aggregate")
    if "LIMIT 5" in sql and ("ORDER BY value DESC, repo_name ASC" not in sql or
                             "break ties by repo_name ascending" not in question):
        raise CandidateRejected("missing_top_n_tie_rule")


# Out-of-coverage extension by one day is answer-neutral for non-calendar
# aggregates because the extra day has no data. For generate_series calendar
# questions it can add a zero-count row, so that neutrality does not apply.
# Exclude out-of-coverage perturbations uniformly; analysis-stage SQL endpoint
# parsing, not row-set grading, will detect these boundary mistakes.
OUTSIDE_COVERAGE_NOTE = (
    "Extending one day beyond coverage is answer-neutral for non-calendar aggregates because the extra day has no data. "
    "For questions using generate_series date scaffolds, the extra day may add a zero-count row and change the row set; "
    "the neutrality conclusion does not apply. Out-of-coverage perturbations are nevertheless excluded uniformly. "
    "Detecting these endpoint mistakes is deferred to future analysis-stage SQL window-endpoint parsing, which is not implemented in this phase; row-set grading cannot provide that guarantee."
)


def sensitivity_cases(start, end, snapshot_start, snapshot_end):
    """Enumerate the six authorized endpoint perturbations and explicit exclusions."""
    assert snapshot_start <= start < end <= snapshot_end
    specs = (("start_plus_one", 1, 0), ("end_minus_one", 0, -1),
             ("end_plus_one", 0, 1), ("start_minus_one", -1, 0),
             ("both_plus_one", 1, 1), ("both_minus_one", -1, -1))
    cases = []
    for name, start_shift, end_shift in specs:
        altered_start = start + timedelta(days=start_shift)
        altered_end = end + timedelta(days=end_shift)
        eligible = snapshot_start <= altered_start <= altered_end <= snapshot_end
        cases.append({"perturbation": name, "start_shift_days": start_shift, "end_shift_days": end_shift,
                      "bounds": [altered_start.isoformat(), altered_end.isoformat()],
                      "eligible": eligible, "exclusion_reason": None if eligible else "outside_snapshot_coverage"})
    return cases


def write_round2_review(previous_path, current_path, original_review_path, out):
    """Preserve all old review identities, mark replacements, and fill window strata."""
    previous_bytes = Path(previous_path).read_bytes()
    current_bytes = Path(current_path).read_bytes()
    previous = {row["id"]: row for row in map(json.loads, previous_bytes.decode().splitlines())
                if row.get("record_type") == "question"}
    current = {row["id"]: row for row in map(json.loads, current_bytes.decode().splitlines())
               if row.get("record_type") == "question"}
    assert previous.keys() == current.keys()
    old_review = Path(original_review_path).read_text()
    reviewed_ids = re.findall(r"^## (v4_\d+) —", old_review, re.MULTILINE)
    assert len(reviewed_ids) == len(set(reviewed_ids)) == 22 and set(reviewed_ids) <= current.keys()
    changed = [id for id in current if previous[id] != current[id]]
    question_changed = [id for id in current if previous[id]["question"] != current[id]["question"]]
    answer_changed = [id for id in current if any(previous[id][key] != current[id][key] for key in ("reference_columns", "reference_rows"))]
    sql_changed = [id for id in current if previous[id]["reference_sql"] != current[id]["reference_sql"]]
    parameters_changed = [id for id in current if previous[id]["parameters"] != current[id]["parameters"]]
    substantive = [id for id in current if id in set(question_changed + answer_changed + sql_changed + parameters_changed)]
    metadata_only = [id for id in changed if id not in substantive]
    replacements = [id for id in reviewed_ids if id in substantive]
    selected = {id: ["original_22_identity", *(["replacement_of_reviewed_question"] if id in replacements else [])]
                for id in reviewed_ids}
    strata = {}
    for id, row in current.items():
        if row["window_expression"] is not None:
            strata.setdefault((row["window_expression"], row["template_family_id"]), []).append(id)
    covered = {current[id]["window_expression"] for id in selected}
    family_counts = Counter(current[id]["template_family_id"] for id in selected)
    actual_expressions = list(dict.fromkeys(row["window_expression"] for row in current.values() if row["window_expression"] is not None))
    for expression in actual_expressions:
        if expression in covered:
            continue
        candidates = [(family_counts[family], family, sorted(ids)[0])
                      for (window, family), ids in strata.items() if window == expression]
        _, family, id = min(candidates)
        selected[id] = ["uncovered_window_expression", f"stratum={expression} x {family}"]
        family_counts[family] += 1
        covered.add(expression)
    assert set(actual_expressions) <= covered and set(replacements) <= selected.keys()
    summary = {"old_questions_sha256": hashlib.sha256(previous_bytes).hexdigest(),
               "new_questions_sha256": hashlib.sha256(current_bytes).hexdigest(),
               "original_review_sha256": hashlib.sha256(Path(original_review_path).read_bytes()).hexdigest(),
               "record_changed_ids": changed, "question_changed_ids": question_changed,
               "answer_changed_ids": answer_changed, "reference_sql_changed_ids": sql_changed,
               "parameters_changed_ids": parameters_changed, "substantive_changed_ids": substantive,
               "metadata_only_changed_ids": metadata_only, "original_review_ids": reviewed_ids,
               "reviewed_replacement_ids": replacements,
               "reviewed_metadata_only_ids": [id for id in reviewed_ids if id in metadata_only],
               "selected_ids": list(selected), "window_expressions": actual_expressions}
    glossary = (ROOT / "eval/glossary.md").read_text()
    time_source = glossary.split("## 1. Time conventions\n", 1)[1].split("\n## 2.", 1)[0].strip()
    lines = ["# v4 Round 2 Manual Sample Review", "",
             "The original 22-question package remains unchanged. All its identities are included below using the current questions; substantive replacements are explicitly marked. Human Round 1 comments have not been supplied, so no signature, finding, or approval is invented.", "",
             "Selection is explicit window_expression x family stratification: retain the original 22 IDs; for every still-uncovered actual expression, choose a family with the smallest current selected count, breaking ties by family ID and then question ID. No fixed-stride sampling and no difficulty-based selection are used.", "",
             OUTSIDE_COVERAGE_NOTE, "", "## Change classification and complete ID inventories", "",
             "Record-level changes include new sensitivity evidence; they must not be interpreted as entity replacements. Substantive changes are the union of question text, reference SQL, reference columns/rows, and entity parameters.",
             "```json", json.dumps(summary, indent=2), "```", "", "## Selected window/family strata", "",
             "| ID | Window expression | Family | Selection reason |", "| --- | --- | --- | --- |"]
    for id, reasons in selected.items():
        row = current[id]
        lines.append(f"| {id} | {row['window_expression']} | {row['template_family_id']} | {', '.join(reasons)} |")
    for id, reasons in selected.items():
        row = current[id]
        lines += ["", f"## {id} — {row['template_family_id']} / {row['paraphrase_id']}", "",
                  "Selection: " + ", ".join(reasons) + ".", "", row["question"], "", "```sql", row["reference_sql"], "```", "",
                  f"Code-computed boundaries: `{row['bounds']}`.",
                  f"Reference columns: `{row['reference_columns']}`; reference row count: {len(row['reference_rows'])}.", ""]
        if id in replacements:
            lines += ["**REPLACEMENT OF AN ORIGINAL 22-QUESTION REVIEW ID — requires renewed human review.**", "",
                      "Previous question:", previous[id]["question"], "", "Previous reference rows:",
                      "```json", json.dumps(previous[id]["reference_rows"], indent=2), "```", "",
                      "Current reference rows:", "```json", json.dumps(row["reference_rows"], indent=2), "```", ""]
        lines += ["Glossary original:", "```text", time_source if row["bounds"] else "No effective time semantics; no time-boundary glossary entry applies.", "```", "",
                  "Manual worksheet (leave blank):", "", "| Item | Reviewer calculation |", "| --- | --- |",
                  "| Inclusive start | |", "| Inclusive final date | |", "| Exclusive end | |", "| UTC / reference-date check | |", "| Agreement and reviewer initials | |", "",
                  "Eligible sensitivity evidence:", "```json", json.dumps(row["sensitivity"], indent=2), "```", "",
                  "Excluded perturbations (not executed):", "```json", json.dumps(row["sensitivity_excluded"], indent=2), "```", "",
                  "Distractor injection probe:", "```json", json.dumps(row["distractor_probe"], indent=2), "```"]
    Path(out).write_text("\n".join(lines) + "\n")
    return summary


def candidate_windows(expression, snapshot_start, snapshot_end):
    """Preferred window first, then all same-length explicit starts in date order."""
    if expression is None:
        return [(None, None, None)]
    start, end = window_bounds(expression)
    assert snapshot_start <= start < end <= snapshot_end
    result = [(expression, start, end)]
    if expression in WINDOW_EXPRESSIONS[:3]:
        return result
    duration = end - start
    # Original preferred dates remain first. No fallback consumes RNG draws.
    for offset in range((snapshot_end - snapshot_start - duration).days + 1):
        candidate_start = snapshot_start + timedelta(days=offset)
        if candidate_start == start:
            continue
        candidate_end = candidate_start + duration
        phrase = f"October {candidate_start.day} through October {(candidate_end - timedelta(days=1)).day}, 2026"
        result.append((phrase, candidate_start, candidate_end))
    return result



# Adjudicated ladder, fixed before execution: retain the existing preferred and
# same-length explicit-window pool (tier 0); exhaust other existing EVENT_TYPES
# in tuple order within that pool (tier 1); exhaust all remaining authorized
# expressions (tier 2); only then retain the first otherwise-valid battery
# failure (tier 3), at most two semantic cases. No additional RNG draws occur.
# Window-family metrics are fixed glossary definitions, so tier 1 is empty.
# Tier 2 order: same expression type first, same duration first, then duration
# distance, duration, start, end, and expression. Each window uses preferred
# metric then the remaining EVENT_TYPES in tuple order, and the same entities.
def candidate_plan(family, expression, event_type, snapshot_start, snapshot_end):
    """Enumerate the finite, predeclared strict candidate ladder without outcomes."""
    base = candidate_windows(expression, snapshot_start, snapshot_end)
    metrics = [event_type]
    if family in TARGETED_ADVANCED + ADJACENT:
        assert event_type in EVENT_TYPES
        metrics += [metric for metric in EVENT_TYPES if metric != event_type]
    plan = [(0, window, event_type) for window in base]
    plan += [(1, window, metric) for metric in metrics[1:] for window in base]
    if expression is None:
        return plan
    length = (base[0][2] - base[0][1]).days
    relative = expression in WINDOW_EXPRESSIONS[:3]
    universe = [(phrase, *window_bounds(phrase)) for phrase in WINDOW_EXPRESSIONS[:3]]
    for first in range((snapshot_end - snapshot_start).days):
        for duration in range(1, (snapshot_end - snapshot_start).days - first + 1):
            start = snapshot_start + timedelta(days=first)
            end = start + timedelta(days=duration)
            phrase = f"October {start.day} through October {(end - timedelta(days=1)).day}, 2026"
            universe.append((phrase, start, end))
    occupied = {window[0] for window in base}
    remaining = [window for window in universe if window[0] not in occupied]
    remaining.sort(key=lambda window: (
        (window[0] in WINDOW_EXPRESSIONS[:3]) != relative,
        (window[2] - window[1]).days != length,
        abs((window[2] - window[1]).days - length),
        (window[2] - window[1]).days, window[1], window[2], window[0]))
    plan += [(2, window, metric) for window in remaining for metric in metrics]
    return plan


def select_candidate(family, case, preferred_expression, scope, event_type, pool, offset,
                     snapshot_start, snapshot_end, seed, digest, assigned, regen, relaxed_count):
    """Exhaust strict pools before a bounded, explicit sensitivity-only relaxation."""
    plan = candidate_plan(family, preferred_expression, event_type, snapshot_start, snapshot_end)
    total_positions = len(plan) * len(pool)
    first_relaxable = None
    for plan_index, (tier, (expression, start, end), metric) in enumerate(plan):
        for entity_index in range(len(pool)):
            params = {"entity": pool[(offset + entity_index) % len(pool)], "scope": scope, "event_type": metric}
            key = json.dumps([family, params, None if start is None else [start.isoformat(), end.isoformat()]], sort_keys=True)
            candidate = {"semantic_case_id": case, "attempt": plan_index * len(pool) + entity_index + 1,
                         "window_attempt": plan_index + 1, "entity_attempt": entity_index + 1,
                         "candidate_pool_positions": total_positions, "entity": params["entity"],
                         "preferred_window_expression": preferred_expression, "window_expression": expression,
                         "preferred_event_type": event_type, "event_type": metric, "fallback_tier": tier,
                         "bounds": None if start is None else [start.isoformat(), end.isoformat()],
                         "seed": seed, "snapshot_sha256": digest}
            if key in assigned:
                regen.append({**candidate, "event_kind": "dedup_exclusion", "reason": "duplicate_semantic_candidate",
                              "duplicate_of_semantic_case_id": assigned[key], "reference_sql": None,
                              "reference_row_count": None, "sensitivity": [], "sensitivity_excluded": []})
                continue
            sql, metrics = reference_sql(family, params, start, end)
            columns, rows = run_reference(sql)
            cases = [] if expression is None else sensitivity_cases(start, end, snapshot_start, snapshot_end)
            excluded = [item for item in cases if not item["eligible"]]
            try:
                for layer in PARAPHRASES:
                    assert_reference(sql, columns, rows, metrics, question_text(family, params, expression, layer))
            except CandidateRejected as error:
                regen.append({**candidate, "event_kind": "hard_assertion_failure", "reason": str(error),
                              "reference_sql": sql, "reference_row_count": len(rows), "reference_rows": rows,
                              "sensitivity": [], "sensitivity_excluded": excluded})
                continue
            sensitivity = []
            for perturbation in cases:
                if not perturbation["eligible"]:
                    continue
                altered_start, altered_end = (date.fromisoformat(value) for value in perturbation["bounds"])
                shifted_sql, _ = reference_sql(family, params, altered_start, altered_end)
                shifted_columns, shifted_rows = run_reference(shifted_sql)
                assert shifted_columns == columns
                sensitivity.append({**perturbation, "changed": not same_multiset(rows, shifted_rows),
                                    "reference_sql": shifted_sql, "row_count": len(shifted_rows), "rows": shifted_rows,
                                    "rows_sha256": hashlib.sha256(json.dumps(shifted_rows, sort_keys=True).encode()).hexdigest()})
            failures = [item["perturbation"] for item in sensitivity if not item["changed"]]
            result = {"params": params, "expression": expression, "start": start, "end": end, "sql": sql,
                      "columns": columns, "rows": rows, "sensitivity": sensitivity, "excluded": excluded,
                      "semantic_key": key, "fallback_tier": tier, "battery_relaxed": False,
                      "failed_perturbations": failures, "candidate": candidate}
            evidence = {**candidate, "reference_sql": sql, "reference_row_count": len(rows), "reference_rows": rows,
                        "sensitivity": sensitivity, "sensitivity_excluded": excluded,
                        "failed_perturbations": failures}
            if failures:
                regen.append({**evidence, "event_kind": "hard_assertion_failure", "reason": "insensitive_" + failures[0]})
                if first_relaxable is None:
                    first_relaxable = result
                continue
            regen.append({**evidence, "event_kind": "candidate_accepted", "reason": "strict_candidate_accepted"})
            return result
    if first_relaxable is not None and relaxed_count < 2:
        result = first_relaxable
        result.update(fallback_tier=3, battery_relaxed=True)
        regen.append({**result["candidate"], "event_kind": "battery_relaxed_acceptance", "reason": "strict_pool_exhausted",
                      "fallback_tier": 3, "strict_positions_exhausted": total_positions,
                      "relaxed_semantic_case_number": relaxed_count + 1, "reference_sql": result["sql"],
                      "reference_rows": result["rows"], "reference_row_count": len(result["rows"]),
                      "failed_perturbations": result["failed_perturbations"],
                      "sensitivity": result["sensitivity"], "sensitivity_excluded": result["excluded"]})
        return result
    reason = "battery_relaxed semantic-case cap of 2" if first_relaxable is not None else "non-battery assertions"
    raise RuntimeError(f"No candidate after {total_positions} deterministic attempts across the complete ladder: {case}; {reason}")

def generate(seed, out):
    """Generate 300 records; finite deterministic retries are limited to item 8."""
    if seed != 42:
        raise ValueError("The preregistered seed is fixed at 42.")
    asyncio.run(check_bounds_consistency())
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(DATABASE_PATH.read_bytes()).hexdigest()
    _, facts = run_reference("SELECT MIN(created_at) AS first_event, MAX(created_at) AS last_event FROM events")
    snapshot_start = date.fromisoformat(facts[0][0][:10])
    snapshot_end = date.fromisoformat(facts[0][1][:10]) + timedelta(days=1)
    _, repos = run_reference("SELECT name FROM repos ORDER BY name ASC")
    _, languages = run_reference("SELECT DISTINCT language FROM repos WHERE language IS NOT NULL ORDER BY language ASC")
    pools = {"repo": [row[0] for row in repos], "language": [row[0] for row in languages]}
    rng = random.Random(seed)
    for pool in pools.values():
        rng.shuffle(pool)
    glossary = (ROOT / "eval/glossary.md").read_text()
    specs = []
    for family in WINDOW_FAMILIES:
        for index, expression in enumerate(WINDOW_EXPRESSIONS):
            for scope in ("repo", "language"):
                specs.append((family, f"{family}_{index:02d}_{scope}", expression, scope, None))
    for family in TARGETED_ADVANCED + ADJACENT:
        for index, expression in enumerate(ADVANCED_WINDOWS):
            specs.append((family, f"{family}_{index:02d}", expression, "repo", EVENT_TYPES[index]))
    for family, scope in (("catalog_lookup", "repo"), ("language_composition", "language")):
        for index in range(5):
            specs.append((family, f"{family}_{index:02d}", None, scope, None))
    records, regen, assigned_semantics = [], [], {}
    relaxed_count = 0
    for family, case, preferred_expression, scope, event_type in specs:
        pool = pools[scope]
        offset = int(case.rsplit('_', 1)[1]) if family in CONTROLS else rng.randrange(len(pool))
        try:
            selected = select_candidate(family, case, preferred_expression, scope, event_type, pool, offset,
                                        snapshot_start, snapshot_end, seed, digest, assigned_semantics, regen, relaxed_count)
        except RuntimeError:
            (out.parent / "v4_regen_log.jsonl").write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in regen))
            raise
        params, expression, start, end = (selected[key] for key in ("params", "expression", "start", "end"))
        sql, columns, rows = (selected[key] for key in ("sql", "columns", "rows"))
        sensitivity, excluded = selected["sensitivity"], selected["excluded"]
        assigned_semantics[selected["semantic_key"]] = case
        relaxed_count += int(selected["battery_relaxed"])
        for layer in PARAPHRASES:
            text = question_text(family, params, expression, layer)
            probe = None
            if layer == "distractor":
                actual = asyncio.run(c2_date_context_for_question(text, OfflineSession(), glossary))
                suffix = actual.rsplit("\n", 1)[-1]
                probe = {"triggered": suffix.startswith("Question window:"),
                         "appended_line": suffix if suffix.startswith("Question window:") else None,
                         "selection_policy": "leftmost canonical window; decorative standalone years ignored",
                         "used_for_filtering": False}
            records.append({"record_type": "question", "id": f"v4_{len(records) + 1:03d}", "question": text,
                            "template_family_id": family, "semantic_case_id": case, "paraphrase_id": layer,
                            "targeted": family in WINDOW_FAMILIES + TARGETED_ADVANCED,
                            "layer": "window" if family in WINDOW_FAMILIES else "control" if family in CONTROLS else "advanced_sql",
                            "snapshot_sha256": digest, "window_expression": expression,
                            "preferred_window_expression": preferred_expression, "preferred_event_type": event_type,
                            "fallback_tier": selected["fallback_tier"], "battery_relaxed": selected["battery_relaxed"],
                            "failed_perturbations": selected["failed_perturbations"],
                            "bounds": None if expression is None else [start.isoformat(), end.isoformat()],
                            "parameters": params, "reference_sql": sql, "reference_columns": columns,
                            "reference_rows": rows, "sensitivity": sensitivity, "sensitivity_excluded": excluded, "distractor_probe": probe})
    assert len(records) == 300 and len(assigned_semantics) == 100 and relaxed_count <= 2
    dedup = check_dedup(records)
    # Full-question overlap is forbidden; literal authorized time spans are required
    # by the later adjudication and are disclosed separately in the overlap audit.
    source_sentences = [normalized_text(line.strip('- ')) for line in glossary.splitlines() if line.strip()]
    copied = [row['id'] for row in records if normalized_text(row['question']) in source_sentences]
    assert not copied, "A template copies a complete glossary source sentence."
    assert hashlib.sha256(DATABASE_PATH.read_bytes()).hexdigest() == digest
    metadata = {"record_type": "metadata", "seed": seed, "question_count": 300,
                "snapshot_sha256": digest, "first_event": facts[0][0], "last_event": facts[0][1],
                "snapshot_bounds": [snapshot_start.isoformat(), snapshot_end.isoformat()],
                "zero_row_policy": "All v4 families forbid empty reference row sets and all-zero metric aggregates.",
                "sensitivity_policy": "Six endpoint perturbations; every in-coverage variant must change the result multiset except explicitly flagged tier-3 cases (at most two semantic cases). Empty half-open intervals from one-day-window contraction remain measurable.",
                "outside_coverage_note": OUTSIDE_COVERAGE_NOTE,
                "regeneration_policy": "Tier 0: preferred metric and existing same-length explicit window pool. Tier 1: remaining authorized EVENT_TYPES in fixed order on that pool. Tier 2: all other authorized windows, same type/length first, stable date order, preferred metric then remaining metrics. Tier 3: first otherwise-valid candidate only after full strict exhaustion; at most two semantic cases. All tiers use the same seeded entity order; duplicate identities remain excluded.",
                "battery_relaxed_semantic_cases": relaxed_count,
                "control_policy": "No effective time predicate; distractor years are explicitly irrelevant and never filter SQL.",
                "grader_comparison": "eval.grader.same_multiset reused; grader.py unchanged; scoring integration deferred.",
                "family_counts": dict(sorted(Counter(row['template_family_id'] for row in records).items()))}
    out.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n" for row in [metadata] + records))
    (out.parent / "v4_regen_log.jsonl").write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in regen))
    overlap = ["# v4 Text Overlap Audit", "", f"Historical normalized full-question overlap: {dedup['historical_overlap']}; v4 unique questions: {dedup['v4_unique']}.",
               "", "Normalization: Unicode NFKC, casefold, punctuation/whitespace collapse. All 60 v2 and 26 v3 questions were included.",
               "", "Complete glossary-line/template-question duplicates: 0. No complete glossary example sentence was used as a question.",
               "", "Required lexical overlap: the authorized time expressions deliberately repeat glossary wording under the later human adjudication. This is disclosed, not classified as an unauthorized copied question. Non-time template wording is new; the colloquial layer preserves time wording verbatim.",
               "", "| Authorized adopted expression | Exact glossary substring |", "| --- | --- |"]
    for expression in dict.fromkeys(row["window_expression"] for row in records if row["window_expression"] is not None):
        overlap.append(f"| {expression} | {'yes' if expression.casefold() in glossary.casefold() else 'no; covered by adjudicated explicit-range rule'} |")
    overlap += ["", "Adjacent families: session segmentation and consecutive active-day runs. Neither appears in the full frozen v2/v3 question texts or reference SQL, a stronger inventory check than the failure-only subset. Existing running/rolling averages and anti-join families were not chosen as adjacent controls.",
                "", "No overlap finding was used as a reason to regenerate an entity or select an easier result."]
    (out.parent / "v4_overlap_audit.md").write_text("\n".join(overlap) + "\n")
    # Preserve the original 22-question package. Round 2 is written separately
    # with explicit previous/current inputs after successful generation.
    return {"questions": len(records), "families": metadata["family_counts"], "regenerations": sum(row["event_kind"] == "hard_assertion_failure" for row in regen),
            "dedup_pool_exclusions": sum(row["event_kind"] == "dedup_exclusion" for row in regen),
            "logged_candidate_events": len(regen), "battery_relaxed_semantic_cases": relaxed_count,
            "fallback_tier_counts": dict(sorted(Counter(row["fallback_tier"] for row in records if row["paraphrase_id"] == "literal").items())),
            "regeneration_reasons": dict(sorted(Counter(row['reason'] for row in regen if row["event_kind"] == "hard_assertion_failure").items())), "dedup": dedup,
            "eligible_perturbations_per_question_record": sum(len(row["sensitivity"]) for row in records),
            "excluded_perturbations_per_question_record": sum(len(row["sensitivity_excluded"]) for row in records)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42, choices=(42,))
    parser.add_argument("--out", type=Path, default=ROOT / "eval/v4_questions.jsonl")
    args = parser.parse_args()
    print(json.dumps(generate(args.seed, args.out), indent=2))
