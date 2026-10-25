# v4 SQL Boundary Rubric and Offline Execution Contract

This rubric is locked before v4 collection. The parser is independent of grader.py, context.py, and their boundary helpers. It uses the existing sqlglot DuckDB AST parser and Python standard-library date arithmetic; it never executes SQL, connects to a database, calls a model, or compares reference answer rows. No new dependency is required.

## Primary classifications

The input is the exact final submitted SQL and the question's authorized half-open UTC boundaries. No submitted SQL is not a correct window: the parser returns unparseable, while the preregistered analysis separately excludes missing submissions from Endpoint 1.

| Class | Rule |
| --- | --- |
| correct | One provable effective events.created_at interval equals the authorized inclusive start and exclusive end. |
| start_wrong | The end is correct; the start is missing or differs. |
| end_wrong | The start is correct; the end is missing or differs. |
| both_wrong | A temporal interval is present and both endpoints differ or are missing. |
| no_window_predicate | No effective created_at constraint is found in the supported query; also the required primary path for a control question whose authorized bounds are null. |
| unparseable | Invalid/multiple/non-SELECT SQL, an ambiguous source, unsupported temporal semantics, contradictory bounds, or another case in which the effective interval cannot be established. Unknown never becomes correct. |

## Supported set semantics

- Parse a single DuckDB SELECT, including reachable CTEs and FROM subqueries. Ignore unused CTEs. Resolve qualified aliases and row-preserving projected column aliases back to a physical events.created_at. An unqualified temporal column with multiple sources is ambiguous. Explicit derived-column name lists, modified star projections, same-select temporal aliases, external schemas, reused CTE branches, multiple physical events sources, scalar/correlated subqueries, recursive dependencies, and set operations are conservatively unparseable. This intentionally leaves some valid queries unclassified.
- Accept direct timestamp comparisons >=, >, <, <=, = and BETWEEN, including literal-on-left comparisons. The snapshot's created_at is a UTC DuckDB TIMESTAMP with microsecond precision: > t becomes >= t+1 microsecond and <= t becomes < t+1 microsecond. BETWEEN on timestamps includes both exact timestamp endpoints; an upper midnight is not an inclusive full day. The last representable microsecond before the authorized end is equivalent to the exclusive end.
- Support CAST(created_at AS DATE), DuckDB ::DATE syntax, and DATE(created_at) as represented by sqlglot. DATE comparisons operate on whole UTC days: >= day includes that day, > day begins the next day, <= day includes the full day, and BETWEEN includes both full endpoint days. DATE versus a non-midnight timestamp is conservatively unparseable. Timezone-bearing constants, sub-microsecond precision, timestamp-to-date-to-timestamp transformations, nonliteral times, date_trunc, arithmetic on the column, and other transforms are not guessed.
- Resolve ISO date/timestamp literals, DATE/TIMESTAMP casts, and addition/subtraction of literal whole-day intervals on constants. Dynamic CURRENT_DATE, parameters, scalar expressions, and unresolved types are unparseable when used as temporal operands.
- AND intersects all proven bounds, retaining the tightest constraints. Non-temporal conjuncts do not define a window. OR is supported only when both branches independently prove the identical bounded interval; otherwise it is unparseable, including a branch without a time bound. NOT on a temporal expression is unparseable. Inner-join temporal ON predicates may constrain rows; outer-join temporal ON predicates are not assumed to filter the preserved side.
- Temporal conditions inside aggregate FILTER, CASE, or IF are conservatively unparseable, even when an ordinary WHERE also has the expected bounds; these embedded conditions must not produce a false correct.
- A temporal predicate above aggregation, DISTINCT, LIMIT/OFFSET, QUALIFY, or a window-function projection cannot be pushed down by this parser. Date grouping alone is not a time filter. A standalone calendar skeleton does not establish an events.created_at window.

## Secondary observations and blind spots

For control questions the primary class always remains no_window_predicate, as requested. observed_time_filter independently records true when a filter is detected, false after a supported no-filter parse, or null when detection cannot be established. secondary_parse_status and reason preserve uncertainty. Thus an extra time filter is observable for the control guardrail rather than hidden by the primary control path.

For every reachable generate_series, compare its inclusive end parameter with authorized exclusive end minus one day. The generate_series_end flag is not_present, correct, wrong, unparseable, or not_applicable. Multiple scaffold checks combine conservatively; this secondary flag never changes the primary window category. The parser does not validate the complete query's metric, grouping, session logic, ranking, or answer correctness. No accuracy measurement is performed in Phase B.

## Scheduler contract

The new scheduler does not import run_experiment.py or grader.py. Preparation and imports do not import the model loop, load .env, read API keys, connect to MCP, or create result files. Future execution is behind explicit entry points and requires separate Phase C authorization. The command-line execution branches prompt for a supplied key only when explicitly invoked; no key has been read in Phase B.

- Pass 1: all 300 source-order questions; six configuration permutations, 50 copies each, shuffled with seed 42.
- Pass 2: choose 60 unique IDs with independent subset seed 4201, retain their source order, then shuffle six permutations with 10 copies each using independent order seed 4202. These seeds are declared before schedule creation and stored in its metadata.
- Both passes are frozen together in eval/v4_schedule.jsonl before any run. Resume reads and validates existing assignments, source hash, IDs, workers, pass labels, and exact six-way balance; it never draws new randomness. Each pass assigns question index modulo five to a worker. The same worker executes all three configurations adjacently and creates fresh conversation state for every trial.
- Future pass-1 records go only to eval/results/runs_v4.jsonl; pass-2 records only to eval/results/runs_v4_pass2.jsonl. Pass 2 cannot start until all 900 unique pass-1 identities have a committed trial record, including recorded errors. Completion is not success and is never based on a score. Offline substitute tests use only temporary paths and reject either formal result path.
- C uses frozen shared context and on-demand glossary lookup. C2.1 adds the real question-aware date entry. C3.1 uses exactly the C2.1 context and changes only the loop's existing whitelist-feedback configuration. Each trial has a new trace, fingerprint capture, client and MCP session. Response model names are retained without altering requests. All records receive harness_version="c2.1".
- first-write-wins is a cross-process flock-protected read/check/append/fsync on (question_id, config, pass). Errors are final records too. Committed identities are skipped on resume. A torn trailing line stops collection for manual recovery; it is not silently repaired. This guarantees stored-record uniqueness, not exactly-once external API delivery after a crash before a record was committed; uncommitted in-flight requests remain a transport limitation.
- Initial collection creates block 1. A restart more than 7200 seconds after the latest persisted activity creates a new block marker in the same result file; exactly two hours retains the block. The runner prints only completed-pair counts and never imports scoring code or aggregates outcomes. Raw trace fields are retained for later blinded analysis.
- Smoke is restricted to d01-d15 in the frozen development file and to a nonformal output path. Phase B does not execute even a development smoke. Offline tests use substitute callables and temporary result files only.

## Source fidelity and pending factual wording

The Library preregistration attachment is preserved as raw UTF-8 bytes outside the repository. Only its actual encoded hash placeholders and the two explicitly adjudicated pass-2 edits may change in eval/v4_preregister.md. The attachment states that supporting evidence is "already committed"; existing git status contradicts that phrase, and commit is forbidden. That sentence is preserved pending explicit human wording adjudication; this rubric does not imply a commit happened. Human Round 1 is a historical record, not a sign-off for the regenerated r2 set.
