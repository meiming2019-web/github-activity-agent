# Hermetic evaluation

Status: Accepted (2026-10-23)

## Context

Live activity data and moving date expressions make a query's meaning change between evaluations. An apparent model difference can instead reflect a changed population, window, or answer key. Comparing SQL text alone would introduce another dependency on spelling and aliases rather than the requested data.

## Decision

Evaluate against the frozen 14-day snapshot and reference date 2026-10-22 (UTC). Express windows as half-open intervals and require literal dates rather than live-clock SQL such as `CURRENT_DATE`. Execute reference SQL at grading time against the read-only snapshot, then compare unordered row multisets while preserving duplicates. Match columns by name first, with the disclosed grader's bounded fallback for unmatched columns.

## Alternatives considered

Live GitHub queries would offer fresher demonstrations but would move the evaluation target. Relative clock expressions would be convenient but would change the frozen task. SQL-string grading would be simpler to inspect, but would conflate query wording with returned values.

## Consequences

Frozen inputs and offline re-grading are reproducible; remote model outputs are not promised to repeat. Stored answer rows made disclosed answer-key and grader errata possible without rerunning the model. The resulting workload has smaller scale and no direct public-leaderboard comparability. Those costs are accepted and disclosed rather than hidden behind a general benchmark claim.
