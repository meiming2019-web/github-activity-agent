# v4 legacy A/B exploratory results

Exploratory, not pre-registered; results MUST NOT be merged into v4 confirmatory conclusions.

## Frozen code and collection

The clean-worktree gate passed before new files were created. All required hashes matched existing published ledgers. A/B call the actual frozen eval.run_experiment.run_config entry: full glossary for both, original one-shot for A, original bounded loop for B, with no lookup_glossary. No C-family trial is run. Historical v2 production-time uncommitted state remains unverifiable; this is reuse of the identified current frozen legacy paths, not a claim of recovered historical provider state.

Harness identifier: `legacy-ab-53121bb04092`; it identifies the frozen loop content, not a historical run-record label. Strict sorted question_id order; A then B; one worker; every trial has a fresh client/session/conversation. First-write-wins includes terminal failures. No outcome was scored before all 600 records landed.

| File | SHA-256 | Existing ledger |
| --- | --- | --- |
| agent/loop.py | 53121bb040921547e87583aa23b234f68bef320a6703f29b0477fc3884c90f93 | eval/c3_on_v2.md |
| eval/run_experiment.py | d9a2ffc5c419b22d9d47dceefe13bc15ccf6a8005ccfb4400853afd443c79465 | eval/c3_on_v2.md |
| agent/mcp_server.py | 3b55d233b1f8f27c1398df53a75065a456456e97219ac2607e9eb03d44b4d41f | eval/c3_on_v2.md |
| eval/grader.py | 34fdf04fb0a75836f78a0e2ec4c90fef4d9b7b5f6c4cab730b00abcbe502dd57 | eval/c3_on_v2.md |
| agent/error_feedback.py | 68fbbafdc74a7902ea4c12a6c92cb525fc6daff5ee50a9a2c4d514df90cdf230 | eval/c3_on_v2.md |
| agent/context.py | 72367ec27f81eda96a65dfa7c908f3f143bea922ed1f1d28ec7a1b2bb29a9ee4 | eval/v4_c21_change.md |
| eval/glossary.md | 1a2ce44850529108249fe9970803b1745787ecf37c63136a062a11bb808c3d05 | eval/c3_on_v2.md |
| eval/v4_questions.jsonl | 829ec0475c1ba1c090c8b1926221124df092af8b35b81ccc2a0a92e1fa897dc1 | eval/v4_preregister.md |
| data/github.duckdb | 2a063cab4176b97cfd00ea8e92932c64346127ba1da4b120452fb48236c25812 | eval/v4_preregister.md |
| eval/score_v4.py | 95a0f4ec4ccf5e3f4f501a2ff24e5fd001a35b142b22f01c1b0ea728616e3c1d | Phase D completion ledger |
| eval/run_v4.py | 80d0f9f67d427842ef3b9f9e6e220eedcc11279ef63307cfb0a61453f11b7a51 | eval/v4_preregister.md |
| eval/v4_sql_bounds.py | 331fa061ba46bb4cf53c52102eeddd3d0e423a557b3328469e0edbc34f32805f | eval/v4_preregister.md |
| eval/results/runs_v4.jsonl | b08c2881f8253d8d1e7d65b849f4fcd76499a2b0d467afe0a7f74140e7832240 | Phase C completion ledger |
| eval/results/runs_v4_pass2.jsonl | 8ff2597534c7459349107c0a55e8819f9c3b96f7a31700083ddddd59c44156a3 | Phase C completion ledger |
| eval/v4_report.md | 6d0555e8c513767983af96a9379e5c86923bfd714f0819e7950082b866ff2ca2 | Phase D completion ledger |

## Descriptive row-set accuracy

| Stratum | n | A | B |
| --- | --- | --- | --- |
| all | 300 | 236/300 (78.67%) | 251/300 (83.67%) |
| window | 180 | 169/180 (93.89%) | 158/180 (87.78%) |
| advanced_sql | 90 | 37/90 (41.11%) | 63/90 (70.00%) |
| control | 30 | 30/30 (100.00%) | 30/30 (100.00%) |

