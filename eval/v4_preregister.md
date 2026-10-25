# v4 Preregistration — Targeted Prospective Validation of C2.1 and C3.1

Date of registration: 2026-10-25
Status: registered before any v4 experimental run. No accuracy measurement has been performed on the v4 question set.

## 0. Frozen artifacts and hashes

| Artifact | SHA-256 |
| --- | --- |
| Question set `eval/v4_questions.jsonl` (300 questions, 100 semantic cases) | 829ec0475c1ba1c090c8b1926221124df092af8b35b81ccc2a0a92e1fa897dc1 |
| Generator `eval/gen_v4_questions.py` | 318aee7fb68c6a660b0598ea77710f3ab7ecdcb66b1b8d6ce90a28076fe6b498 |
| Generator seed | 42 (pre-declared; any reseeding after this date invalidates confirmatory status) |
| Database snapshot `github.duckdb` | 2a063cab4176b97cfd00ea8e92932c64346127ba1da4b120452fb48236c25812 |
| Boundary parser `eval/v4_sql_bounds.py` | 331fa061ba46bb4cf53c52102eeddd3d0e423a557b3328469e0edbc34f32805f |
| Boundary rubric `eval/v4_boundary_rubric.md` | 71d2108cdbb2419e1ba5e1676162b27f56b93295bc87401cd01251dd954e411d |
| Scheduler `eval/run_v4.py` + schedule `eval/v4_schedule.jsonl` | 80d0f9f67d427842ef3b9f9e6e220eedcc11279ef63307cfb0a61453f11b7a51 / 1a9be6c1571f5aceb917fdcc88ff3a66dc5bebcfa9b1540de6ea23620494234e |

Supporting evidence (already committed): glossary audit, adjudication, C2.1 change control, 86/86 byte-identical replay of the legacy entry, FK integrity audit, overlap audit, regeneration log, human sample reviews (round 1 and r2).

## 1. Design classification (honest labeling)

v4 is a **targeted prospective validation** on a **synthetic, stratified, template-generated distribution** whose template families were designed after observing failure modes in v2/v3. It is confirmatory in *procedure* (endpoints, rubrics, hashes, blinding, and analysis rules are locked before any run) but **not** an unbiased confirmatory test on a natural query distribution, because the test distribution was adapted to the previously observed failures.

External validity statement (final wording, locked): "Within the template-defined distribution (well-formed English questions, the frozen 14-day 100-repository snapshot, the enumerated window/metric/scope combinations), the change in window-boundary errors for C2.1 relative to C is X. This does not extend to natural user query distributions, Chinese-language queries, other snapshots, or larger schemas."

## 2. Configurations

- **C**: frozen original configuration (bounded loop, on-demand glossary lookup).
- **C2.1**: C + static glossary-derived date context + one per-question window-boundary line via the question-aware entry `c2_date_context_for_question`. C2.1 is a backward-compatible extension of C2: the legacy entry produces byte-identical contexts on all 86 historical questions (evidence: `eval/v4_c21_replay.md`).
- **C3.1**: C2.1 + actionable whitelist error feedback. The sole difference from C2.1 is the error-feedback middleware.

All run records carry `harness_version="c2.1"`.

## 3. Question set

300 questions = 100 semantic cases × 3 phrasing tiers (literal / colloquial / distractor).

- Window stratum: 180 (3 families × 60), targeted.
- Advanced SQL stratum: 90 = 60 targeted (daily_trend, running_total, day_over_day, day_of_week) + 30 non-targeted (session_segmentation, consecutive_day_runs).
- Control stratum: 30 (catalog_lookup, language_composition), no time semantics.

Authorized window vocabulary is a closed set (3 relative phrases + explicit inclusive ranges within coverage), per `eval/v4_glossary_adjudication.md`. Every question passed the hard assertions: non-empty/non-all-zero reference rows, extended within-coverage sensitivity battery (every testable single-bound and double-bound perturbation changes the reference row set), deterministic Top-N tie-breaking stated in the question text. Out-of-coverage perturbations are excluded uniformly; for generate_series scaffold questions an out-of-coverage day may add a zero-count row, so no neutrality claim is made for that family. Row-set grading blind spots for endpoint slips are backstopped by the SQL window-endpoint parsing (Endpoint 1), not by row-set grading.

Three semantic cases used fallback tier 1 (metric PushEvent → WatchEvent, window unchanged); no case used tier 2/3; `battery_relaxed = 0`. All adjustments are recorded in `eval/v4_regen_log.jsonl` and `eval/v4_fk_audit.md`.

## 4. Primary endpoints and statistical plan

**Endpoint 1 (window stratum; C vs C2.1).** Per-question binary: is the window boundary of the agent's final submitted SQL correct, per the pre-registered rubric (`eval/v4_boundary_rubric.md`) executed by `eval/v4_sql_bounds.py`. Classification set: correct / start_wrong / end_wrong / both_wrong / no_window_predicate / unparseable. Test: exact two-sided McNemar on paired discordant counts, α = 0.05. Questions with no submitted SQL are excluded from Endpoint 1 (no SQL to classify) and counted separately.

