# v4 C2.1 Question-Aware Injection Change Control

## Authorization and corrected call chain

The latest human decision explicitly authorizes a separate question-aware v4 entry point in `agent/context.py`, with all old function bodies byte-for-byte unchanged. This resolves the previous missing-question-input blocker without changing the existing static caller.

Current historical path: `eval/run_experiment.py:run_config` calls `c2_date_context(session, glossary)`, which queries actual MIN/MAX events and calls `frozen_date_boundaries(glossary, first_event, last_event)`. No question text reaches that legacy entry point. This remains unchanged.

New offline v4 path: a caller explicitly passes question text to `c2_date_context_for_question(question_text, session, glossary)`. The function invokes the unchanged old entry point, preserves its returned string, and may append one question-specific line. This new path is validated separately; legacy compatibility is not evidence of new parsing correctness.

## Deterministic parsing and selection specification

- Authorized relative forms are exactly the case-sensitive strings `the last 7 days`, `last week`, and `previous week`, delimited by word boundaries. Their frozen meanings are unchanged.
- Explicit ranges must have canonical spelling `October D through October D, 2026`, with unpadded decimal day numbers, ordinary single spaces, and the shown comma. This enumerates every inclusive interval in the actual October 8–21 snapshot; the endpoint is incremented by one UTC day.
- Inspect every recognized mention before selecting. Reject reversed ranges, invalid calendar dates, and endpoints outside the observed snapshot UTC-day envelope. An invalid later mention is not ignored merely because an earlier valid window exists.
- Select the leftmost valid authorized window by character position. Multiple mentions, including repeated or conflicting windows, do not change this deterministic priority.
- Any full English month name, the word `through`, relative-looking `last N days`, `last week`, `previous week`, `past two weeks`, or `since` outside a canonical recognized span triggers `ValueError`. This guard is case-insensitive, so noncanonical casing, malformed dates, unauthorized durations, and incomplete ranges fail instead of becoming controls. These markers are reserved syntax in this constrained question vocabulary.
- Standalone years such as a decorative repository-creation year do not constitute windows. `UTC date` is a grouping convention only.
- No window: return the old static string with exactly the same bytes, including no appended newline.
- Selected window: append exactly one LF and `Question window: [YYYY-MM-DD, YYYY-MM-DD)`, with no final newline. Preserve the full legacy prefix exactly.
- All recognized date mentions obey these rules regardless of whether prose calls them irrelevant. A syntactically valid distractor placed first can trigger the appended boundary. Probe fields record triggering and the actual appended boundary; probe results must never cause candidate filtering or regeneration.

## Independent validation design

The injection side obtains frozen relative boundaries from the actual legacy context and parses explicit date spans from the question. The independent generator module computes dates from adjudicated constants and inclusive-day arithmetic without importing the injection parser. Test and hard-gate expected cases are constructed explicitly, including the full 105-interval snapshot lattice, relative windows, multiple mentions, distractors, invalid inputs, and no-window text. The gate calls real new-entry functions through an in-process adapter backed by actual allowlisted read-only database tools; it does not fabricate tool outputs.

Legacy replay preserves complete original source bytes and checks their SHA-256 before loading them as a separate module. For each of 86 unique historical IDs it constructs old and new real legacy contexts, including shared schema/sample context and the unchanged lookup instructions. On the first difference it restores only context.py to its saved original bytes, writes failure evidence, and stops. No Agent loop or model is invoked.

## Phase A and Phase B boundaries

After legacy replay, new-entry verification and all existing/new tests must pass before question generation. All earlier freeze rules, fixed seed 42, closed vocabulary, limited regeneration reasons, and artifact requirements remain in force.

Phase B alone will create the new v4 scheduler, pass each C2/C3 question to this entry point, and post-process run records with `harness_version="c2.1"`. C2.1 and C3.1 continue to differ only by error feedback. No scheduler, experimental run, model client, API call, accuracy evaluation, or run_experiment.py modification is part of this change.

## Preservation baseline

Original complete bytes: `/tmp/v4_question_entry_context_before.py`.
Original SHA-256: `688b90977e398fc34ee1f2e4e89928977e6e6f2ac51bb747cd6c7524e20cbe63`.
Execution baseline: `/tmp/v4_question_entry_baseline.json`.
The original glossary, audit, and vocabulary adjudication remain unchanged. The previous change-control report is updated under the latest explicit authorization. Before/after hashes and full diff follow after applying the additive implementation.

