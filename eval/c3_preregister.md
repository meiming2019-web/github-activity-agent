# C3 preregistration

## Nature of the evidence

The 60-question set has already been seen. This round provides regression-level evidence, not a confirmatory experiment.

## Hypothesis H

Actionable error feedback can reduce sql_error_exhausted and revive previously circuit-broken questions without relaxing the whitelist.

## Primary endpoint

The revived count X/5 among t07, t20, t24, u24 and u30. A question is revived if and only if its run successfully submits an answer and is graded correct.

## Secondary endpoints

- Total score X/60.
- sql_error_exhausted count.
- Mean number of steps to first success after an error.
- Tool call count.
- Prompt and completion tokens.

## Guardrail

The number of C2-correct to C3-incorrect transitions is expected to be <= 1. If it exceeds 1, suspend conclusions pending manual investigation.

## Decision rules

- Use the existing deterministic grading path: successfully submitted MCP result rows versus reference rows.
- Report transitions in both directions: incorrect to correct and correct to incorrect.
- Do not calculate p-values.
- Ties and negative findings are reportable.

## Phase A unsolvable-question list and handling

Established unsolvable questions: none.

Phase A found that all 60 reference SQL statements passed validation, and all five constructed probes passed validation and matched their references. No structural impossibility was established. A rejection of one reference spelling would not prove that its question has no legal solution.

There are no established unsolvable questions requiring special handling or exclusion; the total-score denominator remains 60. No score ceiling is inferred from reference SQL compatibility.

## Appendix: frozen approved feedback mapping (verbatim)

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
