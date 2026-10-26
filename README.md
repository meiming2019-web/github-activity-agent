# GitHub Activity Query Agent

[![tests](https://github.com/meiming2019-web/github-activity-agent/actions/workflows/tests.yml/badge.svg)](https://github.com/meiming2019-web/github-activity-agent/actions/workflows/tests.yml)

Ask plain-English questions about GitHub activity — *"which Rust projects gained
the most stars last week?"* — and get answers computed from real GH Archive data
by an agent that writes and executes its own SQL against DuckDB.

The point of this project is not the agent. It's **how the agent was measured**:
the configurations vary the scaffolding (loop, tools, context, error handling),
while using a floating model alias. Preregistered endpoints, exploratory
observations, and post-registration adjudications are reported separately;
insufficient evidence is reported as such.

## Quickstart

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt

# frozen data snapshot (distributed via GitHub Release)
mkdir -p data
# download github.duckdb.gz from the v1.0-freeze Release into data/, then:
gunzip data/github.duckdb.gz
printf '2a063cab4176b97cfd00ea8e92932c64346127ba1da4b120452fb48236c25812  data/github.duckdb\n' | shasum -a 256 -c -

# your key goes in .env (gitignored), never in code
echo 'DEEPSEEK_API_KEY=...' > .env

# run the local UI (contacts DeepSeek; costs API usage)
.venv/bin/streamlit run ui/app.py --server.address 127.0.0.1
```

Run the offline test suite (no credentials, no database needed — snapshot-bound
tests skip themselves with an explicit reason):

```bash
.venv/bin/python -B -m pytest -q -p no:cacheprovider
```

## How it works

```text
Question
  -> A: one SQL-generation request
     B/C: bounded tool-calling loop (agent/loop.py)
        -> C only: keyword glossary lookup (agent/context.py)
        -> stdio MCP server (agent/mcp_server.py) -> read-only DuckDB
        -> client-side submit_answer -> MCP run_query
  -> submitted SQL + rows -> offline grader (eval/grader.py)
```

- Four read-only MCP tools: `list_tables`, `describe_table`, `sample_values`,
  `run_query`. `submit_answer` and `lookup_glossary` are client-side.
- SQL is checked against a sqlglot allowlist; DuckDB opens read-only; queries
  are timed out and results bounded. These controls constrain the query
  interface — they are not a complete sandbox.
- Data: a frozen 14-day GH Archive snapshot (2026-10-08 → 2026-10-22 UTC),
  28,203 events across 100 repositories. The metrics glossary
  ([eval/glossary.md](eval/glossary.md)) defines every metric the agent may use.

## Live mode

An opt-in live mode (`AGENT_MODE=live`) serves recent complete UTC days from an
isolated database, with hourly incremental ingestion and dynamic date context.
Eval mode stays frozen and unchanged. See [docs/live-mode.md](docs/live-mode.md).

## Results at a glance

Five harness configurations over a frozen 300-question set. A/B were collected
separately from the C-family runs; the requested model alias was the same, but
its provider version was not pinned. This table is descriptive:

| Config | What it adds | Accuracy | Tokens per correct answer (derived) |
|---|---|---:|---:|
| A | one-shot, full glossary | 78.67% | 17.1K |
| B | + bounded retry loop | 83.67% | 60.4K |
| C | + on-demand glossary lookup | 89.00% | 70.3K |
| C2.1 | + per-question date injection | 89.67% | 64.8K |
| C3.1 | + actionable error feedback | 91.00% | 64.9K |

Three things we learned:

1. **Observed loop outcomes differ by stratum.** B recorded 63/90 vs 37/90
   correct for A on advanced questions, but a net −11 in window-question
   row-set correctness. These paired final verdicts do not identify a causal
   mechanism or count date-boundary errors.
2. **Per-question date injection improved the operational window-boundary
   endpoint on this targeted distribution.** The preregistered comparison had
   9:0 discordant pairs in favor of C2.1 (exact McNemar p = 0.00390625),
   including an unparseable classification rather than an established semantic
   error. C2.1 had 180/180 submitted window queries classified boundary-correct
   in this run; post-registration adjudications and parser limits remain disclosed.
3. **Evidence for error feedback remains insufficient.** C3.1 had 2:0
   discordant recovery pairs in its favor over C2.1 (p = 0.5). The paired
   subset is underpowered; this does not establish equivalence or no effect.

One more lesson, from the early rounds: across two 30-question batches the
configurations ranked one way in the first, and the second batch reversed it. Reporting only
the first batch would have told a different story — which is why questions,
data, and results are frozen and every grading correction is disclosed in an
errata trail instead of quietly edited.

## Why trust these numbers

- **Preregistered** endpoints and analysis plan before any v4 run
  ([eval/v4_preregister.md](eval/v4_preregister.md)).
- **Blinded collection**: 1,080 v4 raw run records committed before grading.
- **Explicit configuration differences**, with A/B collected separately from
  the C-family runs; the five-configuration ladder is descriptive.
- **Repeat-run flip substudy** to size run-to-run stochasticity.
- **Hash ledger** over the snapshot, questions, results, and reports; raw run
  records are committed (the exploratory log is stored gzipped).
- Post-registration adjudications, parser limits, and negative results are
  disclosed in the reports, not buried. Full account:
  [eval/v4_report.md](eval/v4_report.md) ·
  [eval/v4_ab_exploratory.md](eval/v4_ab_exploratory.md).

## Limitations

- One frozen snapshot of 100 top repositories; a templated question
  distribution. This does not establish free-form NL robustness.
- One model, one provider; `deepseek-chat`/`deepseek-flash` are floating
  aliases, so provider-side drift between run days cannot be ruled out.
- Accuracy comparisons other than the two preregistered endpoints are
  descriptive only, including the ladder table above. Operational
  post-registration adjudications and parser limitations remain disclosed
  for the endpoints; secondary confidence intervals are descriptive.

## Documentation map

| Want to know | Read |
|---|---|
| What was preregistered, and the claim language allowed by it | [eval/v4_preregister.md](eval/v4_preregister.md) |
| Full v4 results, guardrails, adjudications, sensitivity analyses | [eval/v4_report.md](eval/v4_report.md) |
| The exploratory A/B runs (kept out of v4's claims) | [eval/v4_ab_exploratory.md](eval/v4_ab_exploratory.md) |
| Earlier rounds: 60-question ablation, mechanism probes, re-run audit | [eval/results/summary.md](eval/results/summary.md), [eval/c2_on_v2_regression.md](eval/c2_on_v2_regression.md), [eval/c3_on_v2.md](eval/c3_on_v2.md) |
| Metric and date-semantics definitions | [eval/glossary.md](eval/glossary.md) |
| Live mode: windows, ingestion, scheduling | [docs/live-mode.md](docs/live-mode.md) |
| Rebuilding the snapshot, CI behavior, full command reference | [docs/REPRODUCING.md](docs/REPRODUCING.md) |

## References

- Yao et al., [τ-bench](https://arxiv.org/abs/2406.12045) — its `pass^k`
  framing motivates distinguishing success on one trial from reliability
  across trials.
- Li et al., [BIRD](https://arxiv.org/abs/2305.03111) — motivates attention to
  database values and external knowledge; this workload is not a BIRD
  evaluation.