## Applied change hashes and full diff

Before: `688b90977e398fc34ee1f2e4e89928977e6e6f2ac51bb747cd6c7524e20cbe63`.

After: `72367ec27f81eda96a65dfa7c908f3f143bea922ed1f1d28ec7a1b2bb29a9ee4`.

Original file retained as an exact byte prefix; every old function body has zero modified bytes.

```diff
--- a/agent/context.py
+++ b/agent/context.py
@@ -117,3 +117,51 @@
     if payload.get("truncated") or len(payload.get("rows", [])) != 1 or len(payload["rows"][0]) != 2:
         raise ValueError("Expected one complete frozen snapshot bounds row.")
     return frozen_date_boundaries(glossary, *payload["rows"][0])
+
+
+async def c2_date_context_for_question(question_text, session, glossary):
+    """Append the leftmost valid question window; retain legacy context verbatim.
+
+    Parse all mentions before selection, rejecting malformed/out-of-snapshot dates
+    even when another valid window precedes them. Decorative years do not match.
+    A window-shaped distractor can be selected: record this in v4 probes, never
+    filter questions on that basis. Phase B alone will connect the new scheduler
+    and post-process records with harness_version="c2.1" for C2/C3.
+    """
+    if not isinstance(question_text, str):
+        raise ValueError("Question text must be a string.")
+    base = await c2_date_context(session, glossary)
+    windows = json.loads(base.split("\n", 1)[1])["windows"]
+    snapshot = windows["full snapshot window"]
+    pattern = (
+        r"\b(?:the last 7 days|last week|previous week)\b|"
+        r"\bOctober ([1-9]|[12][0-9]|3[01]) through October "
+        r"([1-9]|[12][0-9]|3[01]), (2026)\b"
+    )
+    mentions = []
+    for match in re.finditer(pattern, question_text):
+        expression = match.group(0)
+        if match.group(1) is not None:
+            start = date(2026, 10, int(match.group(1)))
+            end = date(2026, 10, int(match.group(2))) + timedelta(days=1)
+            if not (snapshot["start_inclusive"] <= start.isoformat() < end.isoformat()
+                    <= snapshot["end_exclusive"]):
+                raise ValueError("Explicit question range is outside the frozen snapshot or reversed.")
+        else:
+            key = "last 7 days" if expression == "the last 7 days" else expression
+            start = date.fromisoformat(windows[key]["start_inclusive"])
+            end = date.fromisoformat(windows[key]["end_exclusive"])
+        mentions.append((match.start(), match.end(), start, end))
+    # Recognizable window syntax must not silently become a no-window control.
+    guards = (
+        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\b|"
+        r"\bthrough\b|\b(?:the )?last \d+ days\b|\blast week\b|"
+        r"\bprevious week\b|\bpast two weeks\b|\bsince\b"
+    )
+    for marker in re.finditer(guards, question_text, flags=re.IGNORECASE):
+        if not any(left <= marker.start() and marker.end() <= right for left, right, _, _ in mentions):
+            raise ValueError("Malformed or unauthorized question window expression.")
+    if not mentions:
+        return base
+    _, _, start, end = mentions[0]
+    return base + f"\nQuestion window: [{start.isoformat()}, {end.isoformat()})"
```

## Executed validation before generation

Legacy replay: 86/86 complete contexts byte-identical; see `v4_c21_replay.md`.

New-entry real offline gate: 345 cases; 331 exact-output matches and 14 required rejections. Coverage: three relative forms, all 105 legal explicit intervals in three wording layers, three no-window cases, and four multiple-mention cases. The first-window distractor case was recorded as a valid selection, not filtered. Detailed JSON evidence: `/tmp/v4_new_entry_gate.json`.

Full pytest suite: 360 passed in 13.32 seconds. This comprises 325 existing tests outside the expanded v4 test file plus 35 current v4 tests. No test failed.

## Final Phase A completion report

### 1. Files delivered and responsibilities

