# v4 Phase D analysis report

Status: offline scoring completed under the frozen primary rules plus the explicitly labeled post-registration adjudications below. No model, API, SQL execution, re-run, or frozen-file modification is part of this analysis.

## Frozen inputs and scoring integrity

| Input | Verified SHA-256 |
| --- | --- |
| data/github.duckdb | 2a063cab4176b97cfd00ea8e92932c64346127ba1da4b120452fb48236c25812 |
| eval/gen_v4_questions.py | 318aee7fb68c6a660b0598ea77710f3ab7ecdcb66b1b8d6ce90a28076fe6b498 |
| eval/results/runs_v4.jsonl | b08c2881f8253d8d1e7d65b849f4fcd76499a2b0d467afe0a7f74140e7832240 |
| eval/results/runs_v4_pass2.jsonl | 8ff2597534c7459349107c0a55e8819f9c3b96f7a31700083ddddd59c44156a3 |
| eval/run_v4.py | 80d0f9f67d427842ef3b9f9e6e220eedcc11279ef63307cfb0a61453f11b7a51 |
| eval/v4_boundary_rubric.md | 71d2108cdbb2419e1ba5e1676162b27f56b93295bc87401cd01251dd954e411d |
| eval/v4_preregister.md | 8aeba1dc302b92e9331a3bf0f28c8a451daa415be34ca4dd2aee6c88d5103ab5 |
| eval/v4_questions.jsonl | 829ec0475c1ba1c090c8b1926221124df092af8b35b81ccc2a0a92e1fa897dc1 |
| eval/v4_schedule.jsonl | 1a9be6c1571f5aceb917fdcc88ff3a66dc5bebcfa9b1540de6ea23620494234e |
| eval/v4_sql_bounds.py | 331fa061ba46bb4cf53c52102eeddd3d0e423a557b3328469e0edbc34f32805f |

All 300 per-question snapshot hashes match the actual database bytes. Both frozen result universes are complete (900 pass-1, 180 pass-2 unique identities). No reference SQL is executed: gold rows come only from the question file. No rejected/tool result is promoted to a gold or final answer.

The frozen grader.same_multiset/same_value functions are reused. Its case-insensitive name pinning, unused-column permutation (at most four unpinned columns), extra-column treatment and duplicate-aware tolerant matching are retained. Only its reference-execution prefix is replaced with precomputed reference_columns/reference_rows. The legacy grade_run function itself is never called. A truncated answer is counted under wrong_result_set; its truncation count is separately reported. The grader budget_exceeded branch is labeled breaker; three-consecutive-SQL-error termination retains sql_error_exhausted. No rejected submission is treated as a final SQL.

## Analysis definitions recorded before effects

Exact two-sided McNemar uses the conditional binomial distribution with p=1 for zero discordances. In all tables, left-only favors the first-named configuration and right-only favors the second. Endpoint 1 excludes a pair if either configuration lacks committed SQL; separate marginal missing counts do not create separate paired denominators. Unknown parser classifications are not correct and are disclosed separately. The frozen parser is not repaired or reinterpreted.

Bootstrap implementation choices were recorded before effects: seed 42025; 10000 family-resampling replicates; empirical percentile endpoints ceil(0.025B), ceil(0.975B). These are implementation details, not preregistered values. The later human adjudication selects the estimand/weighting below; those choices were not specified by the original preregistration.

The pre-effect audit identified missing operational definitions; descriptive results were then reported without selecting them. The user subsequently supplied the following decisions after viewing that initial report. They are post-registration adjudications, not retroactive preregistration content.

## Post-registration adjudications (2026-10-25)

E2: the first recorded run_query after the first documented whitelist rejection determines recovery; no following run_query or unidentifiable outcome is failure symmetrically. Counts and IDs below distinguish these conservative failures from observed whitelist rejections. Other tools, including submit_answer, cannot replace that next run_query.

Flip downgrade: use each endpoint binary; sum flips over the two compared configurations and divide by common eligible questions, NOT twice that count. This quantity has range [0,2] (0% to 200%). Compare it with half the pass-1 absolute net discordance |b-c|/n. E1 requires both configs evaluable in both passes; E2 additionally requires both configs to have rejection eligibility in both passes. Eligibility changes are descriptive only. Zero effect implies zero threshold, so an observed zero flip rate still meets the literal >= rule; an empty denominator is not estimable and does not license validation.