**Endpoint 2 (advanced SQL stratum; C2.1 vs C3.1).** Step recovery after the first whitelist rejection: binary per question — does the next `run_query` call after the question's first whitelist rejection pass whitelist validation? Primary analysis: exact McNemar on the paired subset of questions where **both** configs recorded ≥ 1 whitelist rejection. Recovery rates on each config's full rejection set are reported descriptively. Whole-question accuracy and breaker counts in this stratum are secondary.

**Gatekeeping (multiplicity control).** Fixed-sequence testing: Endpoint 2 is tested only if Endpoint 1 reaches p &lt; 0.05. Each test at α = 0.05; no alpha splitting.

## 5. Power statement (sensitivity, not a guarantee)

Endpoint 1, window stratum n = 180, assuming C2.1 window-error rate ≈ 0:

| Assumed C window-error rate | Power (no background flips) | Power (3.3% symmetric background flip, matching observed C3-regression variance) |
| --- | --- | --- |
| 10% | &gt;99% | ≈92% |
| 5% | ≈87% | ≈31% |
| 3% | ≈45% | ≈6% |

The v3 point estimate for C's window-error rate was 2/13 ≈ 15%, with a very wide confidence interval (n = 13). **Pre-registered interpretation:** if the true rate is ≤ 5%, a non-significant result is an expected outcome of insufficient power, not evidence against the mechanism; the report must then present the observed discordant counts and confidence bounds instead of a significance claim.

Endpoint 2 is expected to be underpowered for whole-question accuracy (historical breaker rate ≈ 8%, observed revival rate ≈ 40%); this is why its primary metric is the per-event step-recovery mechanism metric.

## 6. Guardrail

Control stratum (30 questions): all three configs are mechanistically zero-exposure there. Guardrail rule: if **any** pairwise comparison (C–C2.1, C2.1–C3.1, C–C3.1) on the control stratum reaches exact McNemar p &lt; 0.05, pause before reporting and investigate. Additionally pre-registered: per-config count of control questions where a time filter was wrongly introduced (over-application), from SQL parsing.

## 7. Secondary endpoints and process metrics

- Per-stratum whole-question accuracy (row-multiset grading against precomputed reference rows; grader unchanged).
- Error taxonomy identical to v2/v3 (wrong_result_set / sql_error_exhausted / no_submission / missing_columns / breaker), reported per config × stratum.
- First-attempt success rate (first submitted SQL correct vs loop-recovered).
- Silent empty/zero submission rate among wrong answers.
- C2.1 vs C3.1 prefix-match rate (action-sequence identity before first divergence).
- Distractor probe outcomes: injection must append the operative window only; mis-append count is a negative control.
- Cost: prompt/completion tokens and tool calls per question, per config × stratum, including isolated cost of the injected line and of feedback messages.
- Model fingerprint counts (`response_models` fields) across the run window.

## 8. Clustering and inference caveats

Questions are template-generated; intra-family correlation exists, so the 300 questions are not 300 independent concept tests. Primary McNemar p-values are question-level and are interpreted alongside per-family results; a cluster-bootstrap confidence interval by template family is reported as a secondary analysis. Stratified reporting separates targeted vs non-targeted families; if C3.1's advantage appears only on targeted families, conclusions are narrowed accordingly.

## 9. Execution protocol

- Per-question execution order of (C, C2.1, C3.1) assigned by seeded RNG over the 6 permutations, balanced; the assignment is frozen in `eval/v4_schedule.jsonl` and never redrawn on resume.
- 5 parallel workers; each question's three configs run adjacently on the same worker; every trial starts from a fresh conversation state.
- first-write-wins: each (question_id, config, pass) is recorded exactly once; no re-runs, no best-of selection.
- Results are written only to `eval/results/runs_v4.jsonl` (pass 1) and `eval/results/runs_v4_pass2.jsonl` (pass 2).
- Blinding: the runner prints progress counts only; no accuracy aggregation until all runs of the pass have landed.
- Interruption longer than 2 hours starts a new block, recorded in the log.
- **Flip-rate substudy (pass 2):** a pre-declared random subset of 60 questions × 3 configs is run a second time. Pre-registered downgrade rule: if the observed flip rate is ≥ 50% of the observed discordant effect size for an endpoint, the affected claim is reported as exploratory, not validated. The pass-2 subset (60 questions) and its execution order are selected by seeded RNG and frozen in eval/v4_schedule.jsonl before any v4 run; pass 2 executes only after pass 1 completes, under the same blinding and first-write-wins rules.

## 10. Pre-registered claim language

- If Endpoint 1 is significant in the expected direction and the guardrail does not trigger: "On the v4 targeted distribution, per-question window-boundary injection (C2.1) reduced window-boundary errors relative to C (McNemar exact p = …)."
- If Endpoint 2 is significant in the expected direction: "Actionable whitelist feedback (C3.1) improved immediate step recovery after whitelist rejections relative to C2.1."
- Whole-question accuracy differences are reported descriptively unless explicitly covered above; no total-score superiority claim is licensed by this design.
- All statements are scoped to the frozen snapshot, the template distribution, and English questions.

## 11. Errata (wording corrections to earlier reports; frozen files unchanged)

- C3 regression (t02/t17): zero feedback exposure is proven; the attribution of the regressions to trajectory variance is an inference, not a proof.
- "Window errors eliminated" claims for C2 apply to runs with a submitted SQL only; runs without a final SQL are excluded from window-error counting, not counted as correct.