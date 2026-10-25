# v4 Phase A — Step 0 Glossary Audit

## Decision

**BLOCKED — stop the entire Phase A at Step 0, pending human adjudication.**

The frozen glossary does not define any of the four candidate expressions explicitly named in the request: `last 3 days`, `last 14 days`, `past two weeks`, or `since <date>`. The existing seven-day rule is not a general last-N-days rule. Dataset coverage is not a definition of a relative phrase. No candidate was silently removed, assigned inferred semantics, or replaced to make this gate pass.

This document audits proposed vocabulary before generator design. No generator, template inventory, boundary implementation, question set, or downstream tests have been created. Therefore the mapping below covers all time expressions defined in the glossary and all four explicitly requested candidates; it is not a claim that an implemented generator's vocabulary has been validated.

## Source and preflight

- Source: `eval/glossary.md`, read in full, 107 lines.
- Source SHA-256: `1a2ce44850529108249fe9970803b1745787ecf37c63136a062a11bb808c3d05`.
- Repository: `/Users/meiming/workspace/github-activity-agent`.
- Repository instructions and `README.md` were read. No applicable `.agents` directory or repository `.codex` instruction directory was present; no additional local skill instructions were discovered.
- Initial `git status --porcelain=v1 -uall`: empty (clean).
- Before auditing, an integrity baseline recorded SHA-256 for 17,053 existing regular files and the targets of 3 symlinks, including tracked artifacts, ignored traces, database bytes, raw data, and the local virtual environment.
- Exclusions: Git internal metadata, `.env`, `.env.example`, and two virtual-environment certificate bundles named `cacert.pem`. Environment and certificate files were not read or loaded. Secret-like files were excluded from content hashing.
- The baseline was stored outside the repository at `/tmp/github_activity_v4_baseline.json`; it is verification evidence, not an additional project deliverable.
- Database SHA-256 recorded solely for file-integrity verification: `2a063cab4176b97cfd00ea8e92932c64346127ba1da4b120452fb48236c25812`. The database was not opened or queried. No actual minimum/maximum event dates were derived, and no snapshot-range claim below is presented as an empirical query result.

## Verbatim glossary evidence

The following passages are copied from the frozen source. Line numbers refer to that source.

### E1 — time conventions, lines 8–19

```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

### E2 — dataset coverage, line 24

```text
- Coverage: 14 full UTC days, `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00`.
```

### E3 — catalog time semantics, lines 69–72

```text
- `stars`, `forks`, `open_issues` BIGINT — catalog counts as of `fetched_at`.
  They are snapshot values, not live counts, and not restricted to the event window.
- `created_at` TIMESTAMP — repository creation time, UTC; may be NULL.
- `fetched_at` TIMESTAMP — when this catalog snapshot was fetched.
```

### E4 — event window versus catalog snapshot, lines 103–105

```text
- Star-related catalog fields (`stars`) describe the snapshot at `fetched_at`; the
  metric `new_stars` describes event activity inside a window. They answer different
  questions and must not be mixed.
