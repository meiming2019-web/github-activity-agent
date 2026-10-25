# C2 on the seen v2 question set: regression validation

**This is a regression on an already-seen question set, not a confirmatory experiment.** The v2 questions have already been used for A/B/C experiments and failure review. This separate C2 run does not replace or enter the frozen v2/v3 results, mechanism probe, or main summary.

## Outcome

| Recorded set | Correct / total |
|---|---:|
| Historical C, frozen runs_v2.jsonl | 50/60 |
| New C2 regression | 47/60 |

C2 corrected three historical C failures and introduced six failures on questions historical C passed. The observed total is three fewer correct answers. This separate-date comparison does not identify a causal treatment effect of boundary injection.

## Smoke, collection, and grading protocol

Exactly one d01 C2 smoke completed before the batch. The actual SDK request contained PRECOMPUTED FROZEN DATE BOUNDARIES and the reference date 2026-10-22. It used four model turns and four tools. Its answer was not graded or written to any repository results/history file; only an external execution receipt was retained.

The batch contains 60 unique question IDs, in exact t01–t30 then u01–u30 order. It began at 2026-10-25T08:12:16.318214+00:00 and ended at 2026-10-25T08:21:30.820398+00:00. There are 55 completed statuses and five error statuses. No recorded attempt was repeated; errors are terminal under first-write-wins.

No grading, historical accuracy inspection, or correctness summary occurred before all 60 raw records were persisted. The collector then retained an exact external before-grading copy. Only after that barrier was the unchanged eval.grader.grade_run invoked for each question. All references passed the existing validator; no trusted-reference bypass or fallback was needed.

The exact v2 path was used: successful recorded MCP submission rows versus reference rows from agent.mcp_server.execute_select. No final answer SQL was reconstructed or re-executed offline. Status/submission/truncation/shape guards, case-insensitive pinned column names, injective value matching, unordered duplicate-preserving multiset comparison, and 1e-6 relative float tolerance with no implicit absolute tolerance all remain unchanged. V3 positional/ordered comparison rules were not substituted.

As explicitly authorized, the new file alone received its final verdict metadata after collection. Every non-grading collection field retains its exact value and serialized field value, original key order and question order; no attempt was replaced. The before-grading file SHA-256 is:

`a8df71e5a8656dee740809c689b7628d51b60ac1e96156e1e03fa722729dd2cb`

Its exact raw copy remains outside the repository. Historical runs.jsonl, runs_v2.jsonl, runs_v3.jsonl, all v3 artifacts and all other protected files remain byte-identical.

## Paired transitions against historical C

| Transition | Count | Complete question IDs |
|---|---:|---|
| C wrong → C2 correct | 3 | u11, u19, u23 |
| C correct → C2 wrong | 6 | t10, t13, t20, t24, u24, u30 |
| Both correct | 44 | t01, t02, t03, t04, t06, t08, t09, t11, t12, t14, t15, t16, t17, t18, t23, t25, t27, t28, t29, t30, u01, u02, u03, u04, u05, u06, u07, u08, u09, u10, u12, u13, u14, u15, u16, u17, u18, u20, u21, u22, u25, u27, u28, u29 |
| Both wrong | 7 | t05, t07, t19, t21, t22, t26, u26 |

All 60 question IDs appear exactly once in this transition partition. These are verdict transitions, not claims that any individual change was caused by C2.

## Historical window audit and paired C2 result

The audit covered every historical C record, including all 50 passes and all 10 failures. Final SQL was available and parsed for 58 records. Historical t07 and t26 have no submitted final SQL, so their window semantics are unavailable rather than presumed correct. Both failed and passing final SQL were checked against the frozen reference windows and calendar expressions.

Among those 58 available historical final queries, one definite event-window deviation was found: u19. Its lower bound omits October 8 and its upper bound extends beyond the frozen reference date. The added upper tail contains no snapshot records, so that component alone is invisible to row-set grading; the complete historical run nevertheless failed. No additional passed historical query with an explicit out-of-snapshot upper bound or other observed date-bound deviation was found. This is an exhaustive inventory of available final SQL in these records, not a universal SQL-equivalence proof.