Family bootstrap: draw 11 family labels with replacement per replicate from the full 11-family universe, 10000 times. Include all eligible questions from each selected family, with equal question weights and family multiplicity. Project each draw onto the relevant endpoint or full-set paired population; no eligible rows means an undefined replicate, counted and omitted from numerical percentiles. Use |b-c|/n consistently with the adjudicated absolute net effect; signed differences remain visible separately. Percentile order statistics use the number of valid replicates. No family without endpoint exposure is treated as a negative observation.

Prefix-match denominator: all 300 paired C2.1/C3.1 traces. Compare exact tool names and argument objects in trace order, ignoring random call IDs, outputs and timing; do not normalize SQL or reconstruct contexts. Align positions and take the earliest first-whitelist-rejection index across the pair as the boundary, excluding that rejection call itself (strictly before). Both traces must reach the cutoff and all preceding actions must match. If neither rejects, require full-sequence equality. Empty prefixes are explicitly disclosed.

v4_138: retain the frozen main classification. A separately labeled, human-authorized sensitivity sets its C boundary judgment to correct, without changing the parser, files or main analysis. Message-level token cost and runtime actual injection text remain unavailable.

## Endpoint 1: window stratum, C versus C2.1

| Paired n | Both correct | C only | C2.1 only | Neither correct | Joint exclusions | Exact two-sided p | C2.1 minus C |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 179 | 170 | 0 | 9 | 0 | 1 | 0.00390625 | 0.05027932960893855 |

| Config | Window questions | No committed SQL | Correct / submitted | Parser categories |
| --- | --- | --- | --- | --- |
| C | 180 | 1 | 170/179 (94.97%) | {"both_wrong": 8, "correct": 170, "unparseable": 1} |
| C2.1 | 180 | 0 | 180/180 (100.00%) | {"correct": 180} |
| C3.1 | 180 | 0 | 180/180 (100.00%) | {"correct": 180} |

| Family | Paired n | C only | C2.1 only | Joint exclusions |
| --- | --- | --- | --- | --- |
| window_active_contributors | 59 | 0 | 5 | 1 |
| window_collaboration_events | 60 | 0 | 2 | 0 |
| window_new_stars | 60 | 0 | 2 | 0 |

Non-significance is not evidence against the mechanism. The preregistered power statement anticipates low power if the true baseline error rate is at most 5%; the observed small error count is not a proof that the true rate meets that condition. Discordant counts are retained regardless of significance. Family clustering and only three window families limit independent information; missing SQL is not a correct window.

Visible frozen-parser limitation: v4_138/C is unparseable because the non-events py CTE is reused. Its sole events source has literal predicates >= 2026-10-08 and < 2026-10-15, matching its authorized interval. The locked binary still counts this as not classified correct. The nine Endpoint-1 discordances comprise eight both_wrong classifications and one unparseable classification; they must not be described as nine independently established semantic boundary errors. No repaired verdict is substituted into the main analysis; the explicitly authorized sensitivity appears separately below.

## Endpoint 2: advanced stratum, C2.1 versus C3.1

Fixed-sequence gate open: True. Both configurations have a documented whitelist rejection on 27 questions; paired binary outcomes under adjudication: 27; remaining invalid pair exclusions: 0.

| Both recover | C2.1 only | C3.1 only | Neither recover | Exact p (gate-eligible only) |
| --- | --- | --- | --- | --- |
| 0 | 0 | 2 | 25 | 0.5 |

| Config | Documented rejection set | Observed next-query pass | Conservative failures | Unclassified outcomes | Recovery / full rejection set | Reasons (all advanced) |
| --- | --- | --- | --- | --- | --- | --- |
| C | 27 | 1 | 26 | 0 | 1/27 (3.70%) | {"no_next_run_query": 14, "no_rejection": 63, "rejected": 12, "passed": 1} |
| C2.1 | 34 | 1 | 33 | 0 | 1/34 (2.94%) | {"no_next_run_query": 27, "no_rejection": 56, "rejected": 6, "passed": 1} |
| C3.1 | 35 | 2 | 33 | 0 | 2/35 (5.71%) | {"no_rejection": 55, "no_next_run_query": 28, "rejected": 4, "unknown": 1, "passed": 2} |

