# C3 Phase A: whitelist feasibility and error-hint mapping draft

**Status: Phase A complete; mappings pending user review. Phases B, C and D have not started.** This document records source inspection and offline feasibility analysis only. No agent, model API, dependency installation or C3 implementation was run. The five queries below are feasibility-only artifacts and must not be inserted into runtime hints or prompts.

## Evidence and method

The current agent/mcp_server.py was read in full. The query and metadata allowlists, AST traversal, scope resolution, constant-generator checks, limit planning, connection setup, timeout, serialization and four registered tools were inspected. Existing event/repository column names and types were read through the unchanged metadata tool functions.

Each constructed candidate was passed to mcp_server.validate_sql before any execution. A rejected candidate would not have been executed directly; all five initial candidates passed, so no rejected candidate or alternate attempt was needed. Each accepted candidate and its unchanged reference SQL were then executed once directly in bounded read-only DuckDB. Candidate SQL was not rewritten for execution.

The existing connection factory supplied read_only=True, memory_limit=2GB, threads=2, disabled external access and disabled extension auto-install/load. Each direct statement had a ten-second interruptible deadline; fetching was bounded at the existing row cap plus one sentinel. All candidate and reference results were below the cap.

Comparison used the actual unchanged eval.grader.grade_run function. The just-executed reference object was supplied to its reference reader to avoid executing the same reference twice; no grader source or comparison rule changed. The candidate result was a feasibility comparison input, not an agent run or experiment record. V2 column-name pinning/value matching, duplicate-preserving unordered multiset comparison, float relative tolerance of 1e-6 without an absolute tolerance, and status/shape/truncation checks were retained. Every candidate matched by column_names. This does not establish universal SQL equivalence on other data.

## Complete current allowed surface

### Tables, scopes and tool boundaries

| Boundary | Actual allowed relations |
|---|---|
| run_query physical query sources | Unqualified events and repos only: QUERY_TABLES = {(empty schema, events), (empty schema, repos)}. |
| describe_table and sample_values | events, repos and ingest_log, using the fixed TableName literal input. These metadata permissions do not extend run_query. |
| Internal list_tables catalog query | information_schema.tables only, through its separate CATALOG_TABLES set and fixed CATALOG_SQL. It filters the current database/main schema and the three known names. This is not a user-query permission. |

CTE/subquery scopes are resolved separately from physical tables. Defined CTE aliases are not treated as additional physical table permissions. Arbitrary schema/catalog relations, paths and system tables are excluded. For analytical queries, even a main-qualified table spelling does not match the empty-schema allowlist. Catalog/schema-qualified columns are explicitly rejected. Physical table names are normalized to lowercase during scope checking.

Only four tools are registered: list_tables, describe_table, sample_values and run_query. The client-side submission contract is not another MCP tool. Metadata identifiers come from a strict fixed literal type and are quoted before use. The execution path rejects views masquerading as analytical base tables.

### Complete accepted AST construct names

These are the exact SAFE_NODES entries, not a claim that every arbitrary combination of them is valid DuckDB syntax:

```text
Select From Table TableAlias Identifier Column Star Alias Literal Null Boolean
    Paren Subquery CTE With Join Where Group Having Qualify Order Ordered Limit Offset
    Window WindowSpec Distinct Filter EQ NEQ GT GTE LT LTE And Or Not Is In Between
    Like ILike Add Sub Mul Div IntDiv Mod Neg Tuple DataType DataTypeParam Interval Var Case
```

The root must be one Select expression, optionally WITH. Multiple statements, non-SELECT roots and recursive WITH are rejected. VALUES and UNION are not included. An otherwise allowed parent cannot hide a rejected node in a subquery, CTE or expression: validation walks the full tree.

### Complete accepted canonical function names

These are the exact SAFE_FUNCTIONS entries. sqlglot canonicalization determines the name checked; Anonymous functions use their uppercased source name. This is an allowance list, not proof that every native spelling, argument list or type is supported:

```text
COUNT COUNT_IF SUM AVG MIN MAX MEDIAN STDDEV STDDEV_POP STDDEV_SAMP VAR_POP VAR_SAMP
    ABS ROUND CEIL FLOOR COALESCE NULLIF LOWER UPPER LENGTH CHAR_LENGTH CONCAT
    CAST TRY_CAST CASE IF DATE_TRUNC TIMESTAMP_TRUNC EXTRACT
    CURRENT_DATABASE ROW_NUMBER RANK DENSE_RANK LAG LEAD FIRST_VALUE LAST_VALUE
    ARRAY ARRAY_AGG JSON_EXTRACT JSON_EXTRACT_SCALAR GENERATE_SERIES
```