| Question | Frozen reference event window | Historical C final predicate and verdict | C2 final predicate and verdict |
|---|---|---|---|
| u19 | `[2026-10-08, 2026-10-22)` | `e.created_at >= TIMESTAMP '2026-10-09 00:00:00' AND e.created_at < TIMESTAMP '2026-10-23 00:00:00'`; FAIL (`wrong_result_set`) | `e.created_at >= TIMESTAMP '2026-10-08 00:00:00' AND e.created_at < TIMESTAMP '2026-10-22 00:00:00'`; PASS |

Historical u20 already uses [2026-10-08, 2026-10-22) and passed; the new C2 u20 also uses those boundaries and passes. A shifted u20 predicate observed in a separate probe is not substituted for this frozen historical record. The other two improvements, u11 and u23, had matching historical date boundaries; their improvements therefore are not counted as historical window corrections.

## Post-hoc static audit of all final SQL time predicates

This audit does not change any grader verdict. The table accounts for all 60 historical C and all 60 new C2 records. Predicate blocks below contain the complete extracted date-related comparisons, null guards and calendar generators; repeated identical blocks are referenced rather than duplicated. Expressions are sqlglot-rendered extracts, not rewritten executed SQL. Non-temporal row-rank/count tests are excluded. Repository creation-date conditions are distinct from event-window bounds and are not incorrectly treated as out-of-snapshot event errors.

NO_SQL means no successful submitted final SQL exists. It is an unavailable observation, not evidence of correct date handling. All 55 available C2 final queries parsed; five are unavailable: t07, t20, t24, u24, u30. Historical coverage is 58 parsed and two unavailable. No parse failures were concealed. Calendar-generated per-day bounds were inspected with their date spine. No unresolved ambiguity was assigned a guessed semantic verdict; missing final SQL remains unassessable.

| Question | Historical C block | C2 block | Post-hoc flag |
|---|---|---|---|
| t01 | P01 | P01 | No date-bound deviation observed |
| t02 | P02 | P03 | No date-bound deviation observed |
| t03 | P03 | P03 | No date-bound deviation observed |
| t04 | P04 | P04 | No date-bound deviation observed |
| t05 | P03 | P03 | No date-bound deviation observed |
| t06 | P05 | P06 | No date-bound deviation observed |
| t07 | NO_SQL | NO_SQL | C: unavailable; C2: unavailable |
| t08 | P07 | P08 | No date-bound deviation observed |
| t09 | P03 | P03 | No date-bound deviation observed |
| t10 | P09 | P03 | C2: correct event bounds; zero-day output coverage differs |
| t11 | P10 | P10 | No date-bound deviation observed |
| t12 | P03 | P03 | No date-bound deviation observed |
| t13 | P11 | P11 | No date-bound deviation observed |
| t14 | P11 | P05 | No date-bound deviation observed |
| t15 | P12 | P13 | No date-bound deviation observed |
| t16 | P14 | P15 | No date-bound deviation observed |
| t17 | P11 | P11 | No date-bound deviation observed |
| t18 | P16 | P17 | No date-bound deviation observed |
| t19 | P11 | P18 | No date-bound deviation observed |
| t20 | P19 | NO_SQL | C2: unavailable |
| t21 | P12 | P13 | No date-bound deviation observed |
| t22 | P03 | P12 | No date-bound deviation observed |
| t23 | P12 | P12 | No date-bound deviation observed |
| t24 | P20 | NO_SQL | C2: unavailable |
| t25 | P05 | P05 | No date-bound deviation observed |
| t26 | NO_SQL | P21 | C: unavailable; C2: output-date filter differs; see detail |
| t27 | P22 | P22 | No date-bound deviation observed |
| t28 | P23 | P23 | No date-bound deviation observed |
| t29 | P05 | P05 | No date-bound deviation observed |
| t30 | P03 | P03 | No date-bound deviation observed |
| u01 | P05 | P05 | No date-bound deviation observed |
| u02 | P03 | P03 | No date-bound deviation observed |
| u03 | P04 | P04 | No date-bound deviation observed |
| u04 | P05 | P05 | No date-bound deviation observed |
| u05 | P05 | P05 | No date-bound deviation observed |
| u06 | P05 | P05 | No date-bound deviation observed |
| u07 | P05 | P05 | No date-bound deviation observed |
| u08 | P03 | P02 | No date-bound deviation observed |
| u09 | P13 | P13 | No date-bound deviation observed |
| u10 | P11 | P11 | No date-bound deviation observed |
| u11 | P11 | P11 | No date-bound deviation observed |
| u12 | P24 | P25 | No date-bound deviation observed |
| u13 | P11 | P11 | No date-bound deviation observed |
| u14 | P26 | P27 | No date-bound deviation observed |
| u15 | P11 | P11 | No date-bound deviation observed |
| u16 | P12 | P13 | No date-bound deviation observed |
| u17 | P28 | P22 | No date-bound deviation observed |
| u18 | P12 | P13 | No date-bound deviation observed |
| u19 | P29 | P11 | C: shifted [Oct 9, Oct 23); C2: corrected bounds |
| u20 | P05 | P06 | No date-bound deviation observed |
| u21 | P11 | P18 | No date-bound deviation observed |
| u22 | P30 | P31 | No date-bound deviation observed |
| u23 | P02 | P03 | No date-bound deviation observed |
| u24 | P30 | NO_SQL | C2: unavailable |
| u25 | P05 | P05 | No date-bound deviation observed |
| u26 | P28 | P28 | No date-bound deviation observed |
| u27 | P11 | P05 | No date-bound deviation observed |
| u28 | P05 | P05 | No date-bound deviation observed |
| u29 | P05 | P06 | No date-bound deviation observed |
| u30 | P03 | NO_SQL | C2: unavailable |