| File | Responsibility |
| --- | --- |
| `agent/context.py` | Purely additive question-aware v4 entry; unchanged legacy byte prefix. |
| `eval/check_c21_replay.py` | Real offline old-entry replay and read-only transport adapter. |
| `eval/v4_c21_replay.md` | Per-question hashes for all 86 complete historical contexts. |
| `eval/v4_bounds.py` | Independent generator-side window and question parsing. |
| `eval/check_bounds_consistency.py` | Separate real new-entry hard gate. |
| `eval/gen_v4_questions.py` | Fixed-seed bounded offline generator and requested audits/review package. |
| `eval/row_normalize.py` | JSON serialization/deserialization normalization; this named required module was absent and was created. |
| `eval/check_v4_dedup.py` | Normalized full-question overlap checks against v2/v3 and within v4. |
| `tests/test_v4_bounds.py` | 35 tests for independent bounds, real new-entry checks, rejection behavior, and legacy replay. |
| `tests/test_v4_generation.py` | 21 tests covering SQL families, hard assertions, bounded failure, dedup, normalization, and two-run reproducibility. |
| `eval/v4_questions.jsonl` | One metadata header plus 300 question records with reference SQL/columns/rows and provenance. |
| `eval/v4_regen_log.jsonl` | Every item-8 rejection in deterministic traversal order. |
| `eval/v4_overlap_audit.md` | Normalized overlap audit and disclosed required glossary-time-span overlap. |
| `eval/v4_sample_review.md` | 22 questions, two different semantic cases per family, with blank manual worksheets. |
| `eval/v4_c21_change.md` | Authorized design, full additive diff, separate validation evidence, and this completion record. |

The two test files are required to test every new implementation function. No new dependency or configuration file was introduced. The original glossary audit and vocabulary adjudication remain unchanged. Temporary baseline/source/evidence files are outside the repository and support preservation and replay rather than adding project artifacts.

### 2. Requirements not executed and reasons

All authorized Phase A implementation and offline artifact checks completed. Human worksheet entries remain blank as requested. Phase B caller integration, scheduling, run-record post-processing, scoring integration, experimental Agents, model APIs, and accuracy measurements were not executed because they are outside this phase or explicitly prohibited. No `run_experiment.py` or `grader.py` change was made.

### 3. Deliberately resisted additions

No historical caller rewrite, no new ranges in the static glossary injection, no relative-phrase changes, no glossary edit, no model runs, no extra error-feedback behavior, no future configuration abstraction, no seed changes, and no filtering based on apparent difficulty or distractor probes. No Git add, commit, or push was performed.

## Final actual test and generation results

Final complete suite: **381 passed in 45.06 seconds**, comprising 325 existing tests outside these v4 test files and 56 current phase tests (35 boundary/replay plus 21 generation). Earlier full suite before generator addition: 360 passed. The generation-specific run passed 21 tests, including two complete seed-42 generations whose question bytes, regeneration logs, overlap audits, and sample reviews were identical. No test failed and no compatibility rollback was needed.

Official CLI executed: `python -B eval/gen_v4_questions.py --seed 42 --out eval/v4_questions.jsonl`. The default seed is 42 and other seeds are rejected.

Actual snapshot event extrema: `2026-10-08T00:02:49` through `2026-10-21T23:58:01`; UTC-day envelope `[2026-10-08, 2026-10-22)`. Each row carries database SHA-256 `2a063cab4176b97cfd00ea8e92932c64346127ba1da4b120452fb48236c25812`. All SQL uses the unchanged allowlist and bounded read-only executor, including its memory and timeout controls.

Counts: 180 targeted window questions; 60 targeted advanced SQL questions; 30 non-targeted advanced SQL questions; 30 controls. Each paraphrase layer has 100 questions. There are 100 semantic cases and 11 families.

| Family | Questions | Targeted |
| --- | ---: | --- |
| catalog_lookup | 15 | False |
| consecutive_day_runs | 15 | False |
| daily_trend | 15 | True |
| day_of_week | 15 | True |
| day_over_day | 15 | True |
| language_composition | 15 | False |
| running_total | 15 | True |
| session_segmentation | 15 | False |
| window_active_contributors | 60 | True |
| window_collaboration_events | 60 | True |
| window_new_stars | 60 | True |

Regeneration events: **217**. Each has a permitted item-8 reason; finite traversal stops after each entity pool is exhausted. Sensitivity shifts the entire half-open interval by -1 and +1 day, and both unordered result multisets must differ. `eval.grader.same_multiset` is reused unchanged; all reference rows pass through `eval.row_normalize.normalize_rows`.