Rejections require exact frozen whitelist diagnostics (including original raw_error for feedback runs). A generic SQL/transport error does not prove rejection or whitelist passage. The next recorded run_query is used, skipping metadata/glossary tools and submit_answer. Undispatched or unidentified next-call results are conservative failures, not proven whitelist rejections. An unknown earlier SQL error leaves first-rejection identity unproven and is conservatively failed. No-next and unknown-next reason counts and IDs are retained below. No Endpoint-2 confirmatory p is reported when Endpoint 1 fails its gate.

## Control guardrail

| Pair | n | Left only | Right only | Exact p |
| --- | --- | --- | --- | --- |
| C vs C2.1 | 30 | 0 | 0 | 1 |
| C vs C3.1 | 30 | 0 | 0 | 1 |
| C2.1 vs C3.1 | 30 | 0 | 0 | 1 |

Guardrail triggered: False. No pairwise control comparison reaches p<0.05; this does not prove absence of side effects.

| Config | Controls | No SQL | Extra time filter true | False | Unknown |
| --- | --- | --- | --- | --- | --- |
| C | 30 | 0 | 0 | 30 | 0 |
| C2.1 | 30 | 0 | 0 | 30 | 0 |
| C3.1 | 30 | 0 | 0 | 30 | 0 |

Control primary classification no_window_predicate is not evidence of no added time filter; the separate observed_time_filter field is used. Unknown detection and absent SQL are reported separately.

## Whole-question accuracy and error taxonomy

| Stratum | n | C | C2.1 | C3.1 |
| --- | --- | --- | --- | --- |
| window | 180 | 172/180 (95.56%) | 179/180 (99.44%) | 178/180 (98.89%) |
| advanced targeted | 60 | 36/60 (60.00%) | 30/60 (50.00%) | 35/60 (58.33%) |
| advanced non-targeted | 30 | 29/30 (96.67%) | 30/30 (100.00%) | 30/30 (100.00%) |
| control | 30 | 30/30 (100.00%) | 30/30 (100.00%) | 30/30 (100.00%) |
| all | 300 | 267/300 (89.00%) | 269/300 (89.67%) | 273/300 (91.00%) |

| Family | n | C | C2.1 | C3.1 |
| --- | --- | --- | --- | --- |
| catalog_lookup | 15 | 15/15 (100.00%) | 15/15 (100.00%) | 15/15 (100.00%) |
| consecutive_day_runs | 15 | 15/15 (100.00%) | 15/15 (100.00%) | 15/15 (100.00%) |
| daily_trend | 15 | 9/15 (60.00%) | 9/15 (60.00%) | 11/15 (73.33%) |
| day_of_week | 15 | 3/15 (20.00%) | 0/15 (0.00%) | 4/15 (26.67%) |
| day_over_day | 15 | 11/15 (73.33%) | 10/15 (66.67%) | 8/15 (53.33%) |
| language_composition | 15 | 15/15 (100.00%) | 15/15 (100.00%) | 15/15 (100.00%) |
| running_total | 15 | 13/15 (86.67%) | 11/15 (73.33%) | 12/15 (80.00%) |
| session_segmentation | 15 | 14/15 (93.33%) | 15/15 (100.00%) | 15/15 (100.00%) |
| window_active_contributors | 60 | 54/60 (90.00%) | 59/60 (98.33%) | 58/60 (96.67%) |
| window_collaboration_events | 60 | 58/60 (96.67%) | 60/60 (100.00%) | 60/60 (100.00%) |
| window_new_stars | 60 | 60/60 (100.00%) | 60/60 (100.00%) | 60/60 (100.00%) |

| Stratum | Config | wrong_result_set | sql_error_exhausted | no_submission | missing_columns | breaker | Truncated (overlap) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| window | C | 7 | 0 | 0 | 0 | 1 | 0 |
| window | C2.1 | 1 | 0 | 0 | 0 | 0 | 0 |
| window | C3.1 | 2 | 0 | 0 | 0 | 0 | 0 |
| advanced targeted | C | 5 | 18 | 0 | 0 | 1 | 0 |
| advanced targeted | C2.1 | 2 | 28 | 0 | 0 | 0 | 0 |
| advanced targeted | C3.1 | 2 | 23 | 0 | 0 | 0 | 0 |
| advanced non-targeted | C | 0 | 1 | 0 | 0 | 0 | 0 |
| advanced non-targeted | C2.1 | 0 | 0 | 0 | 0 | 0 | 0 |
| advanced non-targeted | C3.1 | 0 | 0 | 0 | 0 | 0 | 0 |
| control | C | 0 | 0 | 0 | 0 | 0 | 0 |
| control | C2.1 | 0 | 0 | 0 | 0 | 0 | 0 |
| control | C3.1 | 0 | 0 | 0 | 0 | 0 | 0 |
| all | C | 12 | 19 | 0 | 0 | 2 | 0 |
| all | C2.1 | 3 | 28 | 0 | 0 | 0 | 0 |
| all | C3.1 | 4 | 23 | 0 | 0 | 0 | 0 |

