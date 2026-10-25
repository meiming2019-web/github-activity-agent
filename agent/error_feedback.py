"""Approved deterministic feedback for recognized SQL-whitelist refusals."""

import re


# Copied verbatim from the approved generic mapping block; no feasibility SQL.
MESSAGES = (
    'Error category: Multiple statements or a non-SELECT root.  \n'
    'Rule: Accept one SELECT root, optionally with non-recursive CTEs.  \n'
    'Generic alternative: Express the operation as one supported SELECT with joins or CTEs when that preserves the intended result.',
    'Error category: An unlisted function.  \n'
    'Rule: Only the published canonical function names are permitted; a permitted name does not validate its native signature.  \n'
    'Generic alternative: Consider the permitted EXTRACT, CAST, aggregate or window functions for the needed operation; keep unsupported native argument errors unchanged.',
    'Error category: An unsupported VALUES relation.  \n'
    'Rule: VALUES is outside the accepted AST constructs.  \n'
    'Generic alternative: Use a relevant named base relation or a permitted constant generator when it represents the intended domain; do not substitute an unrelated observed domain.',
    'Error category: An unsupported UNION or other set-operation node.  \n'
    'Rule: Set-operation nodes are not included in the accepted AST constructs.  \n'
    'Generic alternative: Consider conditional aggregation, joins or non-recursive CTEs only after preserving duplicate and null semantics; there is no universal OR-based replacement.',
    'Error category: An unsupported EXISTS expression.  \n'
    'Rule: EXISTS is not in the accepted function list.  \n'
    'Generic alternative: A join to appropriately grouped or deduplicated keys, or an anti-join, may express the same relation; account for null keys and duplicate multiplicities.',
    'Error category: A range table source.  \n'
    'Rule: The end-exclusive range form is explicitly rejected; only the permitted generate_series table source is accepted.  \n'
    'Generic alternative: Use constant-argument generate_series for a required sequence after checking endpoint semantics, rather than blindly replacing one generator name with another.',
    'Error category: Another table function or external reader.  \n'
    'Rule: Only named permitted tables and the special generate_series table source are accepted.  \n'
    'Generic alternative: Query the named base tables with ordinary SELECTs; scalar JSON_EXTRACT or JSON_EXTRACT_SCALAR can serve field access where appropriate, without implying general array expansion is available.',
    'Error category: Non-constant generate_series table-source arguments.  \n'
    'Rule: Table-source arguments must recursively be exact Literal, Interval(this), Cast(this) or Paren(this) nodes; columns, subqueries and other functions are excluded.  \n'
    'Generic alternative: Use constant casts and intervals for a complete calendar; DISTINCT CAST(created_at AS DATE) from events covers observed dates only and omits zero-event days.',
    'Error category: An unauthorized table, schema or catalog qualifier.  \n'
    'Rule: Analytical physical sources are unqualified events or repos; qualifiers and other relations are rejected by the scope checks.  \n'
    'Generic alternative: Use those base tables and correctly resolved CTE aliases; obtain schema information through the existing metadata tools rather than system-table queries.',
    'Error category: A recursive CTE.  \n'
    'Rule: Recursive WITH is explicitly rejected.  \n'
    'Generic alternative: Use a non-recursive relational plan or a permitted constant calendar when it preserves the requested computation; do not assume every recursive problem has such a rewrite.',
    'Error category: An invalid LIMIT expression or option.  \n'
    'Rule: Top-level LIMIT must be a nonnegative integer literal without extra limit options.  \n'
    'Generic alternative: Supply an ordinary integer-literal limit when needed; the server still bounds returned rows and exposes truncation.',
    'Error category: A view used as an analytical relation.  \n'
    'Rule: Named analytical relations must be physical base tables, as checked against the internal catalog.  \n'
    'Generic alternative: Query the permitted base tables and define derived relations within the same SELECT using non-recursive CTEs or subqueries.',
    'Error category: Another unsupported AST construct.  \n'
    'Rule: Every node must pass the published construct/function checks.  \n'
    'Generic alternative: Consult the allowed SELECT, join, grouping, filtering and window surface; no semantics-preserving rewrite is promised for an uncovered construct.',
)


EXACT_ERRORS = {
    "Only one SELECT statement (optionally WITH) is allowed.": 0,
    "Recursive CTEs are not allowed.": 9,
    "Catalog-qualified and schema-qualified columns are not allowed.": 8,
    "Only generate_series is allowed; range is not allowed.": 5,
    "generate_series arguments must be constant literals, intervals, casts, or parentheses.": 7,
    "Table functions are not allowed.": 6,
    "Catalog-qualified and external schema tables are not allowed.": 8,
    "Only named tables and SELECT subqueries are allowed.": 8,
    "LIMIT must be a nonnegative integer literal.": 10,
    "LIMIT must be a nonnegative integer literal without options.": 10,
    "Only physical base tables are allowed; views are not allowed.": 11,
}


def whitelist_feedback(content):
    """Map exact validator diagnostics; preserve uncovered/native errors unchanged."""
    reason = content.removeprefix("Error executing tool run_query: ")
    index = EXACT_ERRORS.get(reason)
    if index is None:
        function = re.fullmatch(r"Function is not allowed: ([A-Z][A-Z_0-9]*)", reason)
        construct = re.fullmatch(r"SQL construct is not allowed: ([A-Za-z][A-Za-z0-9_]*)", reason)
        if function:
            index = 4 if function.group(1) == "EXISTS" else 1
        elif construct:
            node = construct.group(1)
            index = 2 if node == "Values" else 3 if node in {"Union", "Intersect", "Except"} else 12
        elif re.fullmatch(r"Table is not allowed: [^\n]+", reason):
            index = 8
    return MESSAGES[index] if index is not None else content
