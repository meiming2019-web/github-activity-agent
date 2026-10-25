# C3 on the seen v2 question set: Phase D regression report

**Guardrail exceeded: conclusions are suspended pending manual investigation.** Two C2-correct questions became C3-incorrect, exceeding the preregistered allowance of at most one. The outcomes below are retained without repair or reruns.

This is regression-level evidence on an already-seen 60-question set, not a confirmatory experiment. The hypothesis was that actionable error feedback can reduce sql_error_exhausted and revive previously circuit-broken questions without relaxing the whitelist. The observations do not establish that hypothesis causally; the frozen guardrail requires suspension of conclusions.

## Preregistered outcomes

| Endpoint | C2 baseline | C3 |
|---|---:|---:|
| Primary: revived among t07, t20, t24, u24, u30 | 0/5 | 2/5 |
| Secondary: total correct | 47/60 | 47/60 |
| Secondary: sql_error_exhausted count | 5 | 1 |
| Secondary: mean steps to first success after an error, descriptive definition below | 4/3 | 4/3 |
| Secondary: tool-call count | 319 | 333 |
| Secondary: prompt tokens | 3793981 | 4030090 |
| Secondary: completion tokens | 63755 | 67587 |

Revived means successfully submitted AND graded correct. Only t20 and u30 meet both conditions. Avoiding the SQL-error circuit breaker alone does not count as revival. Overall correctness is tied; no p-values were calculated. Negative findings and the tie are reported unchanged.

## Guardrail and paired transitions

C2-correct to C3-incorrect transitions: **2**, on **t02 and t17**. Expected: <= 1. Since 2 > 1, conclusions are suspended pending manual investigation. This rule is applied regardless of the aggregate tie or reduction in circuit-breaker failures.

| Transition | Count | Complete question IDs |
|---|---:|---|
| C2 incorrect → C3 correct | 2 | t20, u30 |
| C2 correct → C3 incorrect | 2 | t02, t17 |
| Both correct | 45 | t01, t03, t04, t06, t08, t09, t11, t12, t14, t15, t16, t18, t23, t25, t27, t28, t29, t30, u01, u02, u03, u04, u05, u06, u07, u08, u09, u10, u11, u12, u13, u14, u15, u16, u17, u18, u19, u20, u21, u22, u23, u25, u27, u28, u29 |
| Both incorrect | 11 | t05, t07, t10, t13, t19, t21, t22, t24, t26, u24, u26 |

All 60 IDs appear exactly once in the transition partition. Neither t02 nor t17 encountered an SQL tool error or received mapped feedback in its C3 trajectory. That does not cancel the guardrail violation and does not prove a cause for either regression; both submitted results fail the unchanged v2 comparison.

## All five previously circuit-broken questions

| Question | C3 runtime status | Submitted | Correct | Revived | Final failure category | Tools / model turns | Mapped feedback messages |
|---|---|---|---|---|---|---|---:|
| t07 | completed | Yes | No | No | wrong_result_set | 7 / 7 | 2 |
| t20 | completed | Yes | Yes | Yes | none | 8 / 6 | 0 |
| t24 | completed | Yes | No | No | wrong_result_set | 6 / 6 | 1 |
| u24 | error | No | No | No | sql_error_exhausted | 7 / 6 | 0 |
| u30 | completed | Yes | Yes | Yes | none | 7 / 7 | 2 |

- **t07:** two run_query whitelist refusals (TIME_TO_STR and DAYNAME) received the approved feedback. A later query executed successfully and an answer was submitted, but it was not graded correct. The submitted column named day_of_week contains weekday-name strings, whereas the reference column with that name is numeric. The v2 grader pins the matching name; the separate numeric dow_num column does not override that pinning. The verdict was not manually rescued.
- **t20:** successfully submitted and correct, hence revived. Its one error was a failed submit_answer using ARRAY_CONTAINS; that error remained raw because the approved middleware intercepts run_query only. No mapped feedback was delivered in this trajectory. Its revival therefore cannot be attributed directly to an observed mapped hint.
- **t24:** one run_query EXPLODE refusal received feedback, then a query executed and an answer was submitted. The final query returns ten event-bearing dates rather than the reference calendar's fourteen dates. Execution recovery did not satisfy the frozen correctness rule; not revived.
- **u24:** no successful submission and no final answer_sql. Three consecutive failed submit_answer attempts were rejected for UNNEST, recursive CTEs and Values. All remained unmodified under the frozen run_query-only interception rule. The run stopped with sql_error_exhausted and was not rerun or rescued offline.
- **u30:** two run_query refusals (EXPLODE and Values) received approved hints. A later query executed, was submitted and matched the reference; revived. Its date spine is derived from observed event dates. Equality on this frozen snapshot does not prove that this spelling would preserve zero-event dates on arbitrary data.