Whole-question differences are descriptive; no total-score superiority claim is licensed. Taxonomy is mutually exclusive; truncation is an overlapping diagnostic. SQL-error exhaustion and tool-budget breakers remain separate rather than being silently merged.

## First submission, empty/zero outputs, and trajectory prefixes

| Stratum | Config | First submitted SQL correct / known | No attempt or unavailable | Correct after failed first submit | Wrong answers | Empty / wrong | All numeric zero / wrong |
| --- | --- | --- | --- | --- | --- | --- | --- |
| window | C | 172/179 (96.09%) | 1 | 0 | 8 | 0/8 (0.00%) | 0/8 (0.00%) |
| window | C2.1 | 179/180 (99.44%) | 0 | 0 | 1 | 0/1 (0.00%) | 0/1 (0.00%) |
| window | C3.1 | 178/180 (98.89%) | 0 | 0 | 2 | 0/2 (0.00%) | 0/2 (0.00%) |
| advanced targeted | C | 34/53 (64.15%) | 7 | 2 | 24 | 0/24 (0.00%) | 0/24 (0.00%) |
| advanced targeted | C2.1 | 27/55 (49.09%) | 5 | 3 | 30 | 0/30 (0.00%) | 0/30 (0.00%) |
| advanced targeted | C3.1 | 26/58 (44.83%) | 2 | 9 | 25 | 0/25 (0.00%) | 0/25 (0.00%) |
| advanced non-targeted | C | 29/29 (100.00%) | 1 | 0 | 1 | 0/1 (0.00%) | 0/1 (0.00%) |
| advanced non-targeted | C2.1 | 30/30 (100.00%) | 0 | 0 | 0 | 0/0 (not estimable) | 0/0 (not estimable) |
| advanced non-targeted | C3.1 | 30/30 (100.00%) | 0 | 0 | 0 | 0/0 (not estimable) | 0/0 (not estimable) |
| control | C | 30/30 (100.00%) | 0 | 0 | 0 | 0/0 (not estimable) | 0/0 (not estimable) |
| control | C2.1 | 30/30 (100.00%) | 0 | 0 | 0 | 0/0 (not estimable) | 0/0 (not estimable) |
| control | C3.1 | 30/30 (100.00%) | 0 | 0 | 0 | 0/0 (not estimable) | 0/0 (not estimable) |
| all | C | 265/291 (91.07%) | 9 | 2 | 33 | 0/33 (0.00%) | 0/33 (0.00%) |
| all | C2.1 | 266/295 (90.17%) | 5 | 3 | 31 | 0/31 (0.00%) | 0/31 (0.00%) |
| all | C3.1 | 264/298 (88.59%) | 2 | 9 | 27 | 0/27 (0.00%) | 0/27 (0.00%) |

First-attempt means the first dispatched submit_answer, as stated in Section 7, not the first exploratory run_query. Its success is measurable from stored final rows only when it is the committed successful submission; a failed submission is not a row-set success. Rejected earlier SQL is never executed offline. Empty means []; zero means at least one numeric cell and every numeric cell zero (categorical/date cells ignored). These are observable output flags, not inferred intent or silent semantic correctness.

Adjudicated prefix-match: 94/300 (31.33%); paired trace denominator 300 (required formal universe: 300). No rejection in either trace: 73/250 fully identical. At least one rejection: 21/50 pre-rejection prefixes identical. Empty pre-rejection prefixes: 0.

## Distractor probes and parser observability

| Stratum | Frozen distractor probes | Mis-append | IDs |
| --- | --- | --- | --- |
| window | 60 | 0 | None |
| advanced_sql | 30 | 0 | None |
| control | 10 | 0 | None |

