# Single-agent deferral

Status: Accepted (2026-10-23)

## Context

A planner/executor/critic architecture offers specialization, but adds handoffs, shared-state questions, and coordination failures. Those additions would complicate interpreting this prototype's policy comparisons. With n=60, a reviewer intervention would also change how the available loop budget is spent; this study could not isolate those effects.

## Decision

Use a single agent with a bounded tool loop and defer multi-agent orchestration. Keep A/B as a comparison of interaction policies and B/C as a comparison of glossary delivery policies. These are controlled policy comparisons, not proof that every outcome difference has a uniquely identified elementary cause.

## Alternatives considered

A planner-executor split could separate decomposition from SQL execution, at the cost of another coordination boundary. A critic or reviewer could challenge a proposed answer, but its contribution would need to be separated from additional deliberation and tool opportunities. Neither alternative was experimentally tested here.

## Consequences

The shared loop keeps submission and stopping rules inspectable without an orchestration layer. Terminal failure categories remain visible in recorded outcomes, although missing historical tool traces remain missing. We accept a bounded capability ceiling and defer architecture expansion to future work. Any later multi-agent comparison should state its coordination and budget policy explicitly rather than treating extra agents as a free improvement.