```

## Defined expressions and boundary semantics

Bounds in this table are documentation transcriptions or direct combinations of the quoted rules, not executable boundary calculations or database observations. All interval endpoints below are UTC midnight; `[start, end)` includes start and excludes end.

| Expression or convention | Glossary entry wording | Defined meaning / boundary | Audit status |
| --- | --- | --- | --- |
| `today` / `reference_date` | E1: `reference_date` = **2026-10-22**. Every question treats this date as "today". | Fixed reference date `2026-10-22`; no standalone "today" event window is specified. | Reference anchor defined; do not invent a today-window template. |
| All time windows | E1: Time windows are half-open intervals: `created_at >= start AND created_at < end`. | Inclusive start, exclusive end; all timestamps UTC. | General boundary convention defined; does not choose endpoints for undefined phrases. |
| `The last 7 days` | E1: "The last 7 days" means the 7 full UTC days before `reference_date`. | `[2026-10-15, 2026-10-22)`. | Defined, specifically for seven days. |
| Explicit inclusive date range, including `October 8 through October 21, 2026` | E1: An explicit range like "October 8 through October 21, 2026" means the stated interval, with "end date inclusive" and "the exclusive bound is the next day". | Example: `[2026-10-08, 2026-10-22)`; the rule describes a supplied start and inclusive end date. | Defined; not an open-ended `since` rule. |
| `Previous week` | E1: "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC). | `[2026-10-08, 2026-10-15)` by the stated dates and general half-open convention. | Defined for the frozen reference; no general calendar-week algorithm specified. |
| `last week` | E1: "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC). | `[2026-10-15, 2026-10-22)` by the stated dates and general half-open convention. | Defined for the frozen reference. |
| `UTC date` | E1: A "UTC date" of an event is `CAST(created_at AS DATE)`. | Date projection for grouping; does not select a time window. | Defined date convention. |
| Dataset coverage / `14 full UTC days` | E2, quoted in full above. | Documented coverage `[2026-10-08, 2026-10-22)`. | Dataset fact as documented, not a `last 14 days` or `past two weeks` phrase definition; actual extrema not queried. |
| Catalog counts `as of fetched_at` | E3 and E4, quoted in full above. | Catalog snapshot time, distinct from event-window activity. | Defined field semantics; no relative-window definition. |

Metric sections refer to a "requested time window" and require thresholds to be assessed separately in each window; they do not define additional window expressions. Event and repository timestamps are identified as UTC. No other relative-window definitions appear in the complete source.

## Required candidate-by-candidate gap audit

The neighboring source text below is evidence of what exists, not authorization to extend it. The full original passages are preserved in E1–E4.

| Requested candidate | Exact relevant glossary text | Missing definition | Specific human decision required |
| --- | --- | --- | --- |
| `last 3 days` | E1: ``- "The last 7 days" means the 7 full UTC days before `reference_date`:`` | No three-day entry and no parameterized `last N days` rule. The seven-day entry cannot establish three-day endpoints. | Explicitly disallow this phrase, or authorize a separate versioned semantic specification stating its anchor, full UTC dates versus elapsed duration, inclusion/exclusion of the reference day, and exact inclusive/exclusive endpoints. |
| `last 14 days` | E2: ``- Coverage: 14 full UTC days, `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00`.`` E1 defines "The last 7 days". | No fourteen-day relative-window entry. Equal numeric duration or possible equality to coverage does not define the phrase. | Explicitly disallow this phrase, or authorize a separate versioned definition with its anchor and endpoints, stating whether it means a relative window or the observed complete snapshot and how snapshot coverage affects it. |
| `past two weeks` | E1: `- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).` | No `past two weeks` entry or alias mapping. Neither the union of the two named weeks nor a rolling fourteen-day interpretation is authorized. | Explicitly disallow this phrase, or choose and specify its intended meaning: two calendar weeks, fourteen full UTC dates before an anchor, or the union of the two frozen named weeks; provide exact endpoints and alias authorization if applicable. |
| `since <date>` | E1: `- An explicit range like "October 8 through October 21, 2026" means` and the inclusive-end explanation in E1. | No `since` entry; an explicit range supplies both endpoints, whereas this phrase omits the end. Start-date inclusion, permitted date form, and terminal bound are unspecified. | Explicitly disallow this phrase, or authorize a separate versioned definition specifying the supplied date's meaning, inclusive/exclusive start, and terminal bound (including whether the reference date or snapshot end controls it). |

**No proposed interpretation in the decision column has been adopted.** Human authorization must resolve these candidates explicitly. The frozen `eval/glossary.md` remains unchanged; any decision requiring a different source of semantics must also explicitly resolve the current requirement that each generator phrase map to that frozen glossary. This audit does not authorize a replacement glossary, new semantic file, or an altered Phase A scope.

The requested `literal`, `colloquial`, and `distractor` layers have not been drafted. A colloquial paraphrase cannot be presumed to be a licensed synonym, and an irrelevant time mention cannot be presumed harmless before a concrete template is reviewed. After adjudication, every concrete time-window wording would still need a mapping to an authorized original entry. Advanced SQL family names such as daily trend or running total do not supply the missing window semantics.

## Gate consequences and completion report

### 1. Files delivered and responsibilities

- `eval/v4_glossary_audit.md` — the sole new repository file: frozen-source evidence, complete defined-time inventory, the four mandatory candidate checks, explicit adjudication questions, and the Step 0 stop decision.
- No code functions or third-party dependencies were added. The temporary baseline is necessary to verify the requested before/after preservation of existing files and is kept outside the repository.

### 2. Requirements not executed and reasons

All work below is **not executed because Step 0 failed**:

- Generator, CLI arguments, seed behavior, templates, and generation logic.
- Database min/max query and empirical snapshot-range derivation. Database bytes were hashed only for preservation evidence.
- Independent boundary implementation and injection-side cross-check.
- Question generation: window layer `0/180`; targeted advanced SQL `0/60`; non-targeted advanced SQL `0/30`; time-free controls `0/30`; total `0/300`. No template families were instantiated, so per-family generated counts are not applicable.
- Reference SQL generation/execution, grader reuse assessment, and row normalization.
- Nonempty/nonzero, shifted-boundary sensitivity, and deterministic Top-N assertions.
- Regeneration: no attempts, no events, and no `eval/v4_regen_log.jsonl`; this is not a measured rejection rate.
- Text deduplication and glossary/template overlap audit; no `eval/v4_overlap_audit.md` was created.
- Manual review package: `eval/v4_sample_review.md` was not created.
- Downstream tests: no pytest run, no test functions created, and no full-suite pass count. A documentation-integrity check is not a passing Phase A test suite.

### 3. Deliberately resisted additions

- Did not extrapolate seven days into a generic duration rule, equate coverage with relative-window semantics, or silently remove any candidate.
- Did not draft generator or boundary code, create questions, choose paraphrases, add fallback semantics, or make new configuration files.
- Did not modify frozen files, load `.env`, access credentials, run an experiment Agent, call any model API, measure accuracy, or execute `git add`, `git commit`, or `git push`.

## Verification scope

The final delivery records this new file's SHA-256, the before/after integrity comparison, and final Git status separately to avoid embedding a self-referential digest. Documentation verification checks that every quoted source block is byte-for-byte present in the unchanged glossary and that all four requested candidates and the stop decision are represented. This does not validate a generator, boundary implementation, or question set.