The C3 file has 59 completed runtime statuses and one error status. Its thirteen grading failures are twelve wrong_result_set and one sql_error_exhausted. A runtime-completed status is not a correctness verdict.

## Recovery-step endpoint: ambiguity and descriptive calculation

The frozen preregistration names "mean number of steps to first success after an error" but does not operationally define steps, success, repeated errors or unrecovered cases. The following descriptive interpretation was disclosed and retained outside the repository before collection; it was not added to or represented as a frozen confirmatory definition:

- A recovery episode opens at the first failed SQL tool call, meaning run_query or submit_answer. Further SQL failures before success remain in the same episode.
- A step is an actually dispatched tool call after the opening failure, including the successful call. Intervening metadata and lookup calls count as steps but do not themselves end SQL recovery. Static-context assembly calls are outside the deliberative trace and are excluded.
- The episode closes at the first later successful SQL tool call, including a successful submission. For adjacent failure then success, the distance is one step. Undispatched post-submission rejections are excluded.
- An episode without a later successful SQL tool call is reported as unrecovered with no finite recovery-step value. It is not assigned zero and is not silently dropped from the accounting. The displayed mean is conditional on recovered episodes, not a mean over all failures.

| Descriptive recovery accounting | C2 | C3 |
|---|---:|---:|
| Total SQL-error episodes | 8 | 7 |
| Recovered episodes contributing a finite distance | 3 | 6 |
| Unrecovered episodes | 5 | 1 |
| Individual finite distances, in trace order | 1, 1, 2 | 2, 1, 1, 1, 1, 2 |
| Conditional mean | 4/3 = 1.333333… | 8/6 = 1.333333… |

Thus this descriptive mean is tied, with different recovery/censoring denominators. It is not evidence that C3 recovers faster. Recovering a syntactically executable SQL statement is separate from submitting a correct answer.

Episode audit (positions refer to each saved tool_calls trace; distances count dispatched calls):

| Config | Question | First error position | SQL errors in episode | First successful SQL position | Steps |
|---|---|---:|---:|---|---|
| C2 | t07 | 3 | 3 | none | unrecovered |
| C2 | t13 | 6 | 1 | 7 | 1 |
| C2 | t20 | 5 | 3 | none | unrecovered |
| C2 | t21 | 5 | 1 | 6 | 1 |
| C2 | t24 | 3 | 3 | none | unrecovered |
| C2 | u22 | 3 | 2 | 5 | 2 |
| C2 | u24 | 5 | 3 | none | unrecovered |
| C2 | u30 | 3 | 3 | none | unrecovered |
| C3 | t07 | 3 | 2 | 5 | 2 |
| C3 | t20 | 7 | 1 | 8 | 1 |
| C3 | t24 | 3 | 1 | 4 | 1 |
| C3 | u10 | 6 | 1 | 7 | 1 |
| C3 | u22 | 3 | 1 | 4 | 1 |
| C3 | u24 | 5 | 3 | none | unrecovered |
| C3 | u30 | 3 | 2 | 5 | 2 |

## Cost and observed feedback

| Measure across all 60 attempts | C2 | C3 |
|---|---:|---:|
| Tool-call count | 319 | 333 |
| Glossary lookup calls / received returns | 73 / 73 | 76 / 76 |
| Prompt tokens | 3793981 | 4030090 |
| Completion tokens | 63755 | 67587 |
| Total tokens | 3857736 | 4097677 |

Totals include failed attempts. Tool-call counters and static-context exclusions follow the unchanged loop path. C3 has seven mapped-feedback entries; each retains a sanitized raw_error separately from the feedback text. Full glossary arguments and exact returned sections are retained in the new records. Failed submit_answer errors and native/uncovered database errors remain passthrough by design; no middleware SQL rewrite or automatic tool retry occurred.

## Complete paired grading results