| Reason | Count |
| --- | ---: |
| all_zero_aggregate | 111 |
| empty_reference | 22 |
| insensitive_shift_+1 | 23 |
| insensitive_shift_-1 | 61 |

Deduplication: 300 unique normalized v4 questions; zero overlap with all 86 historical questions. Source normalization uses NFKC, casefolding, and punctuation/whitespace collapse. Required verbatim authorized time spans are separately disclosed in the overlap audit; they are retained under the later human wording decision. No complete glossary example sentence is used as a question.

Adjacent-family evidence: session segmentation and consecutive active-day runs have no family-term matches in either historical question/reference-SQL set, `eval/results/runs_v2.jsonl`, `eval/results/runs_v3.jsonl`, or `eval/v3_classification.jsonl`. This uses stored evidence only and does not regrade runs.

Distractor probes: 100 records, 90 append a question window and 10 controls append none. All 100 have `used_for_filtering=false`. The no-window controls contain no effective time predicate; their decorative years are expressly irrelevant. The separate synthetic multi-mention test records that a window-shaped distractor placed first is selected.

Manual package: `eval/v4_sample_review.md`, 22 questions, two per family, with reference SQL, code-computed boundaries, original glossary text, blank calculations, sensitivity evidence, and reference row counts.

## New-entry gate: adopted expressions

| Adopted expression | Independent / injected bounds | Literal | Colloquial | Distractor |
| --- | --- | --- | --- | --- |
| the last 7 days | [2026-10-15, 2026-10-22) | PASS | PASS | PASS |
| last week | [2026-10-15, 2026-10-22) | PASS | PASS | PASS |
| previous week | [2026-10-08, 2026-10-15) | PASS | PASS | PASS |
| October 8 through October 9, 2026 | [2026-10-08, 2026-10-10) | PASS | PASS | PASS |
| October 8 through October 10, 2026 | [2026-10-08, 2026-10-11) | PASS | PASS | PASS |
| October 8 through October 12, 2026 | [2026-10-08, 2026-10-13) | PASS | PASS | PASS |
| October 8 through October 14, 2026 | [2026-10-08, 2026-10-15) | PASS | PASS | PASS |
| October 8 through October 17, 2026 | [2026-10-08, 2026-10-18) | PASS | PASS | PASS |
| October 8 through October 21, 2026 | [2026-10-08, 2026-10-22) | PASS | PASS | PASS |
| October 15 through October 21, 2026 | [2026-10-15, 2026-10-22) | PASS | PASS | PASS |

## New-entry gate: all 105 legal inclusive ranges

All dates are in October 2026; each row was checked through the actual new entry in literal, colloquial, and decorative-year distractor questions.