## Boundary classifications and non-submission

| Config | Window n | No final SQL | Correct | start_wrong | end_wrong | both_wrong | no_window_predicate | unparseable | All-strata no submission |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | 180 | 0 | 179 | 0 | 0 | 0 | 0 | 1 | 45 |
| B | 180 | 1 | 175 | 0 | 1 | 0 | 0 | 3 | 19 |

Boundary counts use the frozen parser on committed final SQL only. No final SQL is excluded, never counted as correct. Unparseable is not proof of a semantic boundary error. No parser repair, gold reconstruction, reference-SQL execution, hypothesis test, or confirmatory comparison is performed. All row scores use the same precomputed reference rows and unchanged score_v4.grade_rows logic.

## Collection health and trace limits

| Config | Terminal trials | API errors | API retries | Response models |
| --- | --- | --- | --- | --- |
| A | 300 | 0 | 0 | {'deepseek-flash': 300} |
| B | 300 | 0 | 0 | {'deepseek-flash': 1044} |

Original legacy traces are retained with additive legacy_api_trace/legacy_tool_trace protocol capture. This captures failed one-shot SQL without changing answer_sql or treating an attempted query as a submission. Request/response protocol content and MCP outcomes are preserved with key redaction; SDK-private reasoning and authentication headers are not captured. The trial fields match the v4 record envelope (pass=1, worker=0, block/time/harness), in a separate exploratory file.

A process crash after an external request but before durable recording cannot prove exactly-once external execution. Such an uncertain interrupted trial requires manual examination before resume; no blind retry is authorized. A second concurrent collector is rejected before any trial. Recorded failures are never retried.

## Execution and validation evidence

Collection completed normally with 600 distinct terminal identities, no missing identities, and no repeated recorded identity. UTC interval: 2026-10-25T18:18:16.621612+00:00 to 2026-10-25T18:58:39.882590+00:00; duration 2423.260978 seconds (40 minutes 23.26 seconds), block 1 only. A made 300 API requests and B made 1044; all 1344 response model fingerprints were deepseek-flash. There were zero API errors and zero API retries.

The original legacy terminal statuses were A: 255 completed / 45 error; B: 281 completed / 19 error. These are preserved terminal outcomes, not additional API errors. Every such trial remains in the raw file and was not rerun. These counts are distinct from row-set correctness.

Before any API request, the new offline tests passed 20/20 and the complete offline suite passed 584/584 (564 existing + 20 new) in 204.64 seconds. Six existing multiprocessing fork deprecation warnings were emitted. The first new-test run had one fixture import failure (an unavailable httpx import); the fixture was corrected to the already installed SDK dependency httpx2. No dependency was added and no experiment was used to debug it. Equivalence tests compare actual frozen run_config with the transparent capture wrapper for A and B, including request inputs, original trace output, failure handling, and branch/tool behavior. Other tests cover redaction, fresh transport, first-write-wins, concurrent exclusion, completeness-gated scoring, and output-path isolation.

The initial working tree was clean. All 15 ledger checks above matched again after collection and scoring. No tracked source, frozen question, database, historical result, preregistration, or confirmatory report was modified. Only the four files below are new; the test file is necessary to satisfy repository test requirements and verify unchanged legacy behavior. No git add, commit, or push was performed. No C-family or smoke trial was run.

| New artifact | SHA-256 |
| --- | --- |
| eval/run_v4_ab.py | 09bbeb4b1d39f2781ee670b390d103ed97151096050c7cd83c966a2c04d4a17c |
| tests/test_run_v4_ab.py | 4853996bacb94d4acb5bb8a874e761e9bc85f0d638260321fbafcdc4497b964c |
| eval/results/runs_v4_ab_exploratory.jsonl | e8237e43764b30d5a4c8d4c11070b29c49063e5bdf39556a6d2ec74282ba2194 |

The hash of this report is supplied in the completion message, avoiding a self-referential checksum.
