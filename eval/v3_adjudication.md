# v3 Reference Adjudication

The user describes the v3 authoring procedure as a double-blind protocol: Gemini authored the questions and reference SQL in `eval/v3_questions.jsonl`, while Codex independently authored `eval/v3_reference_codex.jsonl` from the answer-stripped blind questions, retained as `eval/v3_questions_blind.jsonl`, together with `eval/glossary.md` and the frozen database schema. Under the user-provided protocol, neither author saw the other's reference answers before finalizing its own version. Codex had no access to other reference answers during its blind authoring phase. Here, "double-blind" describes independent, blinded authoring; the external Gemini authoring history is user-provided provenance, not independently established by the local execution comparison.

The comparison phase subsequently unblinded the references. It compared `eval/v3_reference_gemini.jsonl` with `eval/v3_reference_codex.jsonl` on the frozen `data/github.duckdb`, using a read-only connection. Each original SQL statement was executed exactly once: 52 executions across 26 questions, without SQL changes or retries. Column aliases were ignored, and values were compared by column position. If either statement had a top-level `ORDER BY`, ordered row sequences were compared; otherwise, multisets preserving duplicates were compared. Native fetched values were compared exactly, without normalization, rounding, or tolerance.

The recorded execution-level result is **26/26 MATCH, 0 DIFF, 0 ERROR**. The evidence is `eval/v3_reference_compare.jsonl`, whose SHA-256 is:

`af20d7f867053f8bba489da27daa85d532988a6886b27925b399279e347c291d`

No discrepancy required human adjudication. The user designates the `reference_sql` values in `eval/v3_questions.jsonl` as the canonical answers. Retain `eval/v3_reference_codex.jsonl` and `eval/v3_questions_blind.jsonl` as evidence of the independent blind authoring, alongside the Gemini reference snapshot and comparison record.

Equality was demonstrated only on the frozen database. This is not a universal SQL equivalence proof and does not establish that the references will agree on other datasets.

This note documents the decision and artifact hashes. It does not record a completed Git commit or freeze commit; no staging, commit, or push was performed for this documentation task.