| Inclusive source range | Expected/injected half-open bounds | All three layers |
| --- | --- | --- |
| October 8 through October 8, 2026 | [2026-10-08, 2026-10-09) | PASS |
| October 8 through October 9, 2026 | [2026-10-08, 2026-10-10) | PASS |
| October 8 through October 10, 2026 | [2026-10-08, 2026-10-11) | PASS |
| October 8 through October 11, 2026 | [2026-10-08, 2026-10-12) | PASS |
| October 8 through October 12, 2026 | [2026-10-08, 2026-10-13) | PASS |
| October 8 through October 13, 2026 | [2026-10-08, 2026-10-14) | PASS |
| October 8 through October 14, 2026 | [2026-10-08, 2026-10-15) | PASS |
| October 8 through October 15, 2026 | [2026-10-08, 2026-10-16) | PASS |
| October 8 through October 16, 2026 | [2026-10-08, 2026-10-17) | PASS |
| October 8 through October 17, 2026 | [2026-10-08, 2026-10-18) | PASS |
| October 8 through October 18, 2026 | [2026-10-08, 2026-10-19) | PASS |
| October 8 through October 19, 2026 | [2026-10-08, 2026-10-20) | PASS |
| October 8 through October 20, 2026 | [2026-10-08, 2026-10-21) | PASS |
| October 8 through October 21, 2026 | [2026-10-08, 2026-10-22) | PASS |
| October 9 through October 9, 2026 | [2026-10-09, 2026-10-10) | PASS |
| October 9 through October 10, 2026 | [2026-10-09, 2026-10-11) | PASS |
| October 9 through October 11, 2026 | [2026-10-09, 2026-10-12) | PASS |
| October 9 through October 12, 2026 | [2026-10-09, 2026-10-13) | PASS |
| October 9 through October 13, 2026 | [2026-10-09, 2026-10-14) | PASS |
| October 9 through October 14, 2026 | [2026-10-09, 2026-10-15) | PASS |
| October 9 through October 15, 2026 | [2026-10-09, 2026-10-16) | PASS |
| October 9 through October 16, 2026 | [2026-10-09, 2026-10-17) | PASS |
| October 9 through October 17, 2026 | [2026-10-09, 2026-10-18) | PASS |
| October 9 through October 18, 2026 | [2026-10-09, 2026-10-19) | PASS |
| October 9 through October 19, 2026 | [2026-10-09, 2026-10-20) | PASS |
| October 9 through October 20, 2026 | [2026-10-09, 2026-10-21) | PASS |
| October 9 through October 21, 2026 | [2026-10-09, 2026-10-22) | PASS |
| October 10 through October 10, 2026 | [2026-10-10, 2026-10-11) | PASS |
| October 10 through October 11, 2026 | [2026-10-10, 2026-10-12) | PASS |
| October 10 through October 12, 2026 | [2026-10-10, 2026-10-13) | PASS |
| October 10 through October 13, 2026 | [2026-10-10, 2026-10-14) | PASS |
| October 10 through October 14, 2026 | [2026-10-10, 2026-10-15) | PASS |
| October 10 through October 15, 2026 | [2026-10-10, 2026-10-16) | PASS |
| October 10 through October 16, 2026 | [2026-10-10, 2026-10-17) | PASS |
| October 10 through October 17, 2026 | [2026-10-10, 2026-10-18) | PASS |
| October 10 through October 18, 2026 | [2026-10-10, 2026-10-19) | PASS |
| October 10 through October 19, 2026 | [2026-10-10, 2026-10-20) | PASS |
| October 10 through October 20, 2026 | [2026-10-10, 2026-10-21) | PASS |
| October 10 through October 21, 2026 | [2026-10-10, 2026-10-22) | PASS |
| October 11 through October 11, 2026 | [2026-10-11, 2026-10-12) | PASS |
| October 11 through October 12, 2026 | [2026-10-11, 2026-10-13) | PASS |
| October 11 through October 13, 2026 | [2026-10-11, 2026-10-14) | PASS |
| October 11 through October 14, 2026 | [2026-10-11, 2026-10-15) | PASS |
| October 11 through October 15, 2026 | [2026-10-11, 2026-10-16) | PASS |
| October 11 through October 16, 2026 | [2026-10-11, 2026-10-17) | PASS |
| October 11 through October 17, 2026 | [2026-10-11, 2026-10-18) | PASS |
| October 11 through October 18, 2026 | [2026-10-11, 2026-10-19) | PASS |
| October 11 through October 19, 2026 | [2026-10-11, 2026-10-20) | PASS |
| October 11 through October 20, 2026 | [2026-10-11, 2026-10-21) | PASS |
| October 11 through October 21, 2026 | [2026-10-11, 2026-10-22) | PASS |
| October 12 through October 12, 2026 | [2026-10-12, 2026-10-13) | PASS |
| October 12 through October 13, 2026 | [2026-10-12, 2026-10-14) | PASS |
| October 12 through October 14, 2026 | [2026-10-12, 2026-10-15) | PASS |
| October 12 through October 15, 2026 | [2026-10-12, 2026-10-16) | PASS |
| October 12 through October 16, 2026 | [2026-10-12, 2026-10-17) | PASS |
| October 12 through October 17, 2026 | [2026-10-12, 2026-10-18) | PASS |
| October 12 through October 18, 2026 | [2026-10-12, 2026-10-19) | PASS |
| October 12 through October 19, 2026 | [2026-10-12, 2026-10-20) | PASS |
| October 12 through October 20, 2026 | [2026-10-12, 2026-10-21) | PASS |
| October 12 through October 21, 2026 | [2026-10-12, 2026-10-22) | PASS |
| October 13 through October 13, 2026 | [2026-10-13, 2026-10-14) | PASS |
| October 13 through October 14, 2026 | [2026-10-13, 2026-10-15) | PASS |
| October 13 through October 15, 2026 | [2026-10-13, 2026-10-16) | PASS |
| October 13 through October 16, 2026 | [2026-10-13, 2026-10-17) | PASS |
| October 13 through October 17, 2026 | [2026-10-13, 2026-10-18) | PASS |
| October 13 through October 18, 2026 | [2026-10-13, 2026-10-19) | PASS |
| October 13 through October 19, 2026 | [2026-10-13, 2026-10-20) | PASS |
| October 13 through October 20, 2026 | [2026-10-13, 2026-10-21) | PASS |
| October 13 through October 21, 2026 | [2026-10-13, 2026-10-22) | PASS |
| October 14 through October 14, 2026 | [2026-10-14, 2026-10-15) | PASS |
| October 14 through October 15, 2026 | [2026-10-14, 2026-10-16) | PASS |
| October 14 through October 16, 2026 | [2026-10-14, 2026-10-17) | PASS |
| October 14 through October 17, 2026 | [2026-10-14, 2026-10-18) | PASS |
| October 14 through October 18, 2026 | [2026-10-14, 2026-10-19) | PASS |
| October 14 through October 19, 2026 | [2026-10-14, 2026-10-20) | PASS |
| October 14 through October 20, 2026 | [2026-10-14, 2026-10-21) | PASS |
| October 14 through October 21, 2026 | [2026-10-14, 2026-10-22) | PASS |
| October 15 through October 15, 2026 | [2026-10-15, 2026-10-16) | PASS |
| October 15 through October 16, 2026 | [2026-10-15, 2026-10-17) | PASS |
| October 15 through October 17, 2026 | [2026-10-15, 2026-10-18) | PASS |
| October 15 through October 18, 2026 | [2026-10-15, 2026-10-19) | PASS |
| October 15 through October 19, 2026 | [2026-10-15, 2026-10-20) | PASS |
| October 15 through October 20, 2026 | [2026-10-15, 2026-10-21) | PASS |
| October 15 through October 21, 2026 | [2026-10-15, 2026-10-22) | PASS |
| October 16 through October 16, 2026 | [2026-10-16, 2026-10-17) | PASS |
| October 16 through October 17, 2026 | [2026-10-16, 2026-10-18) | PASS |
| October 16 through October 18, 2026 | [2026-10-16, 2026-10-19) | PASS |
| October 16 through October 19, 2026 | [2026-10-16, 2026-10-20) | PASS |
| October 16 through October 20, 2026 | [2026-10-16, 2026-10-21) | PASS |
| October 16 through October 21, 2026 | [2026-10-16, 2026-10-22) | PASS |
| October 17 through October 17, 2026 | [2026-10-17, 2026-10-18) | PASS |
| October 17 through October 18, 2026 | [2026-10-17, 2026-10-19) | PASS |
| October 17 through October 19, 2026 | [2026-10-17, 2026-10-20) | PASS |
| October 17 through October 20, 2026 | [2026-10-17, 2026-10-21) | PASS |
| October 17 through October 21, 2026 | [2026-10-17, 2026-10-22) | PASS |
| October 18 through October 18, 2026 | [2026-10-18, 2026-10-19) | PASS |
| October 18 through October 19, 2026 | [2026-10-18, 2026-10-20) | PASS |
| October 18 through October 20, 2026 | [2026-10-18, 2026-10-21) | PASS |
| October 18 through October 21, 2026 | [2026-10-18, 2026-10-22) | PASS |
| October 19 through October 19, 2026 | [2026-10-19, 2026-10-20) | PASS |
| October 19 through October 20, 2026 | [2026-10-19, 2026-10-21) | PASS |
| October 19 through October 21, 2026 | [2026-10-19, 2026-10-22) | PASS |
| October 20 through October 20, 2026 | [2026-10-20, 2026-10-21) | PASS |
| October 20 through October 21, 2026 | [2026-10-20, 2026-10-22) | PASS |
| October 21 through October 21, 2026 | [2026-10-21, 2026-10-22) | PASS |

