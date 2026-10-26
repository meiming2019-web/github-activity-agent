# Live mode

Live is an independent, opt-in data path. `AGENT_MODE=live` selects it; an absent
`AGENT_MODE` or `AGENT_MODE=eval` keeps the existing UI's frozen config-C context
and reference date 2026-10-22. Unknown modes fail rather than silently selecting
another database. No command below is run automatically.

## Window vocabulary

The reference instant is captured once per question, converted to UTC, and can be
injected in tests. "Today" means its UTC calendar date; today's events are
incomplete and never belong to a supported question window. All bounds are
half-open UTC midnights:

- `the last N days`, integer N from 1 to 14: `[today-N, today)`.
- `last week`: `[today-7, today)`.
- `previous week`: `[today-14, today-7)`.
- Explicit inclusive dates: `2026-10-12 through 2026-10-24`,
  `October 12 through October 24, 2026`, or
  `December 25, 2026 through January 7, 2027`. The exclusive upper bound is the
  stated final date plus one day. Matching is case-insensitive.

An explicit range containing today or a later date is rejected with "Today's data
is incomplete". A range entirely before the preceding 14 complete UTC days is
rejected with "Data has rolled out of retention". Reversed and malformed dates,
N outside 1-14, unsupported temporal syntax, and multiple window mentions are
rejected with a request to use one documented form. An interval partially
outside retention is accepted **without clamping or rewriting** its endpoints.
Its unavailable older portion is disclosed as missing data, not zero activity.

The parser is intentionally conservative, using documented grammar and lexical
rejection of recognizable unsupported expressions (including yesterday, today,
since, past/next periods, month/week/day names and malformed date forms). It is
not a complete arbitrary-language temporal classifier; unrecognized metaphors or
novel paraphrases cannot be claimed detected. Use the explicit forms above for
time-dependent questions. Non-temporal questions receive coverage context but
no fabricated window. Decorative time mentions may also be rejected; clarify
the question instead of silently choosing a window.

Examples for `the last 7 days`:

| Injected now | UTC today | Window |
|---|---|---|
| 2026-11-01T00:01:00Z | 2026-11-01 | [2026-10-25, 2026-11-01) |
| 2026-11-01T23:59:00-07:00 | 2026-11-02 | [2026-10-26, 2026-11-02) |
| 2027-01-01T00:30:00+08:00 | 2026-12-31 | [2026-12-24, 2026-12-31) |

## Data, ingestion, and late arrivals

`data/github_live.duckdb` is ignored by the existing `data/` Git rule. It contains
only events/catalog/ingestion bookkeeping, never evaluation answers or glossary
text. The fixed 100 names come from `repos.txt`. The initial repository catalog
is copied **read-only** from `data/github.duckdb`, preserving its original
`fetched_at`. The UI visibly labels **repo metadata frozen at 2026-10-22**. This
is live event activity with frozen metadata, not refreshed stars or languages.

Retention starts at UTC today minus 14 days; today's completed archive hours are
retained as an ingestion buffer, in addition to the preceding 14 full days.
The current, unfinished hour is not downloaded. Each invocation fetches every
missing retained hour and refetches the latest 24 completed hours, even if an
archive was previously ingested. This also catches gaps after a multi-day outage.
Matching event IDs use first-write-wins deduplication. New late/backfilled IDs
are accepted; the same ID does not overwrite its previously stored payload.
Updates arriving outside the 24-hour refresh horizon are not guaranteed observed.
**Data is as of ingestion time.**

Each hour commits events and its ledger entry atomically. A failed download,
invalid matching event, corrupt gzip, or malformed JSON leaves that hour's
previous committed data intact and returns a nonzero ingestion exit status.
Other hours may succeed. Failed missing hours remain gaps and are retried on the
next invocation; no failure is marked complete. Coverage context lists missing
complete-day hours and the latest successful ingestion timestamp. Even full
hour-file coverage does not prove GH Archive captured every GitHub event.
Old events and ledger entries roll out according to event date/archive date.

Concurrent ingestion is rejected by a nonblocking file lock. Agent queries use
separate read-only connections and the frozen SQL allowlist, memory limits,
external-access restrictions, timeout and row cap. Ingestion alone uses a trusted
writable connection for its fixed schema and parameterized DML; user SQL never
reaches that connection. A DuckDB read/write process lock conflict is an error,
not permission to open the frozen DB or bypass read-only access. Retry manually
or schedule ingestion between interactive requests.

Run explicitly from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B scripts/ingest_live.py
AGENT_MODE=live .venv/bin/streamlit run ui/app.py
AGENT_MODE=live .venv/bin/python -B -m agent.run_mode "Count collaboration_events for the last 7 days"
AGENT_MODE=eval .venv/bin/python -B -m agent.run_mode "Count collaboration_events for the last 7 days"
```

For hourly scheduling, configure your own scheduler to execute the first command
at minute 15 of every hour, with the repository as its working directory. A cron
example (replace the absolute path) is:

```cron
15 * * * * cd /absolute/path/github-activity-agent && PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B scripts/ingest_live.py
```

No scheduler is installed by this implementation. Initial backfill downloads many
hourly public archives; ingestion needs network access but no API key. UI/CLI
question execution uses the existing DeepSeek credential and incurs model usage;
development tests use fake clients and never read real credentials or download.

The new mode-aware CLI prints a sanitized result to stdout and writes no shared
trace file. The legacy `agent.run` CLI remains unchanged: it is not mode-aware,
uses `AGENT_REF_DATE` (otherwise current UTC date), and writes its existing eval
trace path. Use `agent.run_mode` for mode-aware operation. UI mode changes clear
the displayed question, result and run history; live examples do not reuse dated
eval development prompts. Each question creates fresh connections and state.

Metric definitions are read verbatim from the metric section of
`eval/glossary.md` at runtime. Live lookup cannot return its frozen Time
conventions or Dataset scope sections. Those definitions are not copied into
new files, and the glossary remains unchanged.

## Scope of evidence

All v4 conclusions were validated on the frozen snapshot and declared template
distribution. They **do not automatically apply to live mode**, new dates, delayed
or missing archives, different activity, or stale repository metadata. The new
mode has offline engineering tests, not a new accuracy evaluation.