No available C2 final predicate contains a 2026-10-23 upper bound. Event date boundaries match the examined frozen windows, including u19. This does not imply that every time-related output requirement was met:

- t10: event filtering is [2026-10-15, 2026-10-22), but the submitted SQL lacks the reference calendar and returns five event-bearing days instead of seven days with zeros. Its prose table does not replace the five submitted rows. Verdict remains wrong_result_set.
- t26: the date spine covers October 8–21 and each event-day join is half-open. The reference SQL additionally has `WHERE activity_date >= DATE '2026-10-10'` before its window function; the submitted C2 SQL has no corresponding output/input restriction and emits 14 rows instead of 12. This is a post-hoc output-date-scope deviation, not a shifted snapshot boundary. Verdict remains wrong_result_set.

Predicate block definitions:

**P01**

```sql
created_at < CAST('2026-10-22 00:00:00' AS TIMESTAMP)
created_at >= CAST('2026-10-21 00:00:00' AS TIMESTAMP)
```

**P02**

```sql
created_at < CAST('2026-10-22' AS TIMESTAMP)
created_at >= CAST('2026-10-15' AS TIMESTAMP)
```

**P03**

```sql
created_at < CAST('2026-10-22 00:00:00' AS TIMESTAMP)
created_at >= CAST('2026-10-15 00:00:00' AS TIMESTAMP)
```

**P04**

```sql
created_at < CAST('2026-10-15 00:00:00' AS TIMESTAMP)
created_at >= CAST('2026-10-08 00:00:00' AS TIMESTAMP)
```

**P05**

```sql
created_at < CAST('2026-10-22 00:00:00' AS TIMESTAMP)
created_at >= CAST('2026-10-08 00:00:00' AS TIMESTAMP)
```

**P06**

```sql
created_at < CAST('2026-10-22' AS TIMESTAMP)
created_at >= CAST('2026-10-08' AS TIMESTAMP)
```

**P07**

```sql
created_at < CAST('2026-10-16 00:00:00' AS TIMESTAMP)
created_at >= CAST('2026-10-15 00:00:00' AS TIMESTAMP)
```

**P08**

```sql
created_at < CAST('2026-10-16' AS TIMESTAMP)
created_at >= CAST('2026-10-15' AS TIMESTAMP)
```

**P09**