These probes were captured offline during generation. Runtime traces do not retain the actual injected context; runtime mis-append count is not separately estimable. No post-run reconstruction is substituted for that evidence. Controls have no operative window despite decorative dates.

| Config | Stratum | Primary parser classes (submitted only) | Scaffold end flags |
| --- | --- | --- | --- |
| C | window | {"correct": 170, "both_wrong": 8, "unparseable": 1} | {"not_present": 179} |
| C | advanced_sql | {"unparseable": 52, "correct": 18} | {"not_present": 67, "correct": 2, "unparseable": 1} |
| C | control | {"no_window_predicate": 30} | {"not_present": 30} |
| C2.1 | window | {"correct": 180} | {"not_present": 180} |
| C2.1 | advanced_sql | {"unparseable": 46, "correct": 16} | {"not_present": 62} |
| C2.1 | control | {"no_window_predicate": 30} | {"not_present": 30} |
| C3.1 | window | {"correct": 180} | {"not_present": 180} |
| C3.1 | advanced_sql | {"unparseable": 51, "correct": 16} | {"not_present": 66, "correct": 1} |
| C3.1 | control | {"no_window_predicate": 30} | {"not_present": 30} |

| Frozen parser reason (no correction applied) | Count |
| --- | --- |
| Outer-join temporal ON is not a row restriction | 12 |
| Reused source scope requires branch-sensitive lineage | 1 |
| Scalar/correlated subqueries or set operations are unsupported | 2 |
| Temporal predicate above a non-row-preserving projection | 91 |
| Unsupported transformation of created_at | 44 |

Unparseable does not prove a semantically wrong window, and scaffold flags cannot override the primary classification. The parser intentionally rejects some valid query forms; this report preserves that limitation. Additional visible parser defects, if found, must be disclosed without score repair.

## Cost and model fingerprints

| Stratum | Config | n | Prompt tokens | Completion tokens | Tool calls | Mean prompt | Mean completion | Mean tools |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| window | C | 180 | 11205781 | 150679 | 899 | 62254.339 | 837.106 | 4.994 |
| window | C2.1 | 180 | 10064311 | 130629 | 780 | 55912.839 | 725.717 | 4.333 |
| window | C3.1 | 180 | 10068477 | 132479 | 790 | 55935.983 | 735.994 | 4.389 |
| advanced targeted | C | 60 | 4093053 | 69128 | 327 | 68217.55 | 1152.133 | 5.45 |
| advanced targeted | C2.1 | 60 | 3908615 | 60445 | 326 | 65143.583 | 1007.417 | 5.433 |
| advanced targeted | C3.1 | 60 | 4192490 | 67375 | 339 | 69874.833 | 1122.917 | 5.65 |
| advanced non-targeted | C | 30 | 1869596 | 24898 | 148 | 62319.867 | 829.933 | 4.933 |
| advanced non-targeted | C2.1 | 30 | 1892833 | 25329 | 152 | 63094.433 | 844.3 | 5.067 |
| advanced non-targeted | C3.1 | 30 | 1882380 | 24744 | 155 | 62746.0 | 824.8 | 5.167 |
| control | C | 30 | 1353884 | 8192 | 88 | 45129.467 | 273.067 | 2.933 |
| control | C2.1 | 30 | 1349994 | 8514 | 85 | 44999.8 | 283.8 | 2.833 |
| control | C3.1 | 30 | 1350328 | 8391 | 88 | 45010.933 | 279.7 | 2.933 |
| all | C | 300 | 18522314 | 252897 | 1462 | 61741.047 | 842.99 | 4.873 |
| all | C2.1 | 300 | 17215753 | 224917 | 1343 | 57385.843 | 749.723 | 4.477 |
| all | C3.1 | 300 | 17493675 | 232989 | 1372 | 58312.25 | 776.63 | 4.573 |

Token counts are observed aggregate usage, not money estimates. Tokens of the injected line and feedback messages are not separately recorded; repeated prompt accumulation, variable responses and tokenizer identity prevent exact isolation. No causal cost attribution is inferred from total differences.

Pass 1 response_models: `{'deepseek-flash': 3972}`.
Pass 2 response_models: `{'deepseek-flash': 785}`.

## Pass-2 transitions and downgrade status