## New-entry gate: no-window, multiple-mention, and illegal-input cases

| Synthetic question | Result | Boundaries |
| --- | --- | --- |
| List repository names. | pass | None |
| List repository names. Creation year 2017 is background only. | pass | None |
| Explain the UTC date grouping field. | pass | None |
| Use previous week; ignore last week. | pass | ['2026-10-08', '2026-10-15'] |
| Ignore last week; count events for previous week. | pass | ['2026-10-15', '2026-10-22'] |
| Use October 8 through October 10, 2026; ignore the last 7 days. | pass | ['2026-10-08', '2026-10-11'] |
| Use last week and last week. | pass | ['2026-10-15', '2026-10-22'] |
| Count events for October 7 through October 9, 2026. | rejected_as_required | not applicable |
| Count events for October 8 through October 22, 2026. | rejected_as_required | not applicable |
| Count events for October 10 through October 9, 2026. | rejected_as_required | not applicable |
| Count events for October 8 through October 32, 2026. | rejected_as_required | not applicable |
| Count events for October eight through October 10, 2026. | rejected_as_required | not applicable |
| Count events for October 08 through October 10, 2026. | rejected_as_required | not applicable |
| Count events for October 8 to October 10, 2026. | rejected_as_required | not applicable |
| Count events for October 8 through October 10, 2025. | rejected_as_required | not applicable |
| Count events for Last week. | rejected_as_required | not applicable |
| Count events for last 3 days. | rejected_as_required | not applicable |
| Count events for last 14 days. | rejected_as_required | not applicable |
| Count events for past two weeks. | rejected_as_required | not applicable |
| Count events since October 8, 2026. | rejected_as_required | not applicable |
| Use last week; ignore October 8 through October 22, 2026. | rejected_as_required | not applicable |