```sql
e.created_at < CAST(days.day + INTERVAL '1' DAY AS TIMESTAMP)
e.created_at >= CAST(days.day AS TIMESTAMP)
calendar: GENERATE_SERIES(CAST('2026-10-15' AS DATE), CAST('2026-10-21' AS DATE), INTERVAL '1' DAY)
```

**P10**

```sql
created_at < CAST('2026-10-22 00:00:00' AS TIMESTAMP)
created_at >= CAST('2026-10-19 00:00:00' AS TIMESTAMP)
```

**P11**

```sql
e.created_at < CAST('2026-10-22 00:00:00' AS TIMESTAMP)
e.created_at >= CAST('2026-10-08 00:00:00' AS TIMESTAMP)
```

**P12**

```sql
e.created_at < CAST('2026-10-22 00:00:00' AS TIMESTAMP)
e.created_at >= CAST('2026-10-15 00:00:00' AS TIMESTAMP)
```

**P13**

```sql
e.created_at < CAST('2026-10-22' AS TIMESTAMP)
e.created_at >= CAST('2026-10-15' AS TIMESTAMP)
```

**P14**

```sql
e.created_at < CAST('2026-10-22 00:00:00' AS TIMESTAMP)
e.created_at >= CAST('2026-10-08 00:00:00' AS TIMESTAMP)
r.created_at >= CAST('2022-01-01 00:00:00' AS TIMESTAMP)
```

**P15**

```sql
e.created_at < CAST('2026-10-22' AS TIMESTAMP)
e.created_at >= CAST('2026-10-08' AS TIMESTAMP)
r.created_at >= CAST('2022-01-01' AS TIMESTAMP)
```

**P16**

```sql
e.created_at < CAST('2026-10-22 00:00:00' AS TIMESTAMP)
e.created_at >= CAST('2026-10-15 00:00:00' AS TIMESTAMP)
r.created_at < CAST('2020-01-01 00:00:00' AS TIMESTAMP)
```

**P17**

```sql
e.created_at < CAST('2026-10-22' AS TIMESTAMP)
e.created_at >= CAST('2026-10-15' AS TIMESTAMP)
r.created_at < CAST('2020-01-01' AS TIMESTAMP)
```

**P18**

```sql
e.created_at < CAST('2026-10-22' AS TIMESTAMP)
e.created_at >= CAST('2026-10-08' AS TIMESTAMP)
```

**P19**

```sql
e.created_at < CAST('2026-10-22 00:00:00' AS TIMESTAMP)
e.created_at >= CAST('2026-10-17 00:00:00' AS TIMESTAMP)
```

**P20**

```sql
created_at < CAST('2026-10-22 00:00:00' AS TIMESTAMP)
created_at >= CAST('2026-10-08 00:00:00' AS TIMESTAMP)
calendar: GENERATE_SERIES(CAST('2026-10-08' AS DATE), CAST('2026-10-21' AS DATE), INTERVAL '1' DAY)
```

**P21**

```sql
e.created_at < days.day + INTERVAL '1' DAY
e.created_at >= days.day
calendar: GENERATE_SERIES(CAST('2026-10-08' AS DATE), CAST('2026-10-21' AS DATE), INTERVAL '1' DAY)
```

**P22**

```sql
created_at < CAST('2026-10-15' AS TIMESTAMP)
created_at < CAST('2026-10-22' AS TIMESTAMP)
created_at >= CAST('2026-10-08' AS TIMESTAMP)
created_at >= CAST('2026-10-15' AS TIMESTAMP)
```

**P23**

```sql
created_at < CAST('2026-10-22 00:00:00' AS TIMESTAMP)
created_at >= CAST('2026-10-15 00:00:00' AS TIMESTAMP)
e.created_at < CAST('2026-10-22 00:00:00' AS TIMESTAMP)
e.created_at >= CAST('2026-10-15 00:00:00' AS TIMESTAMP)
```

**P24**

```sql
e.created_at < CAST('2026-10-22 00:00:00' AS TIMESTAMP)
e.created_at >= CAST('2026-10-15 00:00:00' AS TIMESTAMP)
r.created_at < CAST('2018-01-01 00:00:00' AS TIMESTAMP)
```

**P25**