| Question | C2 | C3 |
|---|---|---|
| t01 | PASS | PASS |
| t02 | PASS | FAIL (wrong_result_set) |
| t03 | PASS | PASS |
| t04 | PASS | PASS |
| t05 | FAIL (wrong_result_set) | FAIL (wrong_result_set) |
| t06 | PASS | PASS |
| t07 | FAIL (sql_error_exhausted) | FAIL (wrong_result_set) |
| t08 | PASS | PASS |
| t09 | PASS | PASS |
| t10 | FAIL (wrong_result_set) | FAIL (wrong_result_set) |
| t11 | PASS | PASS |
| t12 | PASS | PASS |
| t13 | FAIL (wrong_result_set) | FAIL (wrong_result_set) |
| t14 | PASS | PASS |
| t15 | PASS | PASS |
| t16 | PASS | PASS |
| t17 | PASS | FAIL (wrong_result_set) |
| t18 | PASS | PASS |
| t19 | FAIL (wrong_result_set) | FAIL (wrong_result_set) |
| t20 | FAIL (sql_error_exhausted) | PASS |
| t21 | FAIL (wrong_result_set) | FAIL (wrong_result_set) |
| t22 | FAIL (wrong_result_set) | FAIL (wrong_result_set) |
| t23 | PASS | PASS |
| t24 | FAIL (sql_error_exhausted) | FAIL (wrong_result_set) |
| t25 | PASS | PASS |
| t26 | FAIL (wrong_result_set) | FAIL (wrong_result_set) |
| t27 | PASS | PASS |
| t28 | PASS | PASS |
| t29 | PASS | PASS |
| t30 | PASS | PASS |
| u01 | PASS | PASS |
| u02 | PASS | PASS |
| u03 | PASS | PASS |
| u04 | PASS | PASS |
| u05 | PASS | PASS |
| u06 | PASS | PASS |
| u07 | PASS | PASS |
| u08 | PASS | PASS |
| u09 | PASS | PASS |
| u10 | PASS | PASS |
| u11 | PASS | PASS |
| u12 | PASS | PASS |
| u13 | PASS | PASS |
| u14 | PASS | PASS |
| u15 | PASS | PASS |
| u16 | PASS | PASS |
| u17 | PASS | PASS |
| u18 | PASS | PASS |
| u19 | PASS | PASS |
| u20 | PASS | PASS |
| u21 | PASS | PASS |
| u22 | PASS | PASS |
| u23 | PASS | PASS |
| u24 | FAIL (sql_error_exhausted) | FAIL (sql_error_exhausted) |
| u25 | PASS | PASS |
| u26 | FAIL (wrong_result_set) | FAIL (wrong_result_set) |
| u27 | PASS | PASS |
| u28 | PASS | PASS |
| u29 | PASS | PASS |
| u30 | FAIL (sql_error_exhausted) | PASS |

## Collection, grading and first-write-wins

Exactly 60 unique C3 question IDs were collected in order t01–t30 then u01–u30. There are no omissions, duplicates or reruns of a recorded outcome. No smoke or model call outside this 60-question batch was run in Phase D. Every raw outcome was saved before any accuracy inspection, scoring or C2 accuracy aggregation.

Only after all 60 records existed did the unchanged eval.grader.grade_run score them. All 60 references passed the current validator. Reference rows came from unmodified agent.mcp_server.execute_select with its read-only, external-access-disabled, memory/thread/timeout/result bounds. No reference exception or alternate execution path was required.

Agent answers were graded from successful recorded MCP submission rows, not by executing or repairing their final SQL offline. The v2 status, submission, truncation and shape checks; case-insensitive pinned names plus injective value matching; unordered duplicate-preserving multiset comparison; and 1e-6 relative floating tolerance with zero implicit absolute tolerance were retained. No v3 positional/ordered rule was substituted. Missing or unsubmitted answers receive no credit.

An exact before-grading raw copy is retained outside the repository. Finalization changes only grading placeholders/metadata in the new C3 file. Every original non-grading field retains its exact value and serialized value, original key order and question order. No generation, terminal status, SQL, answer row, tool trace, lookup return or timestamp was replaced.

Before-grading raw SHA-256: `e91cbf1bb5ebd45f3bf253f6ecfb97d5a325d2d8b3f4222cc987641016601742`.

API retries: **0**. The request ledger contains 294 started requests and 294 received responses, with no transport-error events. SDK automatic retries were disabled. Model turns within an attempt are not retries of recorded question IDs. The initial permission-denied launch occurred before process creation and made no API request; collection began only after explicit destination consent.

## Frozen settings and collection windows

All actual requests specified deepseek-chat and temperature=0, matching the generation parameters recorded in the C2 comparison file. All actual C3 responses reported deepseek-flash; C2 also recorded that response label. Requested aliases, returned model labels, unset optional parameters and current-code provenance are retained separately. No underlying-model identity or provider default is inferred.

C2 collection: 2026-10-25T08:12:16.318214+00:00 through 2026-10-25T08:21:30.820398+00:00.

C3 collection: 2026-10-25T10:32:36.719107+00:00 through 2026-10-25T10:41:54.813820+00:00.

Both batches actually occurred on 2026-10-25 UTC, at different times; a calendar-date difference is not claimed. They were separate collection windows, not contemporaneously interleaved or randomized pairs, so temporal/provider variation remains a confounder.