## Artifact SHA-256 values

This document's own digest is reported separately to avoid a self-referential hash. The original audit and vocabulary adjudication hashes are included as preservation evidence.

| File | SHA-256 |
| --- | --- |
| `agent/context.py` | `72367ec27f81eda96a65dfa7c908f3f143bea922ed1f1d28ec7a1b2bb29a9ee4` |
| `eval/check_c21_replay.py` | `11818b63d14557ed3737abe02c2c75b3d392f89d8b146202e99f75ebfbde0c55` |
| `eval/v4_c21_replay.md` | `9b9fc8b03415432e40ee2fd4169977b3c5ef24ab96f1f40b3cdde29306efc6a6` |
| `eval/v4_bounds.py` | `271237f1b793dd907536a242b63454f3cf01795bf63febd33cf36fe8ddb724ec` |
| `eval/check_bounds_consistency.py` | `9752dd1acfbad70d2643de180104ff198d73bc3564d9dc34f8b027bb681b5072` |
| `eval/gen_v4_questions.py` | `edbfff85fbc19f4b201de33bd3d419ab554aff9643462f825efa6c6fdefee9e4` |
| `eval/row_normalize.py` | `701bfe5d62d01533dd9bf558e5e613689227ba8e75692ed4c2c7befc0ad93d01` |
| `eval/check_v4_dedup.py` | `48f1900f0b5c40105a4bbd5c557b7d5255a3dd4c44120b6412a6ef3d5237a59b` |
| `tests/test_v4_bounds.py` | `03f51fa70e5313bc96ece9f69f13502a82f6ad014ebe0a9522621c390f8ad358` |
| `tests/test_v4_generation.py` | `911e3b739c470292cdedd3622670be828db60b9a08e199bc972194d3c4d36844` |
| `eval/v4_questions.jsonl` | `1e33b109a3af2ffcd74926e49876332cd6173bc6a5476000b623fe9689877067` |
| `eval/v4_regen_log.jsonl` | `f379c08c5fc6ef5c184394574dac3ffa2aac0793ad27aff3fcbfc123b64be559` |
| `eval/v4_overlap_audit.md` | `006851267dc4bb09eb2374597875b7958bf9429ae37f66d23e2df1d8dcb257bc` |
| `eval/v4_sample_review.md` | `8668908ccfc54b2ee89673a37574e9c6a2f6f00fb409c50661c8dbdffc8c6278` |
| `eval/v4_glossary_audit.md` | `1ad7371975afe60380fc38c112d2a34b9b672ec05c7c1a03099a5cc7e907d68a` |
| `eval/v4_glossary_adjudication.md` | `b7eb2aebfa33a5a40ba10b7e97814e49ca4e9ad48631a78775fe3ac2ec2a2248` |