CURRENT_DATABASE remains allowed because the internal catalog query uses it. CURRENT_DATE and CURRENT_TIMESTAMP are absent. EXISTS and unlisted file/network readers are absent. The function rule does not make a scalar function an allowed table function.

### Table functions and exact constant-argument rule

The sole permitted table-function AST is exp.GenerateSeries. Its end-exclusive flag is rejected explicitly, so range is not admitted through sqlglot normalization. Every other non-Identifier table source is rejected.

The recursive constant predicate accepts exactly:

- exp.Literal;
- exp.Interval whose this recursively passes;
- exp.Cast whose this recursively passes;
- exp.Paren whose this recursively passes.

Columns, subqueries, arithmetic, other functions, NULL and Boolean nodes do not satisfy that predicate. Exact types matter: permitting TRY_CAST generally does not make exp.TryCast an accepted generator-argument wrapper. A negative expression parsed as Neg is not an accepted constant argument either. Timestamp/date literal syntax can parse as Cast(Literal) and is accepted. Interval/unit and cast-type syntax still must pass the overall AST checks and native binding. Constant acceptance does not itself prove sensible cardinality or a valid DuckDB overload.

GenerateSeries sources are skipped only in physical-table scope checking; their arguments still undergo the checks above. The constant-argument check applies specifically when GenerateSeries is the this of a Table node; it is not a universal argument rule for scalar function calls. Normal table-alias-qualified columns remain allowed; the rejected column qualifiers are schema/catalog qualifiers. Scalar ARRAY/ARRAY_AGG allowance does not permit UNNEST or other array-expanding table functions.

### Limits, execution safety and result representation

- Default analytical row cap: 200. Without top-level LIMIT, logical SQL gets LIMIT 200 and execution SQL uses a bounded 201-row lookahead. Returned rows are capped and omitted rows set truncated=true.
- A supplied top-level LIMIT must be a nonnegative integer Literal without limit options. Smaller/equal explicit limits are retained; larger ones execute with the bounded sentinel limit. LIMIT syntax is checked separately from the general AST allowance. OFFSET has no additional integer-literal check in this function; DuckDB binding/execution still applies.
- DuckDB connections are read_only=True with memory_limit=2GB, threads=2, enable_external_access=False, autoinstall_known_extensions=False and autoload_known_extensions=False.
- A per-statement watchdog interrupts at ten seconds, repeats interruption until completion and is joined/cleaned before connection close. No shared stale timer or background query is accepted as a successful timeout response.
- Metadata sample results are capped at three rows; describe_table uses LIMIT 0; list_tables uses its fixed bounded catalog statement.
- Models forbid extra fields, use strict validation and disallow non-finite output numbers. QueryInput requires nonempty SQL. Invalid table literals are rejected before identifier interpolation.
- Result conversion preserves strings/bools/integers/null, uses ISO dates/times, exact decimal text, finite floats, null for non-finite numbers, seconds for timedeltas, hex for bytes, and recursive list/dictionary conversion. Query output columns retain database order.
- Parser/validator failures and native DuckDB errors are surfaced as tool errors. Native type, column, binding or dialect support is not repaired by the validator. These layers reduce exposure but are not a complete sandbox proof.

Source locations: table/constants and lists at agent/mcp_server.py:20–46; validation at :103–171; serialization at :174–192; connection and execution at :195–250; tool definitions at :256–288.

### Actual analytical schemas

**events**

| Column | DuckDB type |
|---|---|
| event_id | VARCHAR |
| repo_id | BIGINT |
| repo_name | VARCHAR |
| type | VARCHAR |
| actor | VARCHAR |
| created_at | TIMESTAMP |
| payload_json | VARCHAR |

**repos**

| Column | DuckDB type |
|---|---|
| repo_id | BIGINT |
| name | VARCHAR |
| language | VARCHAR |
| topics | VARCHAR |
| stars | BIGINT |
| forks | BIGINT |
| open_issues | BIGINT |
| created_at | TIMESTAMP |
| fetched_at | TIMESTAMP |

## Reference SQL compatibility audit

All 60 reference_sql values from eval/github_test_questions_v2.jsonl were independently passed through the current validate_sql. Results: 60 accepted, zero rejected. Rejected question IDs/errors: none. This was a compatibility audit; only the five target references were executed in this task.

A rejected reference spelling would not prove that its natural-language task has no legal equivalent. No question is labeled unsatisfiable from a reference rejection, and no score ceiling is inferred from rejection counts. Structural impossibility is not established. The five demonstrations below prove an existing legal path on the frozen data for their respective tasks; they do not predict whether an agent will discover that path.

