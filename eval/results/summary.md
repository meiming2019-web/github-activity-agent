# Experiment summary

Each (question, config) pair was attempted exactly once; recorded outcomes are final.

Reference date: 2026-10-22 (UTC).

| Config | Passed / questions | Prompt tokens | Completion tokens | Total tokens |
|---|---:|---:|---:|---:|
| A | 11/30 | 398207 | 4975 | 403182 |
| B | 12/30 | 1854115 | 29334 | 1883449 |
| C | 14/30 | 2059947 | 31924 | 2091871 |

Tokens include all recorded attempts; each question/config counts once in the pass matrix.

| Question | A | B | C |
|---|---|---|---|
| t01 | PASS | PASS | PASS |
| t02 | FAIL (missing_columns) | FAIL (missing_columns) | PASS |
| t03 | PASS | PASS | PASS |
| t04 | FAIL (missing_columns) | FAIL (missing_columns) | FAIL (missing_columns) |
| t05 | PASS | FAIL (missing_columns) | FAIL (missing_columns) |
| t06 | PASS | PASS | PASS |
| t07 | FAIL (no_submission) | FAIL (sql_error_exhausted) | FAIL (sql_error_exhausted) |
| t08 | FAIL (missing_columns) | PASS | PASS |
| t09 | PASS | PASS | PASS |
| t10 | FAIL (missing_columns) | FAIL (sql_error_exhausted) | PASS |
| t11 | PASS | PASS | PASS |
| t12 | PASS | PASS | PASS |
| t13 | FAIL (missing_columns) | FAIL (missing_columns) | FAIL (missing_columns) |
| t14 | PASS | PASS | PASS |
| t15 | FAIL (missing_columns) | FAIL (missing_columns) | FAIL (missing_columns) |
| t16 | FAIL (missing_columns) | FAIL (missing_columns) | FAIL (missing_columns) |
| t17 | FAIL (missing_columns) | FAIL (missing_columns) | FAIL (missing_columns) |
| t18 | FAIL (missing_columns) | FAIL (missing_columns) | FAIL (missing_columns) |
| t19 | FAIL (missing_columns) | FAIL (missing_columns) | FAIL (missing_columns) |
| t20 | PASS | FAIL (sql_error_exhausted) | PASS |
| t21 | FAIL (wrong_result_set) | FAIL (missing_columns) | FAIL (missing_columns) |
| t22 | FAIL (missing_columns) | FAIL (missing_columns) | FAIL (missing_columns) |
| t23 | FAIL (missing_columns) | PASS | FAIL (missing_columns) |
| t24 | FAIL (missing_columns) | PASS | PASS |
| t25 | PASS | PASS | PASS |
| t26 | FAIL (no_submission) | FAIL (missing_columns) | FAIL (sql_error_exhausted) |
| t27 | FAIL (missing_columns) | FAIL (missing_columns) | FAIL (missing_columns) |
| t28 | FAIL (missing_columns) | FAIL (missing_columns) | FAIL (missing_columns) |
| t29 | FAIL (missing_columns) | FAIL (missing_columns) | FAIL (missing_columns) |
| t30 | PASS | PASS | PASS |

## Grader v2 re-score (post-hoc, disclosed)
Test set = batch 1 (t01-t30, frozen 2026-10-23) + batch 2 (u01-u30, frozen 2026-10-23), identical authoring protocol; batch 2 graded under grader v2 from first run.

Agent attempts frozen first-write-wins; no agent re-runs. Re-scoring applied two disclosed corrections:
(1) answer-key errata — expected identifier repo_id replaced by repo name (1:1 isomorphic in catalog; questions ask "which repositories", never IDs);
(2) grader v2 column matching — partial name match + injective value matching, fixing v1's all-or-nothing positional fallback.
v1 results above remain the primary frozen record.

| Config | v1 | v2 | Delta |
|---|---:|---:|---:|
| A | 11/30 | 18/30 | +7 |
| B | 12/30 | 20/30 | +8 |
| C | 14/30 | 24/30 | +10 |

Changed verdicts (including changes between failure categories):

| Question | Config | Old result/category | New result | matched_by |
|---|---|---|---|---|
| t02 | A | missing_columns | FAIL (wrong_result_set) | null |
| t02 | B | missing_columns | FAIL (wrong_result_set) | null |
| t04 | A | missing_columns | PASS | column_names |
| t04 | B | missing_columns | PASS | column_names |
| t04 | C | missing_columns | PASS | column_names |
| t05 | B | missing_columns | FAIL (wrong_result_set) | null |
| t05 | C | missing_columns | FAIL (wrong_result_set) | null |
| t08 | A | missing_columns | FAIL (wrong_result_set) | null |
| t10 | A | missing_columns | FAIL (wrong_result_set) | null |
| t13 | A | missing_columns | FAIL (wrong_result_set) | null |
| t13 | B | missing_columns | FAIL (wrong_result_set) | null |
| t13 | C | missing_columns | PASS | name_plus_values |
| t15 | A | missing_columns | PASS | name_plus_values |
| t15 | B | missing_columns | PASS | column_names |
| t15 | C | missing_columns | PASS | column_names |
| t16 | B | missing_columns | PASS | name_plus_values |
| t16 | C | missing_columns | PASS | name_plus_values |
| t17 | A | missing_columns | FAIL (wrong_result_set) | null |
| t17 | B | missing_columns | PASS | name_plus_values |
| t17 | C | missing_columns | PASS | name_plus_values |
| t18 | A | missing_columns | PASS | column_names |
| t18 | B | missing_columns | PASS | column_names |
| t18 | C | missing_columns | PASS | column_names |
| t19 | A | missing_columns | FAIL (wrong_result_set) | null |
| t19 | B | missing_columns | FAIL (wrong_result_set) | null |
| t19 | C | missing_columns | FAIL (wrong_result_set) | null |
| t21 | B | missing_columns | FAIL (wrong_result_set) | null |
| t21 | C | missing_columns | FAIL (wrong_result_set) | null |
| t22 | A | missing_columns | FAIL (wrong_result_set) | null |
| t22 | B | missing_columns | FAIL (wrong_result_set) | null |
| t22 | C | missing_columns | FAIL (wrong_result_set) | null |
| t23 | A | missing_columns | PASS | name_plus_values |
| t23 | C | missing_columns | PASS | name_plus_values |
| t24 | A | missing_columns | FAIL (wrong_result_set) | null |
| t26 | B | missing_columns | FAIL (wrong_result_set) | null |
| t27 | A | missing_columns | PASS | name_plus_values |
| t27 | B | missing_columns | PASS | name_plus_values |
| t27 | C | missing_columns | PASS | name_plus_values |
| t28 | A | missing_columns | PASS | name_plus_values |
| t28 | B | missing_columns | PASS | name_plus_values |
| t28 | C | missing_columns | PASS | name_plus_values |
| t29 | A | missing_columns | PASS | name_plus_values |
| t29 | B | missing_columns | PASS | name_plus_values |
| t29 | C | missing_columns | PASS | name_plus_values |

t07 evidence discrepancy: EXTRACT(ISODOW) is whitelisted and returned Monday=1, Sunday=7. Frozen records confirm the recorded failures below, but do not retain B/C's rejected SQL/functions; their exact dialect-function failure cause cannot be verified without inventing evidence. A: Run status=error; submitted=False. Baseline stopped: Error executing tool run_query: Function is not allowed: TIME_TO_STR; B: Run status=error; submitted=False. Agent stopped: Stopped after 3 consecutive SQL errors.; C: Run status=error; submitted=False. Agent stopped: Stopped after 3 consecutive SQL errors.
