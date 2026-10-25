# v4 Glossary Adjudication

## Authority and effect

This document records the user's explicit human adjudication for v4 Phase A. It resolves the four vocabulary gaps recorded in `eval/v4_glossary_audit.md` by prohibiting those expressions and establishing the closed vocabulary below. It does not change the frozen glossary or the original audit. The later adjudication supersedes the original requirement that colloquial variants avoid glossary wording: only non-time wording may now be paraphrased.

The Step 0 vocabulary blocker is resolved. This decision does not establish that the independent boundary-consistency gate passes or authorize any experimental Agent run.

## Prohibited expressions

The following expressions must not appear as effective windows or as distractors in v4 question text:

- `last 3 days`
- `last 14 days`
- `past two weeks`
- `since <date>`

Equivalent windows may be expressed using the authorized explicit inclusive date-range form. No implicit aliases, provisional semantics, or reasonable-inference exceptions are authorized.

## Closed authorized vocabulary

All endpoints below are UTC midnight. Intervals are inclusive at the start and exclusive at the end.

| Authorized form | Meaning |
| --- | --- |
| `the last 7 days` | `[2026-10-15, 2026-10-22)` |
| `last week` | `[2026-10-15, 2026-10-22)` |
| `previous week` | `[2026-10-08, 2026-10-15)` |
| Explicit inclusive date range in the form `October 8 through October 21, 2026` | Include the supplied start and end dates; the exclusive upper bound is the supplied end date plus one day. Starts and lengths may vary freely within the snapshot interval `[2026-10-08, 2026-10-22)`, including 2, 3, 5, 7, 10, and 14 days or other lengths within that coverage. |
| `UTC date` | Daily-grouping convention only: `CAST(created_at AS DATE)`; this is not a window. |

The coverage above is part of the adjudication. Phase A still requires read-only queries of the frozen database's actual minimum and maximum event dates; it must not replace those queries with reference-date arithmetic.

## Paraphrase layers

- `literal`: use the authorized time-expression form verbatim.
- `colloquial`: paraphrase only non-time portions such as the metric, scope, or predicate. Keep the authorized time expression verbatim.
- `distractor`: the effective window must use an authorized expression. Irrelevant time mentions may be added only if their interpretation requires no undefined semantics; a decorative repository-creation year is permitted. Prohibited expressions remain prohibited even as distractors.

## Boundary-consistency hard gate

`eval/check_bounds_consistency.py` must assert that independently implemented generator boundaries equal the existing injection-side boundaries for every authorized expression form actually adopted by the generator.

If the injection side fails to recognize an adopted expression, or either side produces different boundaries, stop and report. Do not modify injection code or frozen files, silently remove a failing adopted form, add injection support, or infer missing semantics to make the check pass. The check must use the actual frozen code and data; success is not presumed.

## Remaining Phase A obligations

Continue the original Phase A scope subject to its hard gates: snapshot facts, independent boundaries, 300 questions (180 targeted window, 60 targeted advanced SQL, 30 non-targeted advanced SQL, and 30 time-free controls), three paraphrase layers per family, reference SQL and normalized rows, hard assertions, deduplication and overlap audit, manual review package, reproducibility and other required tests, file hashes, and final Git status.

- Preserve fixed seed `42`; do not select or change the seed after observing outputs.
- Regenerate only for failures of the original item 8 hard assertions (nonempty/nonzero reference results, window sensitivity to one-day boundary shifts, and deterministic Top-N ordering with an explicit tie rule). Record the reason and use a deterministic process.
- Do not select questions by apparent difficulty or presentation quality.
- Bound failure handling so an unsatisfiable candidate cannot cause infinite regeneration. A stop is not a successful generation run.
- Do not run project experimental Agents, call model APIs (including DeepSeek), or measure accuracy.
- Do not read credentials, load `.env`, add dependencies without authorization, or execute `git add`, `git commit`, or `git push`.
- Preserve all existing files, including `eval/glossary.md`, `eval/v4_glossary_audit.md`, frozen code, historical question sets and results, preregistrations, feasibility documents, and traces.
- If a later hard requirement cannot be met or conflicts with another requirement, report the concrete evidence and stop the affected work; do not expand permissions or change frozen content.

## Baseline and reporting

The execution baseline was recorded before creating this file at `/tmp/github_activity_v4_adjudicated_baseline.json`. The pre-existing untracked file `eval/v4_glossary_audit.md` belongs to the earlier Step 0 delivery and is protected in this round; it is not a new file from this continuation.

Preserved source identifiers:

- `eval/glossary.md`: `1a2ce44850529108249fe9970803b1745787ecf37c63136a062a11bb808c3d05`.
- `eval/v4_glossary_audit.md`: `1ad7371975afe60380fc38c112d2a34b9b672ec05c7c1a03099a5cc7e907d68a`.

The completion report must distinguish new files from the existing audit and include this adjudication file's SHA-256, adopted expressions and their individual boundary-check results, layer/family counts, regeneration statistics, review-package path, tests actually run and pass counts, all new-file SHA-256 values, protected-file integrity evidence, and complete Git status. Any hard-gate failure must explicitly identify subsequent work that was not executed.