## Demonstrated feasible paths

| Question | Candidate validation | Candidate execution shape | Reference execution shape | V2 comparison | Truncated |
|---|---|---|---|---|---|
| t07 | PASS, before execution | 7 rows × 2 columns | 7 rows × 2 columns | Equal; column_names | No / No |
| t20 | PASS, before execution | 1 rows × 1 columns | 1 rows × 1 columns | Equal; column_names | No / No |
| t24 | PASS, before execution | 14 rows × 3 columns | 14 rows × 3 columns | Equal; column_names | No / No |
| u24 | PASS, before execution | 14 rows × 4 columns | 14 rows × 4 columns | Equal; column_names | No / No |
| u30 | PASS, before execution | 7 rows × 5 columns | 7 rows × 5 columns | Equal; column_names | No / No |

Exact output columns/types (candidate and reference agree):

- t07: day_of_week BIGINT, event_count BIGINT.
- t20: event_count BIGINT.
- t24: activity_date DATE, new_stars BIGINT, cumulative_new_stars HUGEINT.
- u24: event_date DATE, push_count BIGINT, prev_day_push_count BIGINT, dod_change BIGINT.
- u30: event_date DATE, daily_forks BIGINT, running_total_forks HUGEINT, daily_creates BIGINT, running_total_creates HUGEINT.

Each candidate obtains its values by querying the database; no observed answer value is hardcoded. All five candidates validated on their first attempt. There were five candidate executions and five unchanged reference executions, plus the two bounded schema reads. No rejected candidate was executed.

### t07 — feasibility analysis only

Project each event to its UTC date, then group using the allowed EXTRACT operation for the requested weekday convention. No unsupported weekday helper function is needed.

**Feasibility-only SQL. Do not insert this query, its question identifiers, literals or predicates into runtime hints.**

```sql
WITH activity AS (
    SELECT CAST(created_at AS DATE) AS utc_day
    FROM events
    WHERE created_at >= TIMESTAMP '2026-10-08 00:00:00'
      AND created_at < TIMESTAMP '2026-10-22 00:00:00'
)
SELECT EXTRACT(ISODOW FROM utc_day) AS day_of_week,
       COUNT(*) AS event_count
FROM activity
GROUP BY EXTRACT(ISODOW FROM utc_day)
ORDER BY day_of_week
```

Observed validation: PASS. Direct read-only execution: SUCCESS. Reference comparison: equal under the existing v2 grader; no truncation.

### t20 — feasibility analysis only

Select catalog keys with the frozen text-topic matching convention, then join those keys to the requested event types and interval. This avoids array-expanding table functions. The textual topic pattern follows the frozen reference convention; it is not claimed to be a universal JSON-membership test on arbitrary catalogs.

**Feasibility-only SQL. Do not insert this query, its question identifiers, literals or predicates into runtime hints.**

```sql
WITH selected_repositories AS (
    SELECT repo_id
    FROM repos
    WHERE LOWER(COALESCE(topics, '')) LIKE '%"ai"%'
       OR LOWER(COALESCE(topics, '')) LIKE '%machine-learning%'
)
SELECT COUNT(e.event_id) AS event_count
FROM selected_repositories r
JOIN events e ON e.repo_id = r.repo_id
WHERE e.created_at >= TIMESTAMP '2026-10-17 00:00:00'
  AND e.created_at < TIMESTAMP '2026-10-22 00:00:00'
  AND (e.type = 'PushEvent' OR e.type = 'PullRequestEvent')
```

Observed validation: PASS. Direct read-only execution: SUCCESS. Reference comparison: equal under the existing v2 grader; no truncation.

### t24 — feasibility analysis only

Generate the full constant calendar, left-join daily event ranges and count distinct actors within each day. The subsequent allowed SUM window computes a running total while retaining zero-event days.

**Feasibility-only SQL. Do not insert this query, its question identifiers, literals or predicates into runtime hints.**

```sql
WITH calendar AS (
    SELECT d AS day_start
    FROM generate_series(
        TIMESTAMP '2026-10-08 00:00:00',
        TIMESTAMP '2026-10-21 00:00:00',
        INTERVAL '1 day'
    ) AS g(d)
), counts AS (
    SELECT CAST(c.day_start AS DATE) AS activity_date,
           COUNT(DISTINCT e.actor) AS new_stars
    FROM calendar c
    LEFT JOIN events e
      ON e.created_at >= c.day_start
     AND e.created_at < c.day_start + INTERVAL '1 day'
     AND e.repo_name = 'huggingface/transformers'
     AND e.type = 'WatchEvent'
     AND e.actor IS NOT NULL
    GROUP BY c.day_start
)
SELECT activity_date, new_stars,
       SUM(new_stars) OVER (
           ORDER BY activity_date
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS cumulative_new_stars
FROM counts
ORDER BY activity_date
```