| Binary | Config | Sample eligible by stratum | Jointly evaluable | Pass1 success to failure | Pass1 failure to success | Unavailable pairs | Observed flips / evaluable |
| --- | --- | --- | --- | --- | --- | --- | --- |
| whole_question | C | 60 | 60 | 2 | 2 | 0 | 4/60 (6.67%) |
| whole_question | C2.1 | 60 | 60 | 1 | 1 | 0 | 2/60 (3.33%) |
| whole_question | C3.1 | 60 | 60 | 3 | 1 | 0 | 4/60 (6.67%) |
| boundary | C | 41 | 40 | 1 | 0 | 1 | 1/40 (2.50%) |
| boundary | C2.1 | 41 | 41 | 0 | 0 | 0 | 0/41 (0.00%) |
| boundary | C3.1 | 41 | 41 | 0 | 0 | 0 | 0/41 (0.00%) |
| recovery | C | 15 | 2 | 0 | 0 | 13 | 0/2 (0.00%) |
| recovery | C2.1 | 15 | 4 | 0 | 0 | 11 | 0/4 (0.00%) |
| recovery | C3.1 | 15 | 4 | 0 | 0 | 11 | 0/4 (0.00%) |

Whole-question flips remain descriptive. Endpoint-specific combined flips and exact eligible denominators determine the adjudicated downgrade below.

| Endpoint | Pass2 stratum n | Common eligible n | Flips by config | Combined flips | Flips/n | Pass1 \|b-c\|/n | 50% threshold | Exploratory |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| endpoint1 | 41 | 40 | {"C": 1, "C2.1": 0} | 1 | 0.025 | 0.05027932960893855 | 0.025139664804469275 | False |
| endpoint2 | 15 | 3 | {"C2.1": 0, "C3.1": 0} | 0 | 0.0 | 0.07407407407407407 | 0.037037037037037035 | False |

endpoint1 eligibility: lost=[]; gained=[]; neither pass eligible=[]; missing/invalid judgment=['v4_177']. Common eligible IDs: ['v4_007', 'v4_010', 'v4_013', 'v4_014', 'v4_020', 'v4_024', 'v4_025', 'v4_026', 'v4_027', 'v4_032', 'v4_040', 'v4_041', 'v4_043', 'v4_046', 'v4_049', 'v4_057', 'v4_062', 'v4_066', 'v4_075', 'v4_087', 'v4_088', 'v4_089', 'v4_102', 'v4_103', 'v4_111', 'v4_112', 'v4_113', 'v4_121', 'v4_125', 'v4_131', 'v4_133', 'v4_144', 'v4_151', 'v4_154', 'v4_157', 'v4_167', 'v4_169', 'v4_171', 'v4_176', 'v4_179'].
endpoint2 eligibility: lost=['v4_216']; gained=['v4_201']; neither pass eligible=['v4_182', 'v4_200', 'v4_225', 'v4_242', 'v4_243', 'v4_251', 'v4_252', 'v4_262', 'v4_264', 'v4_269']; missing/invalid judgment=[]. Common eligible IDs: ['v4_188', 'v4_204', 'v4_237'].

## Conservative E2 failures: counts and identities

