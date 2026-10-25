# v3 paired C versus C2 report

## Frozen endpoints

| Endpoint | C | C2 |
|---|---:|---:|
| Primary: whole-question accuracy, v3_01–v3_13 | 12/13 | 12/13 |
| Secondary: whole-question accuracy, v3_01–v3_26 | 21/26 | 24/26 |

The primary endpoint is tied. Among incorrect primary-endpoint runs, C has one window error and C2 has none. This observation is consistent with the preregistered inequality, but does not establish the proposed causal mechanism or guarantee elimination of every semantic window mistake. No p-values were calculated.

## Collection and first-write-wins integrity

All 52 terminal records are present: 26 questions × two configurations, 26 records per configuration, with 52 unique (question_id, config) pairs and no omissions or duplicates. Odd-numbered questions ran C then C2; even-numbered questions ran C2 then C. Execution order is recorded as 1–52.

Collection began at 2026-10-25T06:58:28.992497+00:00 and ended at 2026-10-25T07:05:10.980727+00:00. The collector exited with code 0. There are 51 completed runs and one error: v3_17 / C, which stopped after three consecutive SQL errors and has no submitted answer. All recorded outcomes are final; no run was repeated.

No correctness calculations or accuracy summaries were performed until all 52 records existed. Raw pass/fail fields remain null and grading_status remains pending; the separate classification file contains all 52 decisions without rewriting any raw line. Historical results and traces were not used as output destinations.

## Scoring path and deterministic comparison

The v2 implementation executes reference SQL through mcp_server.execute_select, but grades successful agent answers from their recorded MCP result rows; it does not execute final answer_sql again offline. Evidence: eval/grader.py:50 and :65–77; eval/regrade.py:48–67; eval/run_experiment.py:87–96; agent/loop.py:206 and :226–230.

Following the later explicit approval, only trusted reference SQL was executed unchanged directly in read-only DuckDB. This resolves the frozen validator rejecting EXISTS in canonical references v3_16 and v3_18. Agent answers were graded from successful recorded MCP submission rows, preserving the v2 answer path. The earlier final-SQL-execution wording therefore does not mean offline reconstruction or rescue of agent answers. Rejected or unsubmitted attempts never supply graded rows.

The frozen v3 comparison rules are retained: ignore column aliases and compare all output columns by position; compare ordered row sequences when the reference has a top-level ORDER BY, otherwise compare multisets preserving duplicate multiplicities. Extra or missing output columns fail the shape comparison. There is no column permutation, answer trimming, rounding, or numerical tolerance. These v3 comparison rules differ from v2 column matching and were not replaced by the v2 grader.

Direct reference rows were marshalled with the existing MCP json_value representation to compare with stored JSON answer rows. DATE values consequently use ISO date strings, as they do in the v2 MCP path. Reference types are BIGINT, HUGEINT, VARCHAR and DATE; no floating-point reference columns require a tolerance decision. No SQL was rewritten. Empty reference sets, if present, remain valid row sets under the v3 rule; no v2 EMPTY_REFERENCE override was introduced.

Read-only connections retained the existing 2GB memory limit, two threads, disabled external access and extension auto-install/load, a ten-second interruptible deadline, and bounded result fetching. The direct-execution exception was limited to trusted frozen references and the separately authorized rejected-attempt audit. The production MCP whitelist and runtime remained unchanged.

## Complete paired verdicts

| Question | C | C2 |
|---|---|---|
| v3_01 | PASS | PASS |
| v3_02 | PASS | PASS |
| v3_03 | PASS | FAIL (wrong_result_set) |
| v3_04 | PASS | PASS |
| v3_05 | FAIL (wrong_result_set) | PASS |
| v3_06 | PASS | PASS |
| v3_07 | PASS | PASS |
| v3_08 | PASS | PASS |
| v3_09 | PASS | PASS |
| v3_10 | PASS | PASS |
| v3_11 | PASS | PASS |
| v3_12 | PASS | PASS |
| v3_13 | PASS | PASS |
| v3_14 | FAIL (wrong_result_set) | PASS |
| v3_15 | PASS | PASS |
| v3_16 | FAIL (wrong_result_set) | PASS |
| v3_17 | FAIL (sql_error_exhausted) | PASS |
| v3_18 | PASS | PASS |
| v3_19 | PASS | PASS |
| v3_20 | FAIL (wrong_result_set) | FAIL (wrong_result_set) |
| v3_21 | PASS | PASS |
| v3_22 | PASS | PASS |
| v3_23 | PASS | PASS |
| v3_24 | PASS | PASS |
| v3_25 | PASS | PASS |
| v3_26 | PASS | PASS |

## Window-error classification

