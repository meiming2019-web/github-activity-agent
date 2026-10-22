# Project Rules (MANDATORY for all tasks)

## Project
GitHub Activity Query Agent: natural language → constrained tools → local
DuckDB → answer. A 5-day portfolio prototype, NOT production software.

## Language
ALL project artifacts MUST be in English: code, comments, identifiers,
commit messages, README, docs, and completion reports.

## Tech Stack
Python 3.12, DuckDB, official MCP Python SDK, Pydantic, pytest.
ASK before adding ANY new third-party dependency.

## Hard Rules
1. Do ONLY what the current task asks. No drive-by features, no extra
   abstraction layers, no extra config files.
2. Every function ships with pytest tests; all tests must pass before
   delivery.
3. Data safety: DuckDB always opened read_only; every SQL passes a sqlglot
   allowlist check before execution (SELECT-only, table allowlist, no file
   functions such as read_csv); memory_limit and query timeout are always set.
4. Evaluation assets (reference answers, glossary, question bank) must NEVER
   live inside the database file accessible to the Agent.
5. If you find yourself patching your own fresh bugs more than twice, STOP
   and report instead of stacking more patches.

## Anti-Scope-Creep Rules (HIGHEST PRIORITY)
6. Delivered file/function count must not exceed what the task specifies.
   Every extra file requires justification ("why it cannot work without it")
   in the completion report.
7. On ANY requirement ambiguity, do NOT guess — stop and present options
   for me to choose.
8. No speculative generality: do not handle edge cases the task didn't ask
   for; no parameters or config entries "for future use".

## Completion Report Format (MANDATORY after every task)
① Files delivered and each one's responsibility
② Requirements NOT done, with reasons
③ Temptations you deliberately resisted (things you wanted to add but didn't)

## Layout
scripts/ (one-off scripts), agent/ (Agent & MCP server), eval/ (question
bank & grader), tests/