| Pass | Config | Reason | Full rejection-set count | IDs | In E2 dual-rejection subset | Subset IDs |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | C | no_next_run_query | 14 | v4_181, v4_185, v4_186, v4_190, v4_217, v4_226, v4_227, v4_231, v4_233, v4_234, v4_237, v4_238, v4_239, v4_240 | 10 | v4_185, v4_226, v4_227, v4_231, v4_233, v4_234, v4_237, v4_238, v4_239, v4_240 |
| 1 | C | unknown | 0 | None | 0 | None |
| 1 | C | not_dispatched | 0 | None | 0 | None |
| 1 | C | first_rejection_not_proven | 0 | None | 0 | None |
| 1 | C2.1 | no_next_run_query | 27 | v4_181, v4_183, v4_185, v4_188, v4_192, v4_202, v4_203, v4_204, v4_205, v4_214, v4_215, v4_216, v4_218, v4_219, v4_220, v4_221, v4_226, v4_228, v4_230, v4_232, v4_233, v4_234, v4_235, v4_236, v4_237, v4_238, v4_239 | 22 | v4_185, v4_188, v4_192, v4_202, v4_204, v4_214, v4_215, v4_216, v4_218, v4_219, v4_220, v4_226, v4_228, v4_230, v4_232, v4_233, v4_234, v4_235, v4_236, v4_237, v4_238, v4_239 |
| 1 | C2.1 | unknown | 0 | None | 0 | None |
| 1 | C2.1 | not_dispatched | 0 | None | 0 | None |
| 1 | C2.1 | first_rejection_not_proven | 0 | None | 0 | None |
| 1 | C3.1 | no_next_run_query | 28 | v4_184, v4_185, v4_187, v4_188, v4_190, v4_192, v4_193, v4_195, v4_201, v4_202, v4_204, v4_214, v4_215, v4_216, v4_217, v4_218, v4_220, v4_223, v4_226, v4_227, v4_229, v4_230, v4_231, v4_232, v4_233, v4_234, v4_236, v4_239 | 20 | v4_185, v4_188, v4_192, v4_202, v4_204, v4_214, v4_215, v4_216, v4_218, v4_220, v4_226, v4_227, v4_229, v4_230, v4_231, v4_232, v4_233, v4_234, v4_236, v4_239 |
| 1 | C3.1 | unknown | 1 | v4_219 | 1 | v4_219 |
| 1 | C3.1 | not_dispatched | 0 | None | 0 | None |
| 1 | C3.1 | first_rejection_not_proven | 0 | None | 0 | None |
| 2 | C | no_next_run_query | 0 | None | 0 | None |
| 2 | C | unknown | 0 | None | 0 | None |
| 2 | C | not_dispatched | 0 | None | 0 | None |
| 2 | C | first_rejection_not_proven | 0 | None | 0 | None |
| 2 | C2.1 | no_next_run_query | 5 | v4_188, v4_201, v4_204, v4_216, v4_237 | 4 | v4_188, v4_201, v4_204, v4_237 |
| 2 | C2.1 | unknown | 0 | None | 0 | None |
| 2 | C2.1 | not_dispatched | 0 | None | 0 | None |
| 2 | C2.1 | first_rejection_not_proven | 0 | None | 0 | None |
| 2 | C3.1 | no_next_run_query | 2 | v4_201, v4_204 | 2 | v4_201, v4_204 |
| 2 | C3.1 | unknown | 0 | None | 0 | None |
| 2 | C3.1 | not_dispatched | 0 | None | 0 | None |
| 2 | C3.1 | first_rejection_not_proven | 0 | None | 0 | None |

No-next and unknown-result failures are adjudicated binary zeros, not observations of a tool refusing SQL. They are retained symmetrically in E2 and in eligible cross-pass flips. In particular v4_219/C3.1 has a recorded native Binder Error after the next run_query; absent a structured whitelist-validation field, the conservative unknown-result rule is retained, not silently recoded as recovery.

## Family clustering

| Statistic | Families sampled | Families with eligible rows | Eligible n | Signed difference | Absolute net effect | 95% percentile CI | Zero denominator / 10000 | Valid replicates |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| endpoint1 | 11 | 3 | 179 | 0.05027932960893855 | 0.05027932960893855 | [0.03333333333333333, 0.0847457627118644] | 309 | 9691 |
| endpoint2 | 11 | 4 | 27 | 0.07407407407407407 | 0.07407407407407407 | [0.0, 0.1276595744680851] | 70 | 9930 |
| whole_question: C vs C2.1 | 11 | 11 | 300 | 0.006666666666666667 | 0.006666666666666667 | [0.0, 0.04927536231884058] | 0 | 10000 |
| whole_question: C vs C3.1 | 11 | 11 | 300 | 0.02 | 0.02 | [0.0, 0.050980392156862744] | 0 | 10000 |
| whole_question: C2.1 vs C3.1 | 11 | 11 | 300 | 0.013333333333333334 | 0.013333333333333334 | [0.0, 0.06190476190476191] | 0 | 10000 |

All formal rows above sample the same 11-family universe. Seed=42025, B=10000. Zero-denominator draws are counted and excluded from percentile calculation, not set to zero and not redrawn. Intervals conditional on a nonempty eligible draw can be unstable with few contributing families. Whole-question pairwise CIs are secondary descriptive intervals, not additional primary tests or evidence of general superiority.

## Sensitivity analysis: human-adjudicated v4_138