Only incorrect runs on v3_01–v3_13 enter the preregistered window-error classification. Classification does not change their deterministic correctness verdicts.

| Run | Reference window | Submitted window | Classification and evidence |
|---|---|---|---|
| v3_05 / C | [2026-10-08, 2026-10-15) | [2026-10-15, 2026-10-22) | Window error: both boundaries shifted seven days later; second week selected instead of first. Reference count 24; recorded answer 40. |
| v3_03 / C2 | [2026-10-15, 2026-10-22) | [2026-10-15, 2026-10-22) | Non-window error: `NOT lower(actor) NOT LIKE '%[bot]'` selects the bot-suffix group rather than excluding it. Reference count 16; recorded answer 5. |

Counts: C one window error; C2 zero window errors. Pending human reviews: none. No ambiguous time expression required a guessed classification, and no equivalent DATE BETWEEN expression was counted as an error.

Correct runs were not relabeled as window errors. In particular, C submitted an upper bound of 2026-10-23 instead of 2026-10-22 for v3_11 and v3_12, but the frozen snapshot has no later records and both recorded result sets equal their references. These predicate differences are disclosed without changing the result-based scores or expanding the preregistered classification denominator. V3_16 / C also selects the wrong week, but lies outside the primary v3_01–v3_13 classification scope.

## Negative controls

Actual successful recorded result rows were compared between C and C2, not merely their pass/fail flags. Column aliases were ignored under the same positional rule; ordered controls retained row order.

| Control | Comparison | Actual C versus C2 result | Reference verdicts |
|---|---|---|---|
| v3_20 | Multiset | Identical: one row, four columns | Both fail: both include name in addition to the three requested numeric columns. |
| v3_21 | Ordered sequence | Identical: five rows, two columns | Both pass. |
| v3_22 | Multiset | Identical: one row, one column | Both pass. |
| v3_23 | Ordered sequence | Identical: five rows, three columns | Both pass. |

All four negative-control result comparisons are identical. The preregistered negative-control suspension condition is not triggered. This is an observed control check, not proof that context injection can never have side effects.

## Sandbox-artifact audit and failure disclosure

All 52 recorded trajectories were inspected. Ten whitelist-rejected SQL attempts across seven runs executed successfully in the separately authorized bounded read-only DuckDB audit. None was a successfully submitted final answer_sql. Counts of successfully submitted final SQL rejected by the whitelist: zero; corresponding run IDs: none. Offline executability is a sandbox-artifact observation, not a model-capability signal, and has no effect on scores.

| Run | Tool position/name | Runtime rejection | Native audit | Eventual run outcome |
|---|---|---|---|---|
| v3_14 / C | 4 / run_query | Function is not allowed: EXISTS | Executes; not truncated | completed with a different successful submission |
| v3_16 / C2 | 3 / run_query | Function is not allowed: EXISTS | Executes; not truncated | completed with a different successful submission |
| v3_16 / C | 3 / run_query | Function is not allowed: EXISTS | Executes; not truncated | completed with a different successful submission |
| v3_17 / C | 3 / run_query | SQL construct is not allowed: Values | Executes; not truncated | error; no submission |
| v3_17 / C | 4 / run_query | SQL construct is not allowed: Union | Executes; not truncated | error; no submission |
| v3_17 / C | 5 / run_query | Only generate_series is allowed; range is not allowed. | Executes; not truncated | error; no submission |
| v3_17 / C2 | 3 / run_query | SQL construct is not allowed: Values | Executes; not truncated | completed with a different successful submission |
| v3_17 / C2 | 4 / run_query | SQL construct is not allowed: Union | Executes; not truncated | completed with a different successful submission |
| v3_18 / C2 | 5 / submit_answer | Function is not allowed: EXISTS | Executes; not truncated | completed with a different successful submission |
| v3_18 / C | 4 / run_query | Function is not allowed: EXISTS | Executes; not truncated | completed with a different successful submission |

The v3_18 / C2 submit_answer entry above was a failed submission attempt, not its final committed answer. Its later successful submission used a different, accepted LEFT JOIN query. The other rejected calls were intermediate run_query attempts. Full SQL, call IDs, exact runtime errors, native audit rows and eventual statuses are retained in each affected classification record.

V3_17 / C, raw record line 33, has status=error, submitted=false, answer_sql=null, answer_columns=null and answer_rows=null. It made no submit_answer call. Its three consecutive original errors were:

```text
Error executing tool run_query: SQL construct is not allowed: Values
Error executing tool run_query: SQL construct is not allowed: Union
Error executing tool run_query: Only generate_series is allowed; range is not allowed.
```

