# GitHub Activity Query Agent

[![tests](https://github.com/meiming2019-web/github-activity-agent/actions/workflows/tests.yml/badge.svg)](https://github.com/meiming2019-web/github-activity-agent/actions/workflows/tests.yml)

## Project overview

This project answers natural-language questions over a frozen 14-day GH Archive snapshot covering October 8 through October 21, 2026, UTC. The snapshot contains 28,203 events from a top-100-repository universe and stores activity and repository metadata in DuckDB. A self-built stdio MCP server exposes four read-only tools; the client adds an explicit `submit_answer` contract so the scored result comes from the submitted query. DeepSeek's `deepseek-chat` generates SQL, while a separate offline evaluator compares submitted rows with reference-query results.

## Architecture

```text
Question
  -> A: one SQL-generation request
     B/C: bounded tool-calling loop in agent/loop.py
        -> C only: local keyword lookup in agent/context.py
        -> stdio MCP server in agent/mcp_server.py
           -> read-only DuckDB: events / repos
        -> B/C: client-side submit_answer -> MCP run_query
  -> submitted SQL + rows -> offline eval/grader.py
```

The actual MCP tools are `list_tables`, `describe_table`, `sample_values`, and `run_query`. `submit_answer` and config C's `lookup_glossary` are client-side functions, not additional MCP-server tools. Ordinary exploratory queries do not become scoring answers; a successful submission explicitly records its SQL, columns, rows, and truncation flag.

The server checks SQL through a sqlglot allowlist, restricts query relations, opens DuckDB read-only, disables external access, and interrupts timed-out queries. It returns bounded results and reports truncation. These controls constrain the query interface; they are not a complete sandbox claim. `scripts/` contains the download, ingestion, metadata, and question-verification utilities; `eval/` contains evaluation assets and offline grading. Reference answers and glossary content remain outside the database accessible to the agent.

The local Streamlit interface in `ui/app.py` presents config C's answer, submitted SQL, agent trace, and usage statistics. It reuses the existing loop and a local ECharts asset.

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

## References

- Yao et al., [τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains](https://arxiv.org/abs/2406.12045). Its `pass^k` framing motivates distinguishing success on a trial from reliability across trials. This project's agreement audit is not a `pass^k` estimate.
- Li et al., [Can LLM Already Serve as A Database Interface? A BIg Bench for Large-Scale Database Grounded Text-to-SQLs](https://arxiv.org/abs/2305.03111). BIRD motivates attention to database values and external knowledge; this local workload is not a BIRD evaluation.