Main classification remains unchanged. In the separate sensitivity only, C is classified correct on v4_138: paired n=179; C2.1-only correct=8; C-only correct=0; exact two-sided McNemar p=0.0078125. This value is computed by exact_mcnemar, not copied from the instruction. Direction and nominal significance are unchanged. No sensitivity result replaces the main flip gate or primary p-value.

## Claim scope and locked external validity statement

On the v4 targeted distribution, per-question window-boundary injection (C2.1) reduced window-boundary errors relative to C (McNemar exact p = 0.00390625). This statement uses the frozen operational endpoint; its post-registration stability adjudication and parser limitations are disclosed above.
endpoint2: no significant improvement in the expected direction; no mechanism-improvement claim. The small paired recovery subset has insufficient power; non-significance does not establish equivalence or evidence against the mechanism.

No total-score superiority claim is made. Whole-question accuracy and its CIs are descriptive. C3.1 versus C2.1 accuracy differences are separated into targeted and non-targeted families; no transfer beyond the template distribution is asserted. All conclusions remain scoped to English questions, this snapshot and the declared templates. Post-registration decisions are not retroactively confirmatory procedure.

External validity statement (final wording, locked): "Within the template-defined distribution (well-formed English questions, the frozen 14-day 100-repository snapshot, the enumerated window/metric/scope combinations), the change in window-boundary errors for C2.1 relative to C is X. This does not extend to natural user query distributions, Chinese-language queries, other snapshots, or larger schemas."

The X placeholder above is retained in this verbatim locked quotation; any numerical claim must use the declared paired denominator and the adjudicated inferential status.

## Frozen errata

- C3 regression (t02/t17): zero feedback exposure is proven; the attribution of the regressions to trajectory variance is an inference, not a proof.
- "Window errors eliminated" claims for C2 apply to runs with a submitted SQL only; runs without a final SQL are excluded from window-error counting, not counted as correct.

## Limitations

Message-level token costs for injection and feedback, and actual runtime injected context text, were not recorded. They cannot be reconstructed exactly; no replacement observations or model estimates were created. The offline generator distractor probe is not runtime proof. Conservative E2 failures caused by absent/unknown follow-up are not actual observed whitelist rejections. E2 is underpowered and its flip comparison has only three common eligible questions. E1 has three contributing window families; its no-downgrade decision is very close to the specified threshold. Neither point identifies behavior on natural, multilingual or new-snapshot distributions.

Operational flip, recovery, bootstrap and prefix decisions were supplied after the initial results were seen and are explicitly post-registration. The locked main parser classification for v4_138 remains unchanged; its sensitivity is separate. Full-set absolute-effect CIs are descriptive and do not establish direction or superiority.


## Reproducibility and delivery

Run `python -B -m eval.score_v4` offline. The only analysis output is this report. No raw result, schedule, reference, parser, glossary, preregistration or historical artifact is modified. Synthetic tests and the full offline suite are reported separately at delivery; no model requests are made by the scorer.

## Delivery validation

- Full offline suite after adjudication implementation: **564 passed, 0 failed, 0 skipped**, 6 existing multiprocessing/fork deprecation warnings, 203.19 seconds. This consists of the previous 497 tests plus 67 scorer tests.
- Final scorer tests after report-format and Limitations completion: **67 passed**, 0.65 seconds. These presentation additions did not change endpoint values, denominators, bootstrap sampling or adjudication policy.
- Full-suite command: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider`. Synthetic tests cover zero-discordance McNemar, common denominators, conservative missing/unknown recovery, combined flips divided by n (including values above 1), zero/undefined thresholds, eligibility changes, 11-family sampling with zero eligible draws, literal prefix cutoffs, and the computed v4_138 sensitivity.
- All **96** pre-existing baseline files were hash-verified unchanged, including the database, both raw result files, question bank, parser/rubric, grader, context and preregistration. Git staging is empty.
- Only the three authorized Phase D artifacts changed: `eval/score_v4.py` (offline scoring/statistics/report generation), `tests/test_score_v4.py` (necessary independent synthetic validation), and this report. No new dependency or additional project file was introduced.
- The previously pending operational definitions are now resolved by the explicitly post-registration human decisions. The unrecorded message-token allocation and actual runtime injection text remain non-estimable limitations, not missing implementation work.
- No API/model call, new experimental trial, reference SQL execution, parser repair, frozen-input modification, credential access, git add, commit or push was performed in Phase D.
