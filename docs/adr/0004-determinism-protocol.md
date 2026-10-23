# Determinism protocol

Status: Accepted (2026-10-23)

## Context

A temperature setting expresses a sampling policy, not a provider-level guarantee of bitwise repeatability. A single run is a measurement, but cannot establish its own repeatability. Keeping favorable retries while discarding failures would introduce outcome selection rather than resolve that uncertainty.

## Decision

Request `temperature=0` at every model call site. Record each question/configuration pair once under first-write-wins, including errors. Put probes in separate declared files and never merge them into primary results. Use the separate 60-question config C audit to report observed agreement rather than assume remote outputs repeat.

## Alternatives considered

Higher or varied temperatures could test robustness, but would change the protocol and require separate validation. Repeating attempts until success would select outcomes. Repeated measurements under a predeclared analysis could study variability, but were not part of the frozen primary experiment.

## Consequences

The audit observed 54/60 verdict agreement. We claim no accuracy ranking, and do not infer a variance bound from that agreement. DeepSeek-chat remains a floating alias; provider version drift cannot be ruled out. `temperature=0` may disadvantage loop configurations by reducing useful variation in correction trajectories, but this remains an unverified hypothesis. The five `sql_error_exhausted` cases were loop-only; that observation does not establish temperature as their cause or prove retries deterministic.