```sql
e.created_at < CAST('2026-10-22' AS TIMESTAMP)
e.created_at >= CAST('2026-10-15' AS TIMESTAMP)
r.created_at < CAST('2018-01-01' AS TIMESTAMP)
```

**P26**

```sql
NOT r.created_at IS NULL
created_at < CAST('2026-10-22 00:00:00' AS TIMESTAMP)
created_at >= CAST('2026-10-08 00:00:00' AS TIMESTAMP)
r.created_at < CAST('2016-01-01' AS TIMESTAMP)
r.created_at < CAST('2021-01-01' AS TIMESTAMP)
```

**P27**

```sql
NOT created_at IS NULL
created_at < CAST('2016-01-01' AS TIMESTAMP)
created_at < CAST('2021-01-01' AS TIMESTAMP)
created_at < CAST('2026-10-22' AS TIMESTAMP)
created_at >= CAST('2026-10-08' AS TIMESTAMP)
```

**P28**

```sql
created_at < CAST('2026-10-15 00:00:00' AS TIMESTAMP)
created_at < CAST('2026-10-22 00:00:00' AS TIMESTAMP)
created_at >= CAST('2026-10-08 00:00:00' AS TIMESTAMP)
created_at >= CAST('2026-10-15 00:00:00' AS TIMESTAMP)
```

**P29**

```sql
e.created_at < CAST('2026-10-23 00:00:00' AS TIMESTAMP)
e.created_at >= CAST('2026-10-09 00:00:00' AS TIMESTAMP)
```

**P30**

```sql
created_at < CAST('2026-10-22 00:00:00' AS TIMESTAMP)
created_at >= CAST('2026-10-08 00:00:00' AS TIMESTAMP)
x.day = d.day
calendar: GENERATE_SERIES(CAST('2026-10-08' AS DATE), CAST('2026-10-21' AS DATE), INTERVAL '1' DAY)
```

**P31**

```sql
created_at < CAST('2026-10-22' AS TIMESTAMP)
created_at >= CAST('2026-10-08' AS TIMESTAMP)
daily.day = d.day
calendar: GENERATE_SERIES(CAST('2026-10-08' AS TIMESTAMP), CAST('2026-10-21' AS TIMESTAMP), INTERVAL '1' DAY)
```

## Cost comparison

These totals cover the 60 question attempts only, including terminal failures. Smoke costs are excluded. Tool counts use the unchanged loop counter and exclude static-context assembly calls, as in the existing experiment path.

| Measure | Historical C | C2 regression |
|---|---:|---:|
| Tool-call count | 319 | 319 |
| Glossary retrieval calls | UNAVAILABLE | 73 |
| Prompt tokens | 3947586 | 3793981 |
| Completion tokens | 67291 | 63755 |
| Total tokens | 4014877 | 3857736 |

All 60 historical C records lack tool_names, so historical glossary counts cannot be recovered. UNAVAILABLE is not zero and is not inferred from total tools or substituted from the mechanism probe. The new C2 traces record 73 named lookup calls and 73 received returns, including full arguments and exact returned sections.

## Historical failure buckets, recounted from all 180 frozen records

| Frozen fail_category | Count |
|---|---:|
| wrong_result_set | 29 |
| sql_error_exhausted | 5 |
| no_submission | 2 |
| missing_columns | 2 |
| Total failed | 38 |

These counts were recomputed from runs_v2.jsonl after the collection barrier, not copied from README. The new C2 file has eight wrong_result_set and five sql_error_exhausted decisions. The five error runs are t07, t20, t24, u24 and u30; each stopped after three consecutive SQL errors and has no submitted final SQL. They receive no offline rescue from intermediate attempts.

## Model, retries, and provenance

Every observed request specified deepseek-chat and temperature=0. Every observed batch response reported deepseek-flash; response_models preserves those values separately from the requested alias. No equivalence or underlying-model identity is assumed. Other optional generation parameters were not supplied and provider defaults are not claimed to be pinned.