Observed validation: PASS. Direct read-only execution: SUCCESS. Reference comparison: equal under the existing v2 grader; no truncation.

### u24 — feasibility analysis only

Generate the full constant calendar, count events per half-open day with a left join, and use allowed LAG to carry the preceding daily value. The first preceding value remains null rather than being invented as zero.

**Feasibility-only SQL. Do not insert this query, its question identifiers, literals or predicates into runtime hints.**

```sql
WITH calendar AS (
    SELECT d AS day_start
    FROM generate_series(
        TIMESTAMP '2026-10-08 00:00:00',
        TIMESTAMP '2026-10-21 00:00:00',
        INTERVAL '1 day'
    ) AS g(d)
), counts AS (
    SELECT CAST(c.day_start AS DATE) AS event_date,
           COUNT(e.event_id) AS push_count
    FROM calendar c
    LEFT JOIN events e
      ON e.created_at >= c.day_start
     AND e.created_at < c.day_start + INTERVAL '1 day'
     AND e.type = 'PushEvent'
    GROUP BY c.day_start
), shifted AS (
    SELECT event_date, push_count,
           LAG(push_count) OVER (ORDER BY event_date) AS prev_day_push_count
    FROM counts
)
SELECT event_date, push_count, prev_day_push_count,
       push_count - prev_day_push_count AS dod_change
FROM shifted
ORDER BY event_date
```

Observed validation: PASS. Direct read-only execution: SUCCESS. Reference comparison: equal under the existing v2 grader; no truncation.

### u30 — feasibility analysis only

Generate the constant calendar, conditionally count both event types and apply separate cumulative SUM windows. A full date spine retains days with no matching events.

**Feasibility-only SQL. Do not insert this query, its question identifiers, literals or predicates into runtime hints.**

```sql
WITH calendar AS (
    SELECT d AS day_start
    FROM generate_series(
        TIMESTAMP '2026-10-15 00:00:00',
        TIMESTAMP '2026-10-21 00:00:00',
        INTERVAL '1 day'
    ) AS g(d)
), counts AS (
    SELECT CAST(c.day_start AS DATE) AS event_date,
           COUNT(CASE WHEN e.type = 'ForkEvent' THEN e.event_id END) AS daily_forks,
           COUNT(CASE WHEN e.type = 'CreateEvent' THEN e.event_id END) AS daily_creates
    FROM calendar c
    LEFT JOIN events e
      ON e.created_at >= c.day_start
     AND e.created_at < c.day_start + INTERVAL '1 day'
     AND e.type IN ('ForkEvent', 'CreateEvent')
    GROUP BY c.day_start
)
SELECT event_date, daily_forks,
       SUM(daily_forks) OVER (
           ORDER BY event_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_total_forks,
       daily_creates,
       SUM(daily_creates) OVER (
           ORDER BY event_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_total_creates
FROM counts
ORDER BY event_date
```

Observed validation: PASS. Direct read-only execution: SUCCESS. Reference comparison: equal under the existing v2 grader; no truncation.

## Draft generic error mappings — pending approval

This section is derived only from the validator rules and analytical schema. It contains no question IDs, repository names, frozen answer predicates or data-dependent answers. It is a review draft, not implemented feedback. Each entry has exactly three content lines: error category, rule and generic alternative. Alternatives are conditional directions, not universally semantics-preserving rewrites.

Error category: Multiple statements or a non-SELECT root.  
Rule: Accept one SELECT root, optionally with non-recursive CTEs.  
Generic alternative: Express the operation as one supported SELECT with joins or CTEs when that preserves the intended result.

Error category: An unlisted function.  
Rule: Only the published canonical function names are permitted; a permitted name does not validate its native signature.  
Generic alternative: Consider the permitted EXTRACT, CAST, aggregate or window functions for the needed operation; keep unsupported native argument errors unchanged.

Error category: An unsupported VALUES relation.  
Rule: VALUES is outside the accepted AST constructs.  
Generic alternative: Use a relevant named base relation or a permitted constant generator when it represents the intended domain; do not substitute an unrelated observed domain.

Error category: An unsupported UNION or other set-operation node.  
Rule: Set-operation nodes are not included in the accepted AST constructs.  
Generic alternative: Consider conditional aggregation, joins or non-recursive CTEs only after preserving duplicate and null semantics; there is no universal OR-based replacement.

