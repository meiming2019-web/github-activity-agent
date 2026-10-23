# Explicit answer submission

Status: Accepted (2026-10-23)

## Context

An exploratory query can check coverage rather than answer the question. Choosing the last successful query would confuse that check with the intended result. Prose alone leaves the graded row set ambiguous, while continuing exploration without a stopping contract can consume the available budget.

## Decision

For loop configurations B/C, only a successful client-side `submit_answer` execution establishes the graded SQL and rows. Ordinary `run_query` calls remain exploratory. Config A instead executes its one-shot SQL and submits that execution result; it does not call the pseudo-tool. Bound B/C to 12 calls and stop after three consecutive SQL errors. Constrain execution through layered sqlglot AST validation and a DuckDB read-only session, not an AST-only safety guarantee.

## Alternatives considered

The last-query heuristic avoids an explicit action but cannot identify intent reliably. Extracting SQL from final prose would separate the claimed answer from an executed result. Unbounded correction would avoid a fixed stopping point while making spending and terminal outcomes harder to compare.

## Consequences

The submission boundary is inspectable and unambiguous. `no_submission` and `sql_error_exhausted` are countable outcomes rather than informal explanations for missing answers. The contract also rejects further tools after submission, so the agent must choose when exploration is sufficient. This makes a failed or absent submission visible; it does not guarantee semantic correctness or complete isolation.