Every C2 and C3 sent system context has the same SHA-256: `da3c6cc46a602e96e991e86c126f379e616804fae2784f9a439035b4d00541c8`. The frozen reference date is 2026-10-22. C3 reused C2's schema/samples, precomputed date boundaries, lookup behavior, model settings, twelve-tool budget and three-consecutive-SQL-error circuit breaker. The only implemented policy difference remains the approved run_query whitelist-error feedback. The production source and mapping hashes did not change during Phase D.

## Limitations and interpretation

- This is a seen-set regression, with five selected prior failures, not a confirmatory experiment or an unbiased estimate for unseen questions.
- The guardrail was breached. Conclusions about the hypothesis are suspended pending human investigation, despite the circuit-breaker reduction and two revivals. Neither an aggregate tie nor lack of feedback exposure in the two regressions justifies waiving the frozen rule.
- A requested floating alias and the different response-reported label do not pin a provider model version. Separate run times, nondeterministic trajectories and provider variation prevent clean causal attribution to feedback alone.
- Execution recovery is not correctness recovery: t07 and t24 escape the circuit breaker but remain wrong_result_set. T20 revives without any mapped hint. These observations prevent a simple claim that mapped feedback caused all improvements.
- The approved policy intercepts run_query only. U24 fails on submit_answer refusals, which remain raw. The analysis did not broaden interception or repair this trajectory.
- The recovery-step endpoint lacks a frozen operational definition. The disclosed conditional episode-based calculation is descriptive, with unrecovered cases shown explicitly; it is not a new confirmatory metric definition.
- Result-set equality is limited to the frozen snapshot and inherited v2 reference/grader choices. It does not prove universal SQL equivalence, complete date coverage on other datasets, or correctness of prose beyond the submitted rows. No historical errata, aliases, references or grading rules were changed.

## Artifact hashes and preservation

| New artifact | SHA-256 |
|---|---|
| eval/results/runs_v2_c3.jsonl | e7341909c149c79390ee93d9965801cf185b7a69d8d39b5224fecd28357f4451 |

The report hash is supplied separately in the completion message to avoid a self-referential digest. All 67 pre-existing protected-file hashes match the preflight baseline. Selected unchanged frozen hashes:

| Protected artifact | SHA-256 |
|---|---|
| eval/c3_preregister.md | ce58f891aa764dbab6291df67af66b92607bd2b2c8db64ecc6e8b3087bebf744 |
| eval/c3_feasibility.md | 52696a278d6d8bed737abb6df8ded22642965b053568cbaf3fedad6866047042 |
| agent/error_feedback.py | 68fbbafdc74a7902ea4c12a6c92cb525fc6daff5ee50a9a2c4d514df90cdf230 |
| agent/loop.py | 53121bb040921547e87583aa23b234f68bef320a6703f29b0477fc3884c90f93 |
| agent/context.py | 688b90977e398fc34ee1f2e4e89928977e6e6f2ac51bb747cd6c7524e20cbe63 |
| eval/run_experiment.py | d9a2ffc5c419b22d9d47dceefe13bc15ccf6a8005ccfb4400853afd443c79465 |
| agent/mcp_server.py | 3b55d233b1f8f27c1398df53a75065a456456e97219ac2607e9eb03d44b4d41f |
| eval/grader.py | 34fdf04fb0a75836f78a0e2ec4c90fef4d9b7b5f6c4cab730b00abcbe502dd57 |
| eval/glossary.md | 1a2ce44850529108249fe9970803b1745787ecf37c63136a062a11bb808c3d05 |
| eval/github_test_questions_v2.jsonl | 482af433d897f892274b7e5671f8dfc3beeac5ac38b4247c010fa44cd2177fcf |
| data/github.duckdb | 2a063cab4176b97cfd00ea8e92932c64346127ba1da4b120452fb48236c25812 |
| eval/results/runs_v2_c2.jsonl | d357ee0c0693efc8f037dd9693e28d20f25ac1fe34c75ee58d65a93c67a05184 |
| eval/results/runs_v2.jsonl | a6400c28fa4d4e937e492f3ac1fa2d653ebcfa7ddaf0227f826772251af801ae |
| eval/results/runs_v3.jsonl | b318335647b5037ec217adfae08754a0923bc4b4fd0d00b84b8009ad753f85be |
| eval/traces.jsonl | 495bbf2d7fae7750127598fbb1782a45afbc366c718bce9d6260bed20197d616 |

Only eval/results/runs_v2_c3.jsonl and eval/c3_on_v2.md are new repository deliverables. No source, test, dependency, database, glossary, question, feasibility/preregistration document or historical result was modified. No git staging, commit or push occurred. No extra smoke, experiment, model call or score-chasing rerun was performed. Phase D ends with this report; the guardrail-triggered manual investigation remains pending.
