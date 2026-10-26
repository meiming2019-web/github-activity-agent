# Reproducibility & full experiment record
Moved verbatim from README.md.

## Experiments

All experiments use a frozen DuckDB snapshot of GH Archive events covering
`[2026-10-08, 2026-10-22)` UTC, SHA-256
`2a063cab4176b97cfd00ea8e92932c64346127ba1da4b120452fb48236c25812`,
with a frozen metrics glossary ([eval/glossary.md](../eval/glossary.md)). Run records,
scores, analysis documents, and their hash ledgers live in `eval/`.

### 1. Architecture ablation (A vs B vs C, v2 question set)

- **A** one-shot, full glossary in context
- **B** A + bounded tool loop (run queries, see errors, retry)
- **C** B's loop + on-demand `lookup_glossary` instead of the full glossary

On the 60-question set, the disclosed grader-v2 re-score recorded A 44/60, B 48/60, and C 50/60. The source preserves the original frozen v1 totals of 37/60, 40/60, and 40/60, respectively. The revised totals follow disclosed answer-key and column-matching corrections applied to frozen first-write-wins attempts; no agents were rerun. These are post-hoc re-scoring results, not a fresh experimental replication. Source: [eval/results/summary.md](../eval/results/summary.md#grader-v2-re-score-post-hoc-disclosed).

### 2. Mechanism probes (C2 / C3, v2 regression set)

- **C2** = C + static glossary-derived date context
- **C3** = C2 + whitelist error feedback

On the already-seen v2 regression set, C2 scored 47/60 versus historical C's 50/60: three prior failures became correct and six prior passes became incorrect. The separate collection windows do not identify a causal effect of boundary injection. C3 also scored 47/60; it revived 2/5 previously circuit-broken questions and reduced sql_error_exhausted from 5 to 1, but two C2-correct questions became C3-incorrect, exceeding the allowance of at most one. The C3 report therefore suspends conclusions pending manual investigation; neither the aggregate tie nor execution recovery establishes a mechanism benefit. Sources: [eval/c2_on_v2_regression.md](../eval/c2_on_v2_regression.md) and [eval/c3_on_v2.md](../eval/c3_on_v2.md).

### 3. v4: preregistered validation (confirmatory scope)

Pre-registered before any run ([eval/v4_preregister.md](../eval/v4_preregister.md)).
300 questions (100 semantic cases × 3 phrasing tiers; 180 window / 90 advanced-SQL /
30 control), 1,080 blind runs across two passes, with raw records committed before
grading. Operational analysis definitions were subsequently resolved through
explicitly labeled **post-registration adjudications**; these are not retroactive
preregistration content. Full details: [eval/v4_report.md](../eval/v4_report.md).

- **Endpoint 1 (validated within the stated scope):** question-aware
  window-boundary injection (C2.1) vs C on the frozen window-boundary endpoint —
  C2.1-only correct 9 / C-only correct 0, paired n = 179 with one joint exclusion;
  exact McNemar p = 0.00390625 (separate sensitivity: 8/0,
  p = 0.0078125). The nine discordances include eight `both_wrong` classifications
  and one `unparseable`, not nine independently established semantic errors.
  No window-drift errors were observed under C2.1 in this run: all 180 submitted
  window queries were classified correct. This does not establish a within-trace
  causal explanation for the cross-configuration differences in §4.
- **Endpoint 2 (not validated):** actionable whitelist error feedback
  (C3.1) vs C2.1 on recovery at the first `run_query` after the first rejection —
  C3.1-only recovery 2 / C2.1-only recovery 0, paired n = 27, p = 0.5.
  Direction positive, evidence insufficient and the paired subset underpowered;
  absence of a subsequent query or an identifiable result counts as failure under
  the post-registration adjudication.
- Guardrails did not trigger: control-stratum pairwise p = 1, and zero detected
  extra time filters in 30 controls per configuration. This does not prove absence
  of side effects.
- The final adjudicated flip rule divides the combined flips of the two compared
  configurations by their common eligible question count, not twice that count.
  Endpoint 1: 1/40 = 0.025, below the threshold 0.025139664804469275.
  Endpoint 2: 0/3 = 0.0, below 0.037037037037037035. Each threshold is half the
  pass-1 absolute net discordance proportion. Neither endpoint was downgraded;
  Endpoint 1 is close to its threshold, and Endpoint 2 has only three common
  eligible questions. Eligibility changes are excluded from the flip denominator.
- Scope: targeted prospective validation on a templated question distribution
  over one frozen snapshot. No total-score superiority claims.

### 4. Exploratory A/B ladder on the v4 question set (descriptive)

A/B were run afterwards as a **non-pre-registered, descriptive** complement
([eval/v4_ab_exploratory.md](../eval/v4_ab_exploratory.md)). These numbers must not be
merged into the v4 confirmatory conclusions. The combined table is descriptive:
A/B and the C-family configurations were collected in separate runs.

Row-set accuracy by stratum (n = 300 per config):

| Config | All | Window /180 | Advanced /90 | Control /30 | API calls | Total tokens | K tokens / correct (derived) |
|---|---|---|---|---|---|---|---|
| A | 236/300 (78.67%) | 169 | 37 | 30 | 300 | 4,038,694 | 17.1 |
| B | 251/300 (83.67%) | 158 | 63 | 30 | 1,044 | 15,153,387 | 60.4 |
| C | 267/300 (89.00%) | 172 | 65 | 30 | 1,394 | 18,775,211 | 70.3 |
| C2.1 | 269/300 (89.67%) | 179 | 60 | 30 | 1,280 | 17,440,670 | 64.8 |
| C3.1 | 273/300 (91.00%) | 178 | 65 | 30 | 1,298 | 17,726,664 | 64.9 |

Accuracy comes from the two reports above; advanced C-family counts combine their
targeted and non-targeted rows. Exact API and token totals are checked against
[the A/B records](../eval/results/runs_v4_ab_exploratory.jsonl.gz) and
[the C-family pass-1 records](../eval/results/runs_v4.jsonl), including failed attempts.
Only the explicitly derived column is rounded to one decimal:
`(prompt tokens + completion tokens) / correct answers / 1000`.

Findings:

- **Different observed loop outcomes by stratum.** On window questions, B broke
  19 questions that one-shot A answered correctly while rescuing 8 — a net loss
  of 11. Here "broke" and "rescuing" describe paired final verdicts, not an
  identified causal mechanism. On advanced SQL, B recorded 63/90 versus A's
  37/90; A had 45 non-submissions, all in this stratum, and B had 18 here.
  These observations do not prove that retrying caused each change.
- **Final boundaries and row-set correctness are distinct.** One-shot A had
  179/180 window queries classified correct and one unparseable query. B had
  175 correct, one `end_wrong`, three unparseable, and one without final SQL.
  C2.1 had 180/180 classified correct. These final-query observations do not
  establish that boundaries are never a model limitation or that the loop caused
  every observed difference.
- **Observed accuracy and token use.** C2.1 achieved higher accuracy with fewer
  tokens than C in this run. B used more tokens than A and had more correct
  answers overall. Neither observation establishes dominance, a universal
  value-for-token ranking, or the cause of the cost difference; injection and
  feedback token costs were not separately recorded.
- Boundary parser limitations are disclosed in the reports: `unparseable` does
  not mean a semantic error. Frozen classifications remain unchanged; the
  explicitly authorized v4_138 sensitivity in §3 is reported separately.

### Limitations

- Single frozen snapshot; templated question distribution; results do not
  establish free-form natural-language robustness.
- Recorded v4 responses report `deepseek-flash`; a floating model alias does not
  pin a provider version. Temperature-0 whole-question flips in the pass-2
  subset were C 4/60 (6.67%), C2.1 2/60 (3.33%), and C3.1 4/60 (6.67%). These
  descriptive flips are distinct from the endpoint-specific downgrade rule.
- Accuracy comparisons other than the two preregistered endpoints are
  descriptive only. Operational post-registration adjudications and parser
  limitations remain disclosed, including for the primary endpoints.

### Future Work

1. **D-variant pre-submit verification**: test a self-check step before
   `submit_answer` (re-derive window bounds, verify row counts against a probe
   query). Its benefit and cost remain untested.
2. Test a whitelist-idiom cookbook in the prompt, targeting the observed
   advanced-stratum non-submissions (18–45 per 90 across configurations).
3. Evaluate extending actionable error feedback to the `submit_answer` path.
4. Re-run the ladder on a non-templated, human-authored question set under a
   separately specified protocol.

## Experiment design

All configurations receive the same static context: complete names and types for `events` and `repos`, three sample rows per table, UTC conventions, and the frozen reference date **2026-10-22**. Schema and samples are fetched once at startup and reused; setup is outside the deliberative tool budget. Questions and reference answers are kept separate, and reference SQL is never injected into model context.

| Config | Glossary access | Execution protocol |
|---|---|---|
| A | Full glossary in context | One model request, no model-visible tools, no retry; SQL is executed once through MCP and its result is submitted |
| B | Full glossary in context | Four MCP tools plus client-side `submit_answer`; bounded SQL correction loop |
| C | Keyword retrieval instead of the full glossary | B's loop plus client-side `lookup_glossary`, returning whole matching glossary sections |

A versus B changes the interaction protocol. B versus C changes glossary injection versus retrieval. All use `deepseek-chat` with `temperature=0`; B/C allow at most 12 tool calls, including lookup and submission, and stop after three consecutive SQL errors.

The test set has 60 questions in two preregistered batches, `t01–t30` and `u01–u30`. Here preregistration means a local Git freeze before the respective recorded experiment, not an external registry: batch 1 was frozen at `0111add`, before the results recorded in `70842e4`; batch 2 was frozen at `e13de74`, before the combined results recorded in `0f17c29`. The batches follow the same authoring protocol. Configurations run interleaved by question, with first-write-wins recording: every recorded outcome, including an error, is terminal and skipped on resume.

Grading is deterministic and offline over the frozen data. It checks submission status, truncation, and result shape, then compares unordered multisets with duplicate counts preserved. Grader v2 pins case-insensitive name matches and uses bounded value matching for unmatched columns. Floats use relative tolerance `1e-6` with no absolute tolerance. Empty or truncated reference results are configuration errors rather than valid gold answers.

## Results

The combined 60-question results below use the disclosed grader-v2 adjudication of frozen attempts.

| Config | Correct / 60 | Rounded accuracy | Total tokens per correct answer |
|---|---:|---:|---:|
| A | 44/60 | 73% | 18.4k |
| B | 48/60 | 80% | 72.0k |
| C | 50/60 | 83% | 80.3k |

Token cost includes prompt and completion tokens from all recorded attempts, divided by correct answers. The paired McNemar comparisons are reported below; discordant counts are ordered in the direction named by each comparison.

| Comparison | Discordant pairs | p-value |
|---|---:|---:|
| C vs B | 5:3 | 0.73 |
| B vs A | 6:2 | 0.29 |
| C vs A | 9:3 | 0.15 |

These observations do not establish a configuration ranking. Looping and retrieval consume more tokens per correct answer in this experiment, while the evidence for a consistent accuracy ordering remains limited.

## The replication story

Config C was ahead in the first batch, but the ordering reversed in the second. Reporting only the initial batch would have told a different story from the combined record. The project therefore emphasizes frozen questions, retained failures, disclosed grading corrections, and separate mechanism probes rather than presenting a configuration victory.

The combined result is a record of this model, snapshot, question set, and protocol. The second batch is a check on the initial observation, not a reason to select a favorable subset after seeing its outcomes.

## Failure analysis

The combined grader-v2 record contains 38 failures across 180 attempts. These stored grading categories describe terminal outcomes; they are not the requested causal taxonomy.

| Stored category | Count |
|---|---:|
| `wrong_result_set` | 29 |
| `sql_error_exhausted` | 5 |
| `no_submission` | 2 |
| `missing_columns` | 2 |

| Failure mode | Records | Examples | What happened |
|---|---|---|---|
| Calendar-scaffold omission | 4 | t10-A, t24-A, u24-A/B | No generate_series + zero-fill; days with zero events silently dropped from daily series |
| Metric-semantics divergence | 4 | t19-B/C, u23-A/C | ≥3-per-actor threshold applied at repo level (t19); global COUNT(DISTINCT actor) used as denominator instead of sum-of-per-repo (u23) |
| Ranking/aggregation universe loss | 4 | u26-A/B/C, u11-C | Ranked only repos with events instead of the full 100-repo catalog (u26); INNER instead of LEFT JOIN dropped zero-activity repos (u11) |
| Predicate-discipline errors | 4 | t02-A/B, t05-B/C | Omitted the frozen [bot] exclusion (t02); invented extra exclusion lists not in the glossary (t05) |
| Tie-breaker omission | 3 | t08-A, t17-A, t19-A | Missing deterministic secondary sort → wrong row at the LIMIT boundary |
| Ambiguous-metric divergence | 3 | t22-A/B/C | "Community heat score" is not defined in the glossary; all three configs invented three different formulas — question under-specified (disclosed limitation) |
| Reference/grading mismatch (disclosed) | 3 | t21-A/B/C | All three configs returned identical per-repo averages; the reference computes AVG after the join, making it event-weighted. Disclosed as a mismatch; scores remain unchanged |
| NULL-label rewriting | 2 | t13-A/B | COALESCE(language, 'Unknown') relabels the NULL bucket; value comparison fails |
| Window boundary off-by-one | 1 | u19-C | Used [Oct 9, Oct 23) instead of the frozen [Oct 8, Oct 22) half-open window |
| Output-scope filter omission | 1 | t26-B | Correct rolling average but returned 14 rows instead of the requested Oct-10-onward 12 (plus a hardcoded repo_id learned mid-loop) |

A post-hoc exploratory slice of the 18 window-function questions gives A 12/18 and B/C 15/18 each. Single-table and join results were close. These complexity slices were examined after the experiment and should not be treated as predeclared confirmatory comparisons.

## Re-run audit (config C, all 60 questions, temperature=0, separate declared probe file; frozen v2 results are unchanged and remain the primary outcome)

- Verdict agreement with frozen v2: 54/60 (90%). Frozen C scored 50/60; one independent
  re-run scored 46/60. This single observed shift of 4 questions (including one
  infrastructure connection failure) exceeds the frozen C-B gap (2) and equals the
  B-A gap (4). We therefore claim no reliable accuracy ranking. We do NOT claim an
  estimated noise floor: one re-run cannot bound run-to-run variance, and only
  config C was re-run.

- Final SQL text: of the 55 questions with SQL on both sides, 13/55 (23.6%) were
  byte-identical and 42/55 differed (formatting, aliases, predicate order, or
  structural choices); 5 lacked SQL on at least one side. Verdict agreement does not
  imply identical result sets, and differing strings were not audited for semantic
  equivalence. Claim: final SQL text often varies; the graded verdict stayed the same
  on 90% of questions.

- Token usage: average prompt tokens per run were 65.8k (frozen) vs 64.1k (probe),
  a ~2.5% difference between these two runs. No cost-stability guarantee is made:
  actual cost also depends on completion tokens, cache hits, and pricing, and
  per-correct cost scales with pass count.

- Glossary retrieval: 21/21 glossary questions triggered lookup_glossary (all hits);
  36/38 evaluable non-glossary controls also triggered it (t03 and u28 did not; u24
  received no model response and is excluded). Retrieval is near-universal, not
  selective. "FP" is defined by the needs_glossary label; looking up time conventions
  is not necessarily useless.

- Flip inventory (6): u24 = connection error (infrastructure). Infrastructure errors
  affected two probe questions in total: u24 (a PASS->FAIL flip) and u23 (FAIL->FAIL,
  but the failure reason changed from wrong_result_set to connection error). Both
  remain in the 60-question verdict-agreement denominator (u23 counts as agreement);
  per-metric analyses state their own exclusions (u24 is excluded from lookup-trigger
  and behavioral analyses; u23's SQL adherence is unjudgeable).
  t10 = mid-trajectory error-budget exhaustion. t02 = probe dropped the actor/bot
  predicates (the same trap frozen A/B fell into). t13 = probe rewrote the join as
  INNER JOIN from the events side with COUNT(*), losing zero-event languages.
  u20 = probe used the shifted window [Oct 9, Oct 23). u19 = PASS this time; the frozen
  run had used the same shifted window as probe-u20. All classifications are observed
  SQL/status differences; no root cause is inferred beyond them.

- Recurring error: the shifted window [Oct 9, Oct 23) appeared in two independent runs
  on two different questions (frozen u19, probe u20). This shows recurrence under the
  same configuration across two different questions; its root cause and any fix are
  unverified.

- Caveats: DeepSeek-chat is a floating alias, so provider-side version drift between
  run days cannot be ruled out; connection errors appeared only in probe runs. This
  audit characterizes run-to-run behavior of config C only: it does not estimate a
  statistical noise range, does not license any A/B/C ranking, and does not establish
  cost stability. Frozen primary results stand unchanged.

## Errata

The original frozen v1 totals were A 37/60, B 40/60, and C 40/60. A disclosed answer-key correction changed expected repository identifiers to repository names in 10 questions where the catalog has a one-to-one ID/name mapping. Question text and agent attempts were unchanged; the correction is recorded in commit `ef7f128`.

t21 has a disclosed reference/grading mismatch: the reference SQL computes
   AVG after the join (event-weighted), while all three configs returned identical
   per-repo averages; the grader uses a 1e-6 relative tolerance, so the mismatch is
   not a rounding artifact. Scores remain unchanged.

A separate disclosed grader-v2 correction pins matched column names and searches value mappings for unmatched columns, addressing surface alias and column-order differences. Re-scoring used stored answer rows and read-only reference execution, without rerunning agents. `runs.jsonl` retains the original outcomes, `runs_v2.jsonl` retains the disclosed adjudication, and `summary.md` preserves the original record followed by its disclosure. The Results section explicitly uses v2; independent mechanism-probe records never enter the main totals.

## Limitations

The study has 60 questions, one model, and one provider. `deepseek-chat` is a floating model alias, so later requests need not reach the same underlying model version. A frozen top-repository snapshot is a narrow workload rather than a general GitHub or text-to-SQL benchmark.

120 frozen B/C records lack tool traces. Their glossary-trigger decisions cannot be reconstructed from the frozen artifacts. The later probe observes config C only and cannot establish A/B retrieval behavior or repair missing historical traces.

`t22` uses the underspecified phrase “community heat score.” Its answer key canonicalizes this as total event count, while that term is absent from the glossary. The frozen record cannot establish a claim that lookup was omitted. In the independent probe, the agent did request that term and received no matching section, then retrieved other definitions. This is evidence of a missing definition, not evidence that retrieval was never attempted.

t21 has a disclosed reference/grading mismatch: the reference SQL computes
   AVG after the join (event-weighted), while all three configs returned identical
   per-repo averages; the grader uses a 1e-6 relative tolerance, so the mismatch is
   not a rounding artifact. Scores remain unchanged.

The complexity analysis is post-hoc. The glossary defines only three project-specific metrics: `new_stars`, `collaboration_events`, and `active_contributors`. Whether temperature zero directionally disadvantages a correction loop is an unverified hypothesis; the current experiment does not test it. A received lookup, a matching glossary return, use of the definition in SQL, and a passing final result are distinct observations.

## Future work

Improve schema linking so the agent can identify the required columns and aggregation grain before writing SQL. Evaluate self-consistency with an explicitly budgeted protocol, validate changes on a new frozen test set, and test robustness across temperature settings. These are proposed follow-ups, not implemented or measured results.

## Reproducibility

Use Python 3.12 and the local `.venv`. requirements.txt pins all project dependencies, including the openai SDK and python-dotenv used by the agent.

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

The frozen database is `data/github.duckdb`; it is not a replacement for the question and result artifacts. Runtime credentials belong in the ignored `.env` as `DEEPSEEK_API_KEY`, never in committed files or rendered traces. The experiment and UI use the fixed reference date; the standalone CLI below sets it explicitly.

### Obtaining the frozen database

**Preferred: use the published snapshot.** Open [Release v1.0-freeze](https://github.com/meiming2019-web/github-activity-agent/releases/tag/v1.0-freeze). From the repository root, create the destination directory:

```bash
mkdir -p data
```

Download the attached [github.duckdb.gz](https://github.com/meiming2019-web/github-activity-agent/releases/download/v1.0-freeze/github.duckdb.gz) and save it as `data/github.duckdb.gz`. Decompress the gzip attachment to `data/github.duckdb`, then check the **decompressed file**, not the gzip archive:

```bash
gunzip data/github.duckdb.gz
printf '2a063cab4176b97cfd00ea8e92932c64346127ba1da4b120452fb48236c25812  data/github.duckdb\n' | shasum -a 256 -c -
```

The checksum command must report `data/github.duckdb: OK`. If obtaining an already decompressed copy, place it directly at `data/github.duckdb` and skip `gunzip`. Use the verified Release snapshot to reproduce the recorded evaluation.

**Fallback: reconstruct from the sources.** Use a separate working copy without an existing database; the following commands write metadata and event tables. Keep the historical `repos.txt` list of 100 `owner/repo` entries rather than regenerating today's top repositories. Put a nonempty `GITHUB_TOKEN` assignment in the ignored project-root `.env`: `fetch_repos.py` reads that file directly, not an exported token alone. This GitHub REST token is distinct from `DEEPSEEK_API_KEY`; no DeepSeek key or model call is needed for reconstruction.

Run these commands from the repository root. `fetch_repos.py` takes no CLI options. The ingestion hour bounds are inclusive and UTC:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B scripts/fetch_repos.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B scripts/ingest.py \
  --start 2026-10-08-00 \
  --end 2026-10-21-23 \
  --repos repos.txt \
  --raw-dir data/raw \
  --database data/github.duckdb
```

Check the reconstructed tables against the historical counts of **28,203 events and 100 repos** through the existing read-only query interface:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B - <<'PY'
from agent.mcp_server import run_query

counts = run_query(
    "SELECT (SELECT COUNT(*) FROM events) AS events, "
    "(SELECT COUNT(*) FROM repos) AS repos"
)
print(dict(zip(counts.columns, counts.rows[0])))
assert counts.rows == [[28203, 100]], "Counts differ from the historical snapshot."
PY
```

These are historical sanity-check targets, not guaranteed outcomes of a current rebuild. GitHub metadata and repository names can change, API access can fail, and historical GH Archive files may be unavailable; these conditions can prevent reproducing the counts. Even matching row counts do not establish identical metadata or query answers. A reconstruction has no byte-identity guarantee, and the Release checksum above applies only to the frozen snapshot.

### Command input dependencies

| Command | Required inputs | Real credentials |
|---|---|---|
| Venv creation and pip installation | Python 3.12 and `requirements.txt`; no database | None; package installation needs network access |
| Release download, decompression, and checksum | Release asset; no pre-existing database | None for the public Release |
| Offline pytest command | Project code, tests, and repository test assets; no frozen database | None; fixtures use fake credentials |
| `--dry-run` | Selected question file; existing `runs.jsonl` is read if present; no database | None |
| `verify_questions.py` | `data/github.duckdb` and the selected question file | None |
| `scripts/fetch_repos.py` | Fixed `repos.txt` and project-root `.env`; creates the default database if absent | `GITHUB_TOKEN` in that `.env`; GitHub REST access |
| `scripts/ingest.py` | Fixed `repos.txt`, requested hour range, and available public GH Archive files; creates its tables if absent | None; public archive downloads need network access |
| Reconstruction count check | Database containing `events` and `repos` | None |
| Streamlit UI and standalone agent CLI | `data/github.duckdb`; the UI also reads its glossary and development examples | `DEEPSEEK_API_KEY` in the project `.env` |

### Full test suite and snapshot-free CI

The **complete test suite requires the local frozen snapshot** at `data/github.duckdb`, verified against SHA-256 `2a063cab4176b97cfd00ea8e92932c64346127ba1da4b120452fb48236c25812`. The file is 140,783,616 bytes (140.783616 MB / 134.26171875 MiB), is ignored by Git, and is obtained using the frozen-snapshot instructions above.

When that file is absent, `tests/conftest.py` skips only the explicitly inventoried frozen-snapshot tests: 16 boundary/replay cases in `test_v4_bounds.py` and 16 reference-execution/generation cases in `test_v4_generation.py` (32 parameterized cases total). Each skip explains the missing input and how to obtain it. Pure unit tests, parser/scheduler substitute tests, and tests that create their own temporary databases continue to run. The mocked finite-generation failure test also needs the real snapshot because the generator hashes its bytes.

This guard checks absence only. An existing corrupt database, an inaccessible path, SQL errors, and assertion failures are not converted into skips. With the snapshot present, all existing assertions execute unchanged. A green snapshot-free CI run validates only the remaining tests; it does **not** establish that the complete frozen-data integration suite passed. CI currently runs the offline pytest command without downloading the snapshot. Neither test mode requires real API credentials or a model request.

Run offline tests, verify the selected question file, or inspect pending experiment pairs:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B scripts/verify_questions.py eval/github_test_questions_v2.jsonl
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m eval.run_experiment --config all --questions eval/github_test_questions_v2.jsonl --dry-run
```

The dry-run starts no model or MCP session and writes no result files. The verifier executes reference SQL read-only. Do not regenerate frozen results or summaries to reproduce a table; inspect their recorded fields instead. Any future collection needs an isolated working copy and separate result files because the shipped runner uses fixed result paths.

For an explicitly authorized live demonstration, the Streamlit UI reuses config C:

```bash
.venv/bin/streamlit run ui/app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

The standalone CLI currently uses the default B loop and appends to `eval/traces.jsonl`; it is not a config-C experiment command:

```bash
AGENT_REF_DATE=2026-10-22 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m agent.run "How many events of each type occurred from October 8 through October 21, 2026, in UTC?"
```

Both live interfaces contact DeepSeek and incur API usage when a question runs. The code redacts the configured credential from surfaced content. Neither interface is needed to inspect the frozen experiment.

The following SHA-256 values identify the actual local file bytes, not model versions or guarantees of future API reproducibility:

| Frozen artifact | SHA-256 |
|---|---|
| `eval/github_dev_questions.jsonl` | `320688d3a3138dcebf3dbe014376775accc05f7f12c3da6de5235e524ea5fdde` |
| `eval/github_test_questions.jsonl` | `03bf0a9aa44ea56e2d63af2999a79d2c38fca740f70df5feafaffe4e0ef95b58` |
| `eval/github_test_questions_b2.jsonl` | `790e27ba2ccfff6c80e70e22bf6cd79d022250c714ed8847511451eadaf324b9` |
| `eval/github_test_questions_v2.jsonl` | `482af433d897f892274b7e5671f8dfc3beeac5ac38b4247c010fa44cd2177fcf` |
| `eval/glossary.md` | `1a2ce44850529108249fe9970803b1745787ecf37c63136a062a11bb808c3d05` |
| `eval/results/runs.jsonl` | `bb5194dc054ab96c821f8b5509460b54eb719ca6d38af4fbe0e27613e5347b00` |
| `eval/results/runs_v2.jsonl` | `a6400c28fa4d4e937e492f3ac1fa2d653ebcfa7ddaf0227f826772251af801ae` |
| `eval/results/summary.md` | `9c122c5f21f1d15dd1da2237ba9549f10a49c9d541f8cedc1224dcbcffdcdcce` |
| `eval/results/mechanism_probe.jsonl` | `081e290f4a06291ed2cf963ff468167ce4409b3f88e6125b745acc285c62d291` |
| `data/github.duckdb` | `2a063cab4176b97cfd00ea8e92932c64346127ba1da4b120452fb48236c25812` |
| `eval/v3_questions.jsonl` | `d663207daa8095a0b55efe5425456ee8f427077dbd54311718f1591c1515c3d6` |

The database file is ignored by Git and distributed through the [v1.0-freeze Release](https://github.com/meiming2019-web/github-activity-agent/releases/tag/v1.0-freeze), rather than committed to the repository.