They arose from a VALUES CTE, a UNION ALL CTE and a range(0,5) table source, respectively. None contains EXISTS or NOT EXISTS. The terminal message is `Agent stopped: Stopped after 3 consecutive SQL errors.` Although those attempts execute in the separate native audit, v3_17 / C remains sql_error_exhausted; an unsubmitted attempt is never promoted to a final answer.

## Model settings and provenance limits

Every actual request specified model=deepseek-chat and temperature=0. All 224 provider responses reported model=deepseek-flash in response metadata. Both the requested parameters and response model fields are preserved in every raw run. No requested model was changed, and no explanation for the response-label difference is assumed. Other optional generation parameters were not explicitly supplied; provider defaults are not claimed to be pinned.

Runs_v2.jsonl does not record model, temperature or generation metadata. The original raw-run artifact commits are 70842e457a5392cf8c4f52a0183861dbb46a04ae (2026-10-23T13:19:08+08:00, 90 records) and 0f17c293e7cef5ae9585d776c696ae16ff980078 (2026-10-23T16:36:00+08:00, 180 records). These are artifact commit times, not original generation timestamps or the date of offline regrading.

Git log -p showed that agent/loop.py first entered tracked history later, at cbe87dd021634d8361b1f8479a18bad711ae10af (2026-10-23T20:10:18+08:00). Tracked deepseek-chat / temperature=0 settings are unchanged from that commit through HEAD c04d75ff2c83dfe42c7e212b36b473352a558ac0, including the current relevant working-tree files. This cannot establish production-time uncommitted state before the file was tracked. Historical v2/v3 generation-parameter consistency is therefore unverified; these v3 runs use explicitly authorized current-code provenance. This limitation and the commit range are embedded in every record.

C and C2 used the same existing loop and lookup behavior. All 26 C2 runs had the precomputed boundary block in the sent system context; all 26 C runs excluded it. Context assembly did not consume the deliberative tool budget. No prompts, question SQL, glossary definitions, runtime whitelist, grader source or historical records were changed.

## API retries

API retries: 0. The temporary request ledger contains 224 started requests and 224 received responses, with no transport-error events. The SDK retry setting was zero. Model turns within a run are not retries of a recorded question/config pair. The single terminal error was the SQL-error circuit breaker, not an API retry.

## Artifact hashes and protected-file verification

| Artifact | SHA-256 |
|---|---|
| eval/results/runs_v3.jsonl | b318335647b5037ec217adfae08754a0923bc4b4fd0d00b84b8009ad753f85be |
| eval/v3_classification.jsonl | 9723d55d046bec920bbea16e91648a20e0e25e2de2429fb533ef080c41000677 |
| eval/v3_preregister.md | 537853be1647d2ebf393618d1fe88f356d3731891fee45cd1df1910502fb7fcf |
| eval/v3_questions.jsonl | d663207daa8095a0b55efe5425456ee8f427077dbd54311718f1591c1515c3d6 |
| data/github.duckdb | 2a063cab4176b97cfd00ea8e92932c64346127ba1da4b120452fb48236c25812 |
| agent/loop.py | 78b02e5a4235581fd0f93f5df5adab54c8a1b6b5b6abc78ab0d3e20c9da09952 |
| agent/mcp_server.py | 3b55d233b1f8f27c1398df53a75065a456456e97219ac2607e9eb03d44b4d41f |
| eval/grader.py | 34fdf04fb0a75836f78a0e2ec4c90fef4d9b7b5f6c4cab730b00abcbe502dd57 |
| eval/glossary.md | 1a2ce44850529108249fe9970803b1745787ecf37c63136a062a11bb808c3d05 |
| eval/results/runs.jsonl | bb5194dc054ab96c821f8b5509460b54eb719ca6d38af4fbe0e27613e5347b00 |
| eval/results/runs_v2.jsonl | a6400c28fa4d4e937e492f3ac1fa2d653ebcfa7ddaf0227f826772251af801ae |
| eval/results/mechanism_probe.jsonl | 081e290f4a06291ed2cf963ff468167ce4409b3f88e6125b745acc285c62d291 |
| eval/results/summary.md | 9c122c5f21f1d15dd1da2237ba9549f10a49c9d541f8cedc1224dcbcffdcdcce |
| eval/traces.jsonl | 495bbf2d7fae7750127598fbb1782a45afbc366c718bce9d6260bed20197d616 |

All 58 pre-existing protected-file hashes match the pre-collection baseline, including all question/reference versions, source files, the preregistration, database, historical results, summary, traces and README. The raw runs_v3 bytes also remain unchanged after grading. The only repository outputs are eval/results/runs_v3.jsonl, eval/v3_classification.jsonl and eval/v3_report.md. No source edits, dependency changes, extra agent calls, commits, staging or pushes were performed.