Historical v2 records omit generation metadata. The original raw-run artifact commits 70842e457a5392cf8c4f52a0183861dbb46a04ae and 0f17c293e7cef5ae9585d776c696ae16ff980078 predate the first tracked agent/loop.py at cbe87dd021634d8361b1f8479a18bad711ae10af. Tracked deepseek-chat / temperature=0 settings remain unchanged through current HEAD 1d25acebf72c57b18979bfc5f28caaea8fd00f11, but production-time uncommitted state cannot be established. Each new record carries current-code provenance and explicitly marks historical parameter consistency unverified.

API retries: 0. SDK automatic retries were disabled. The temporary ledger contains 278 batch requests and 278 responses, plus four smoke requests and four responses. No transport-error events occurred. Model turns are not reruns of recorded question IDs. No model calls were made during grading or analysis.

## Limitations

- The 60 questions were already seen in experiments and review. This is regression validation, not a new frozen confirmatory test or an unbiased accuracy estimate for unseen questions.
- Historical C and current C2 were run on different dates, not as contemporaneous randomized pairs. Provider variation, a floating requested alias and absent historical generation metadata prevent a causal interpretation of the three improvements, six regressions or aggregate score difference.
- Requested deepseek-chat and response-reported deepseek-flash differ. The underlying reason and historical equivalence are unknown; the mismatch is disclosed rather than normalized away.
- Row-set grading is insensitive to predicates over empty parts of the snapshot. A correct returned row set is not proof that every explicit boundary is semantically correct on other data. Conversely, calendar/output-date requirements can fail even when event filtering has correct boundaries.
- Static extraction is an inventory and focused semantic review, not a general SQL-equivalence solver. No-submission records provide no final predicate to assess. Catalogue creation-date filters and event-date windows are kept separate.
- Existing v2 reference/grading choices remain frozen, including the disclosed t21 reference/grading mismatch and t22 ambiguity. No answer key, tolerance, column mapping, failure status or verdict was repaired in this regression.
- Historical glossary lookup counts are unavailable. No probe-derived surrogate is presented as historical C instrumentation.

## Integrity and deliverables

Final graded runs_v2_c2.jsonl SHA-256: `d357ee0c0693efc8f037dd9693e28d20f25ac1fe34c75ee58d65a93c67a05184`.

Before-grading raw SHA-256: `a8df71e5a8656dee740809c689b7628d51b60ac1e96156e1e03fa722729dd2cb`. An exact external raw copy is retained for verification.

All 61 protected pre-existing files remain byte-identical, including every earlier results file, v3 artifact, question set, glossary, MCP server, grader, loop, README, dependency file and historical trace. Key frozen hashes:

| Protected artifact | SHA-256 |
|---|---|
| eval/results/runs_v2.jsonl | a6400c28fa4d4e937e492f3ac1fa2d653ebcfa7ddaf0227f826772251af801ae |
| eval/results/runs_v3.jsonl | b318335647b5037ec217adfae08754a0923bc4b4fd0d00b84b8009ad753f85be |
| eval/v3_classification.jsonl | 9723d55d046bec920bbea16e91648a20e0e25e2de2429fb533ef080c41000677 |
| eval/v3_report.md | b2e52a34ed6ea7ca4652962d8a03ed94ecb0ceef03b0c8bfb3b362b4a1489694 |
| eval/github_test_questions_v2.jsonl | 482af433d897f892274b7e5671f8dfc3beeac5ac38b4247c010fa44cd2177fcf |
| eval/glossary.md | 1a2ce44850529108249fe9970803b1745787ecf37c63136a062a11bb808c3d05 |
| eval/grader.py | 34fdf04fb0a75836f78a0e2ec4c90fef4d9b7b5f6c4cab730b00abcbe502dd57 |
| agent/loop.py | 78b02e5a4235581fd0f93f5df5adab54c8a1b6b5b6abc78ab0d3e20c9da09952 |
| data/github.duckdb | 2a063cab4176b97cfd00ea8e92932c64346127ba1da4b120452fb48236c25812 |

Only eval/results/runs_v2_c2.jsonl and eval/c2_on_v2_regression.md are new repository deliverables. No source, historical record, question, main summary, dependency or credential configuration was changed. No git staging, commit or push was performed. No extra model calls or experiments were added.