Error category: An unsupported EXISTS expression.  
Rule: EXISTS is not in the accepted function list.  
Generic alternative: A join to appropriately grouped or deduplicated keys, or an anti-join, may express the same relation; account for null keys and duplicate multiplicities.

Error category: A range table source.  
Rule: The end-exclusive range form is explicitly rejected; only the permitted generate_series table source is accepted.  
Generic alternative: Use constant-argument generate_series for a required sequence after checking endpoint semantics, rather than blindly replacing one generator name with another.

Error category: Another table function or external reader.  
Rule: Only named permitted tables and the special generate_series table source are accepted.  
Generic alternative: Query the named base tables with ordinary SELECTs; scalar JSON_EXTRACT or JSON_EXTRACT_SCALAR can serve field access where appropriate, without implying general array expansion is available.

Error category: Non-constant generate_series table-source arguments.  
Rule: Table-source arguments must recursively be exact Literal, Interval(this), Cast(this) or Paren(this) nodes; columns, subqueries and other functions are excluded.  
Generic alternative: Use constant casts and intervals for a complete calendar; DISTINCT CAST(created_at AS DATE) from events covers observed dates only and omits zero-event days.

Error category: An unauthorized table, schema or catalog qualifier.  
Rule: Analytical physical sources are unqualified events or repos; qualifiers and other relations are rejected by the scope checks.  
Generic alternative: Use those base tables and correctly resolved CTE aliases; obtain schema information through the existing metadata tools rather than system-table queries.

Error category: A recursive CTE.  
Rule: Recursive WITH is explicitly rejected.  
Generic alternative: Use a non-recursive relational plan or a permitted constant calendar when it preserves the requested computation; do not assume every recursive problem has such a rewrite.

Error category: An invalid LIMIT expression or option.  
Rule: Top-level LIMIT must be a nonnegative integer literal without extra limit options.  
Generic alternative: Supply an ordinary integer-literal limit when needed; the server still bounds returned rows and exposes truncation.

Error category: A view used as an analytical relation.  
Rule: Named analytical relations must be physical base tables, as checked against the internal catalog.  
Generic alternative: Query the permitted base tables and define derived relations within the same SELECT using non-recursive CTEs or subqueries.

Error category: Another unsupported AST construct.  
Rule: Every node must pass the published construct/function checks.  
Generic alternative: Consult the allowed SELECT, join, grouping, filtering and window surface; no semantics-preserving rewrite is promised for an uncovered construct.

Uncovered/native errors remain passthrough in the proposed design: binder errors, unknown/ambiguous columns, conversion errors, native signature/dialect failures, timeouts and any unrecognized error retain their original text. This draft does not add SQL repair, retries, tools, prompt injection, whitelist expansion or a new execution policy.

## Integrity and hard stop

All 63 pre-existing protected-file hashes match the pre-analysis baseline, including the database, runtime, grader, glossary, all question/reference versions, historical results, v3 deliverables and the C2 regression outputs. Key SHA-256 values:

| Protected artifact | SHA-256 |
|---|---|
| agent/mcp_server.py | 3b55d233b1f8f27c1398df53a75065a456456e97219ac2607e9eb03d44b4d41f |
| eval/grader.py | 34fdf04fb0a75836f78a0e2ec4c90fef4d9b7b5f6c4cab730b00abcbe502dd57 |
| eval/glossary.md | 1a2ce44850529108249fe9970803b1745787ecf37c63136a062a11bb808c3d05 |
| eval/github_test_questions_v2.jsonl | 482af433d897f892274b7e5671f8dfc3beeac5ac38b4247c010fa44cd2177fcf |
| data/github.duckdb | 2a063cab4176b97cfd00ea8e92932c64346127ba1da4b120452fb48236c25812 |
| eval/results/runs_v2.jsonl | a6400c28fa4d4e937e492f3ac1fa2d653ebcfa7ddaf0227f826772251af801ae |
| eval/results/runs_v3.jsonl | b318335647b5037ec217adfae08754a0923bc4b4fd0d00b84b8009ad753f85be |
| eval/results/runs_v2_c2.jsonl | d357ee0c0693efc8f037dd9693e28d20f25ac1fe34c75ee58d65a93c67a05184 |
| eval/c2_on_v2_regression.md | 03689348952ec48f79e422c65327697cc02779167cbac032e57601422e80e7e2 |

Only eval/c3_feasibility.md is delivered in the repository. Temporary analysis evidence remains outside it. No existing file, code, test, whitelist, reference query or dependency was changed; no agent/model call, experiment, git staging, commit or push occurred.

**Pending approval: the generic mappings in this document require user review. Hard stop here. No Phase B implementation, Phase C run or Phase D work is authorized or started.**
