# v4 Round 1 — Foreign-Key Audit and Read-Only Preflight

## Result and scope

**Foreign-key check passed: 0 distinct event repo_id values absent from repos.** This completes only the independent FK/preflight portion of Round 1. The overall Round 1 repair remains pending missing human-review text and identification of the two requested SQL-style families.

No generator, question set, regeneration log, sample review, context code, historical source, or existing report was modified. The existing 22-question sample is an unsigned review package, not a supplied human review. The placeholder in the request was not saved as a human record.

## Actual query and result

```sql
SELECT COUNT(DISTINCT e.repo_id) AS missing_repo_id_count FROM events e LEFT JOIN repos r ON e.repo_id = r.repo_id WHERE r.repo_id IS NULL
```

Validated execution SQL (the existing executor adds its bounded fetch limit):

```sql
SELECT COUNT(DISTINCT e.repo_id) AS missing_repo_id_count FROM events AS e LEFT JOIN repos AS r ON e.repo_id = r.repo_id WHERE r.repo_id IS NULL LIMIT 201
```

```json
{
  "columns": [
    "missing_repo_id_count"
  ],
  "rows": [
    [
      0
    ]
  ],
  "truncated": false,
  "elapsed_ms": 63.616542145609856
}
```

The query was validated with the existing sqlglot SELECT/table/function allowlist, then executed through `agent.mcp_server.execute_select`. The unchanged connection factory opens DuckDB with `read_only=True`, `memory_limit=2GB`, external access and extension auto-install/load disabled; the executor applies a ten-second interruptible timeout. No MCP session, experimental Agent, model client, or API was started.

The requested measure is `COUNT(DISTINCT e.repo_id)` under an unmatched LEFT JOIN. This report makes that specific integrity claim; it does not substitute the FK result for the still-pending JOIN/no-JOIN row comparison.

## Snapshot and baseline evidence

- Database SHA-256 before query: `2a063cab4176b97cfd00ea8e92932c64346127ba1da4b120452fb48236c25812`.
- Database SHA-256 after query: `2a063cab4176b97cfd00ea8e92932c64346127ba1da4b120452fb48236c25812`.
- The database bytes were unchanged.
- Execution baseline: `/tmp/v4_round1_preflight_baseline.json`, containing 17,069 existing regular-file hashes and 3 symlink targets.
- Git internal metadata and the previously documented environment/certificate exclusions were not content-hashed. No credentials or `.env` file was read or loaded.
- Query output evidence: `/tmp/v4_round1_fk_result.json`.
- Existing changes shown in the initial Git status predate this Round 1 preflight and were preserved.

### Existing question set and sample package

| Artifact | SHA-256 |
| --- | --- |
| `eval/v4_questions.jsonl` | `1e33b109a3af2ffcd74926e49876332cd6173bc6a5476000b623fe9689877067` |
| `eval/v4_sample_review.md` | `8668908ccfc54b2ee89673a37574e9c6a2f6f00fb409c50661c8dbdffc8c6278` |
| `eval/v4_regen_log.jsonl` | `f379c08c5fc6ef5c184394574dac3ffa2aac0793ad27aff3fcbfc123b64be559` |
| `agent/context.py` | `72367ec27f81eda96a65dfa7c908f3f143bea922ed1f1d28ec7a1b2bb29a9ee4` |

Question set: 300 question records plus one metadata record. Existing sample: 22 distinct question IDs, all present in the question set. Neither artifact was regenerated or overwritten.

Old sample IDs:

```text
v4_001
v4_006
v4_061
v4_066
v4_121
v4_126
v4_181
v4_186
v4_196
v4_201
v4_211
v4_216
v4_226
v4_231
v4_241
v4_246
v4_256
v4_261
v4_271
v4_276
v4_286
v4_291
```

Old sample window-expression coverage: `the last 7 days` and `previous week`. The remaining actual expressions are `last week` and seven explicit date-range strings. No additional sample was selected in this preflight.

## Pending JOIN/no-JOIN comparison

The actual human review was not supplied; the request ends with a placeholder. The phrase "two SQL-style families" does not uniquely identify two `template_family_id` values in the available artifacts. The observed implementation has:

- Three window families using events-to-repos joins: `window_new_stars`, `window_collaboration_events`, and `window_active_contributors`.
- Four targeted daily-series families with calendar/count joins rather than events-to-repos joins.
- Two adjacent families using event-only SQL, and two catalog-only control families.

No pair was guessed. No JOIN/no-JOIN comparison SQL was constructed or executed and no reference SQL was changed. Required input: the verbatim Round 1 human review and, if it does not identify them, the two intended family IDs or representative question IDs.

## Read-only implementation observations

- `eval/gen_v4_questions.py:207` currently tests only simultaneous interval shifts of -1 and +1 day. Its snapshot start/end values come from actual MIN/MAX event dates at lines 170–171. No expanded battery has been implemented or executed.
- The existing sample selection at lines 276–277 chooses two records per family; it does not yet stratify by window expression. The current sample remains intact.
- The daily-series SQL at line 87 builds a calendar with `generate_series`, and later fills missing event counts with zero. Consequently, for date-bearing daily outputs, extending a calendar beyond available events can add a zero-count output date: the statement "an out-of-coverage extra day is always row-set neutral" is not universal across existing families. This is a static code observation, not a new perturbation policy or an executed sensitivity result. The requested exclusion of out-of-coverage perturbations has not been changed or implemented.
- All further repairs await the missing review text; no new semantics or family-selection rules were adopted.

## Completion scope

1. Sole new repository file: `eval/v4_fk_audit.md`, recording the real FK query/result, frozen snapshot evidence, existing sample IDs/hashes, and pending inputs.
2. Not executed: human-review transcription, extended sensitivity battery, JOIN/no-JOIN comparison, regeneration, changed-question analysis, r2 sample creation, replay reruns, new-entry reruns, or full-suite reruns. Round 1 is not complete; no new test pass count is claimed.
3. Deliberately resisted: inventing review text, treating the 22-question package as signed off, choosing an unspecified family pair, overwriting existing artifacts, changing context.py, or doing any Git write/model/Agent operation.

## Initial Git status

```text
 M agent/context.py
 M eval/check_bounds_consistency.py
 M eval/v4_bounds.py
 M tests/test_v4_bounds.py
?? eval/check_c21_replay.py
?? eval/check_v4_dedup.py
?? eval/gen_v4_questions.py
?? eval/row_normalize.py
?? eval/v4_c21_change.md
?? eval/v4_c21_replay.md
?? eval/v4_overlap_audit.md
?? eval/v4_questions.jsonl
?? eval/v4_regen_log.jsonl
?? eval/v4_sample_review.md
?? tests/test_v4_generation.py
```

The final report supplies this new document's SHA-256, the post-write preservation check, and final Git status without embedding a self-referential digest.

## Clarified representative SQL-style comparison — completed

The later user instruction identifies v4_001, v4_061, and v4_246, resolving the earlier family-selection ambiguity. These checks use the preserved pre-regeneration question set; they do not rewrite any reference SQL. The actual human review comments are still missing.

Pre-regeneration question set SHA-256: `1e33b109a3af2ffcd74926e49876332cd6173bc6a5476000b623fe9689877067`.
Frozen database SHA-256: `2a063cab4176b97cfd00ea8e92932c64346127ba1da4b120452fb48236c25812`.

Rows were independently executed through the existing read-only allowlisted executor, normalized with the existing row normalizer, serialized as UTF-8 JSON with compact separators and no NaN, and compared byte-for-byte. Column lists were also compared. No unordered or tolerant comparison substitutes for this byte-equality check.

### v4_001 — window_new_stars

Original SQL:
```sql
SELECT COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'firecrawl/firecrawl'
```

Requested style-only variant:
```sql
SELECT COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'firecrawl/firecrawl'
```

Actual results and equality evidence:
```json
{
  "question_id": "v4_001",
  "family": "window_new_stars",
  "reference_columns": [
    "value"
  ],
  "variant_columns": [
    "value"
  ],
  "reference_rows": [
    [
      39
    ]
  ],
  "variant_rows": [
    [
      39
    ]
  ],
  "reference_rows_sha256": "cdef24ea444e71ce3ad57856ea77de43a6e24de57a4651784a0ee04692011ee9",
  "variant_rows_sha256": "cdef24ea444e71ce3ad57856ea77de43a6e24de57a4651784a0ee04692011ee9",
  "rows_byte_identical": true,
  "columns_identical": true
}
```

### v4_061 — window_collaboration_events

Original SQL:
```sql
SELECT COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'morluto/rea'
```

Requested style-only variant:
```sql
SELECT COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'morluto/rea'
```

Actual results and equality evidence:
```json
{
  "question_id": "v4_061",
  "family": "window_collaboration_events",
  "reference_columns": [
    "value"
  ],
  "variant_columns": [
    "value"
  ],
  "reference_rows": [
    [
      170
    ]
  ],
  "variant_rows": [
    [
      170
    ]
  ],
  "reference_rows_sha256": "0edb869ab22bed2613627f7366cda39d094c042d290f74df3a7d2620486b299f",
  "variant_rows_sha256": "0edb869ab22bed2613627f7366cda39d094c042d290f74df3a7d2620486b299f",
  "rows_byte_identical": true,
  "columns_identical": true
}
```

### v4_246 — session_segmentation

Original SQL:
```sql
WITH ordered AS (SELECT e.created_at, LAG(e.created_at) OVER (ORDER BY e.created_at, e.event_id) AS previous_at FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-15' AND e.repo_name = 'rustdesk/rustdesk' AND e.type = 'PushEvent') SELECT SUM(CASE WHEN previous_at IS NULL OR created_at - previous_at > INTERVAL '30 minutes' THEN 1 ELSE 0 END) AS session_count FROM ordered
```

Requested style-only variant:
```sql
WITH ordered AS (SELECT e.created_at, LAG(e.created_at) OVER (ORDER BY e.created_at, e.event_id) AS previous_at FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-15' AND e.repo_name = 'rustdesk/rustdesk' AND e.type = 'PushEvent') SELECT SUM(CASE WHEN previous_at IS NULL OR created_at - previous_at > INTERVAL '30 minutes' THEN 1 ELSE 0 END) AS session_count FROM ordered
```

Actual results and equality evidence:
```json
{
  "question_id": "v4_246",
  "family": "session_segmentation",
  "reference_columns": [
    "session_count"
  ],
  "variant_columns": [
    "session_count"
  ],
  "reference_rows": [
    [
      6
    ]
  ],
  "variant_rows": [
    [
      6
    ]
  ],
  "reference_rows_sha256": "a9aa85acf18adf4f2e42f1cb876a854cf82b70587922457d888db0e2df100099",
  "variant_rows_sha256": "a9aa85acf18adf4f2e42f1cb876a854cf82b70587922457d888db0e2df100099",
  "rows_byte_identical": true,
  "columns_identical": true
}
```

Result: **3/3 byte-identical row sets and identical column lists**. Together with the zero-orphan FK check, these specific representatives have direct evidence that the requested JOIN insertion/removal did not change their answers. This result is limited to the inspected frozen snapshot and statements.

## Round 1 expanded-battery hard stop

**The repair is blocked by a finite-pool feasibility failure; it is not a completed regeneration.** No rule, seed, adopted expression, or metric was changed after this failure. No additional generation or downstream validation was launched.

Command: `python -B -m pytest -q -p no:cacheprovider tests/test_v4_generation.py`. Actual result: **26 passed, 1 failed in 16.80 seconds**, exit code 1. The failed test is the full-generation reproducibility test; its first generation could not complete, so the second generation was never started.

Exact stop: `RuntimeError: No candidate satisfies item 8 after 100 deterministic attempts: window_active_contributors_03_repo`.

This semantic case uses `October 8 through October 9, 2026`, or `[2026-10-08, 2026-10-10)`, for per-repository active contributors. The failure log contains all 100 repository identities exactly once, with attempt numbers 1–100. This establishes exhaustion for this fixed case and candidate pool; it does not establish impossibility for every other window or a broader candidate design.

| Eligible perturbation | Half-open bounds |
| --- | --- |
| start + 1 | [2026-10-09, 2026-10-10) |
| end - 1 | [2026-10-08, 2026-10-09) |
| end + 1 | [2026-10-08, 2026-10-11) |
| both + 1 | [2026-10-09, 2026-10-11) |

The start-minus-one and both-minus-one variants are excluded because their starts lie before the snapshot. No excluded SQL was executed for the battery.

| First rejecting assertion for this fixed case | Repositories |
| --- | ---: |
| all_zero_aggregate | 73 |
| insensitive_both_plus_one | 3 |
| insensitive_end_minus_one | 9 |
| insensitive_end_plus_one | 8 |
| insensitive_start_plus_one | 7 |

The partial attempt logged 269 rejection events in total before stopping. Earlier accepted cases produced 138 in-memory question records (46 completed semantic cases from the fixed iteration order), but no question file was published. These are not a completed dataset or a selected partial replacement.

| Partial-attempt reason | Events |
| --- | ---: |
| all_zero_aggregate | 144 |
| empty_reference | 9 |
| insensitive_both_plus_one | 5 |
| insensitive_end_minus_one | 26 |
| insensitive_end_plus_one | 14 |
| insensitive_start_minus_one | 1 |
| insensitive_start_plus_one | 70 |

Preserved failure log: `/tmp/v4_round1_repair_before/failed_expanded_battery_regen_log.jsonl`.
Failure log SHA-256: `a7266d7a405d8c820a8e77fb0b2e79f191357f190e318699bdab4cf1f2e7ee1b`.

### Complete failed-case candidate inventory

| Attempt | Repository | First failing assertion |
| ---: | --- | --- |
| 1 | deepseek-ai/deepseek-harness | all_zero_aggregate |
| 2 | clash-verge-rev/clash-verge-rev | all_zero_aggregate |
| 3 | torvalds/linux | all_zero_aggregate |
| 4 | yangshun/tech-interview-handbook | all_zero_aggregate |
| 5 | Chalarangelo/30-seconds-of-code | all_zero_aggregate |
| 6 | labuladong/fucking-algorithm | all_zero_aggregate |
| 7 | openai/codex | all_zero_aggregate |
| 8 | Graphify-Labs/graphify | all_zero_aggregate |
| 9 | nilbuild/developer-roadmap | all_zero_aggregate |
| 10 | sindresorhus/awesome | all_zero_aggregate |
| 11 | NousResearch/hermes-agent | insensitive_both_plus_one |
| 12 | TheAlgorithms/Python | all_zero_aggregate |
| 13 | codecrafters-io/build-your-own-x | all_zero_aggregate |
| 14 | electron/electron | all_zero_aggregate |
| 15 | firecrawl/firecrawl | insensitive_end_plus_one |
| 16 | vinta/awesome-python | all_zero_aggregate |
| 17 | AUTOMATIC1111/stable-diffusion-webui | all_zero_aggregate |
| 18 | Shubhamsaboo/awesome-llm-apps | all_zero_aggregate |
| 19 | react/react-native | insensitive_end_minus_one |
| 20 | github/spec-kit | insensitive_end_minus_one |
| 21 | github/gitignore | all_zero_aggregate |
| 22 | twbs/bootstrap | all_zero_aggregate |
| 23 | EbookFoundation/free-programming-books | all_zero_aggregate |
| 24 | msitarzewski/agency-agents | all_zero_aggregate |
| 25 | justjavac/free-programming-books-zh_CN | all_zero_aggregate |
| 26 | 521xueweihan/HelloGitHub | all_zero_aggregate |
| 27 | nodejs/node | insensitive_end_plus_one |
| 28 | Significant-Gravitas/AutoGPT | insensitive_start_plus_one |
| 29 | practical-tutorials/project-based-learning | all_zero_aggregate |
| 30 | ollama/ollama | all_zero_aggregate |
| 31 | Genymobile/scrcpy | all_zero_aggregate |
| 32 | langchain-ai/langchain | insensitive_end_minus_one |
| 33 | langflow-ai/langflow | insensitive_end_plus_one |
| 34 | ohmyzsh/ohmyzsh | all_zero_aggregate |
| 35 | harry0703/MoneyPrinterTurbo | all_zero_aggregate |
| 36 | jackfrued/Python-100-Days | all_zero_aggregate |
| 37 | ultraworkers/claw-code | all_zero_aggregate |
| 38 | openclaw/openclaw | insensitive_end_minus_one |
| 39 | freeCodeCamp/freeCodeCamp | insensitive_end_minus_one |
| 40 | donnemartin/system-design-primer | all_zero_aggregate |
| 41 | anomalyco/opencode | insensitive_both_plus_one |
| 42 | excalidraw/excalidraw | all_zero_aggregate |
| 43 | x1xhlol/system-prompts-and-models-of-ai-tools | all_zero_aggregate |
| 44 | react/react | all_zero_aggregate |
| 45 | jlevy/the-art-of-command-line | all_zero_aggregate |
| 46 | rust-lang/rust | insensitive_start_plus_one |
| 47 | browser-use/browser-use | all_zero_aggregate |
| 48 | tensorflow/tensorflow | all_zero_aggregate |
| 49 | f/prompts.chat | all_zero_aggregate |
| 50 | DigitalPlatDev/FreeDomain | all_zero_aggregate |
| 51 | iptv-org/iptv | insensitive_start_plus_one |
| 52 | mattpocock/skills | all_zero_aggregate |
| 53 | microsoft/vscode | insensitive_end_minus_one |
| 54 | open-webui/open-webui | insensitive_start_plus_one |
| 55 | golang/go | insensitive_start_plus_one |
| 56 | yt-dlp/yt-dlp | all_zero_aggregate |
| 57 | krahets/hello-algo | all_zero_aggregate |
| 58 | shadcn-ui/ui | insensitive_end_minus_one |
| 59 | Hack-with-Github/Awesome-Hacking | all_zero_aggregate |
| 60 | flutter/flutter | all_zero_aggregate |
| 61 | anthropics/skills | all_zero_aggregate |
| 62 | getify/You-Dont-Know-JS | all_zero_aggregate |
| 63 | ggml-org/llama.cpp | insensitive_both_plus_one |
| 64 | VoltAgent/awesome-design-md | all_zero_aggregate |
| 65 | multica-ai/andrej-karpathy-skills | all_zero_aggregate |
| 66 | microsoft/generative-ai-for-beginners | all_zero_aggregate |
| 67 | microsoft/PowerToys | all_zero_aggregate |
| 68 | DietrichGebert/ponytail | all_zero_aggregate |
| 69 | farion1231/cc-switch | insensitive_end_plus_one |
| 70 | ytdl-org/youtube-dl | all_zero_aggregate |
| 71 | huggingface/transformers | insensitive_end_plus_one |
| 72 | 996icu/996.ICU | all_zero_aggregate |
| 73 | jwasham/coding-interview-university | all_zero_aggregate |
| 74 | Snailclimb/JavaGuide | all_zero_aggregate |
| 75 | garrytan/gstack | insensitive_end_minus_one |
| 76 | massgravel/Microsoft-Activation-Scripts | all_zero_aggregate |
| 77 | nextlevelbuilder/ui-ux-pro-max-skill | all_zero_aggregate |
| 78 | anthropics/claude-code | insensitive_end_minus_one |
| 79 | microsoft/markitdown | all_zero_aggregate |
| 80 | avelino/awesome-go | all_zero_aggregate |
| 81 | Comfy-Org/ComfyUI | all_zero_aggregate |
| 82 | CyC2018/CS-Notes | all_zero_aggregate |
| 83 | n8n-io/n8n | insensitive_end_plus_one |
| 84 | ripienaar/free-for-dev | all_zero_aggregate |
| 85 | affaan-m/ECC | all_zero_aggregate |
| 86 | public-apis/public-apis | all_zero_aggregate |
| 87 | godotengine/godot | insensitive_start_plus_one |
| 88 | trimstray/the-book-of-secret-knowledge | all_zero_aggregate |
| 89 | airbnb/javascript | all_zero_aggregate |
| 90 | 2dust/v2rayN | all_zero_aggregate |
| 91 | vuejs/vue | all_zero_aggregate |
| 92 | langgenius/dify | insensitive_start_plus_one |
| 93 | vercel/next.js | insensitive_end_plus_one |
| 94 | kubernetes/kubernetes | all_zero_aggregate |
| 95 | trekhleb/javascript-algorithms | all_zero_aggregate |
| 96 | awesome-selfhosted/awesome-selfhosted | all_zero_aggregate |
| 97 | obra/superpowers | all_zero_aggregate |
| 98 | rustdesk/rustdesk | all_zero_aggregate |
| 99 | ossu/computer-science | all_zero_aggregate |
| 100 | morluto/rea | insensitive_end_plus_one |

### Final out-of-coverage rationale implemented in the generator

> Extending one day beyond coverage is answer-neutral for non-calendar aggregates because the extra day has no data. For questions using generate_series date scaffolds, the extra day may add a zero-count row and change the row set; the neutrality conclusion does not apply. Out-of-coverage perturbations are nevertheless excluded uniformly. These endpoint mistakes will be detected by SQL window-endpoint parsing during analysis, not by row-set grading.

This is the requested constrained rationale and uniform exclusion rule, not a claim that a universal neutrality property was experimentally established.

### Delivered changes, preservation, and pending work

- Modified `eval/gen_v4_questions.py`: six-case battery, explicit exclusion records, preserved original review, and explicit window-expression/family stratification with separate substantive versus evidence-only change classification.
- Modified `tests/test_v4_generation.py`: expanded battery and r2 classification tests. Individual checks passed, but the full-generation test failed on the actual finite candidate pool; this implementation is not delivered as a passing complete generator.
- Updated this FK report with the three successful style comparisons and the concrete hard-stop evidence. No other project file was intentionally changed in this repair.
- Original question set, official regeneration log, and original 22-question package remain untouched and backed up at `/tmp/v4_round1_repair_before`. No new question-set hash or changed-question list from a complete regeneration exists; published dataset changes are zero.
- No production `eval/v4_sample_review_r2.md` was created. The replacement impact on the original 22 IDs cannot be concluded without a successful complete regeneration. Unit-test-only review outputs are not human review packages.
- The actual new-entry gate ran as the first generation precondition and returned before candidate generation. The old-entry 86-question replay and complete pytest suite were not rerun after the generation hard stop; earlier success counts are not reused as Round 1 pass counts.
- Human Round 1 comments are still missing. `eval/v4_sample_review_round1.md` was not created, and no placeholder or signed-off review was invented.
- No context.py, glossary, original audit/adjudication, historical code/data/results, seed, or reference-SQL template was altered. No model, Agent, accuracy assessment, or Git write operation was performed.

## Integrity-check qualification

The final broad baseline comparison also detected a byte change in the ignored macOS directory metadata file `.DS_Store`. No task command wrote or restored this file; the origin of the change is not established. It is not treated as an authorized project-code change and has not been overwritten.

Before SHA-256: `9a834d7677ee506839e3a5d5e0edefdcb68e5c1f98f594d11672c47c4b58f744`.

Observed current SHA-256: `5af1d87c9f1cb8fcd6ea2c8b94c3898b75a7add8791278bae71f8aebec9720ab`.

The final delivery distinguishes this observed metadata change from the three authorized repair-file changes and separately verifies all protected code, question, log, and review artifacts.

A subsequent inventory also observed a new ignored `eval/.DS_Store` file (SHA-256 `8e225ffd3275f366724b03baa6d0d54eb103e020fc46678a0d5fa14e44946c8e`). No task command created or restored this metadata file; its origin is not established. It is excluded from the task deliverables but disclosed as an observed filesystem difference.

## Deterministic window fallback correction — rules recorded before the next trial

The original item-8 authorization explicitly permits entity/window regeneration. The previous implementation exhausted only entities at one fixed window and omitted the authorized explicit-window fallback. The prior 269-event failure log remains independently preserved at `/tmp/v4_round1_repair_before/failed_expanded_battery_regen_log.jsonl`, SHA-256 `a7266d7a405d8c820a8e77fb0b2e79f191357f190e318699bdab4cf1f2e7ee1b`; it is not erased or recast as exhaustion of all legal windows.

Rules for the forthcoming trial, independent of candidate outcomes:

1. Preserve each slot's preferred original expression and existing family, metric, scope, event type, and three paraphrases. Keep seed 42 and the existing seeded entity shuffle/offset.
2. Try the original window first. Only after every entity position for that window is exhausted may an explicit range advance to another window.
3. For explicit ranges, keep duration unchanged. Enumerate every other fully covered start date in ascending order. Use the same already-determined entity order for every window; consume no new RNG draws for fallback windows.
4. Relative forms keep their exact frozen bounds and never become explicit forms. Controls remain window-free.
5. The finite bound is the complete number of window/entity positions, not an arbitrary retry cap. A two-day range has 13 legal positions in the 14-day snapshot and, for repository scope, at most 13 x 100 positions. Declare exhaustion only after the complete eligible pool is covered.
6. Preserve all six perturbations and the stated out-of-coverage exclusion policy. Every eligible perturbation must change the reference multiset. No metric, threshold, window length, sensitivity condition, or count is relaxed.
7. Log every rejected candidate with preferred expression, candidate expression/bounds, window index, entity position, entity, and objective reason. Accepted expression/bounds must propagate consistently to text, SQL, probes, output records, overlap inventory, and r2 review.
8. Preserve the old 22-question review. r2 retains its IDs/current replacements and covers every actual expression using window-expression x family strata. The number of actual expressions and review rows is derived from the result, not forced to the former ten/30.

### Existing duplicate semantic instances and deterministic eligibility

The unchanged pre-repair dataset contains three repeated semantic-instance pairs across different semantic_case_id values:

- `window_new_stars_01_language` / `window_new_stars_09_language`;
- `window_collaboration_events_01_language` / `window_collaboration_events_09_language`;
- `window_active_contributors_00_repo` / `window_active_contributors_01_repo`.

The semantic identity is family + entity/scope/event-type parameters + effective boundaries; wording aliases do not create a new semantic instance. The three paraphrases of one case intentionally share that identity. Per the explicit instruction to handle such duplicates, once an identity is assigned to an earlier case, it is ineligible for later cases. Traverse onward deterministically without executing that duplicate's SQL, and record a separate `dedup_exclusion` event. This is distinguished from an item-8 failed validation; it must not be mislabeled as a nonempty/sensitivity failure. No question slot is dropped and no duplicate constraint is weakened.

The implementation/tests may change only within the authorized phase-generation scope. context.py, glossary, original audit/adjudication, old review, historical artifacts, and the previous failure evidence remain unchanged. No actual replacement date or successful candidate is chosen in advance or based on perceived difficulty.

## Complete-pool trial result — relative-window hard stop

**The explicit-window fallback omission is corrected, but Round 1 regeneration is still blocked by a different fully exhausted case.** No further trial, seed change, metric change, relative-window change, or relaxed assertion was attempted after this result.

The generation-specific pytest command completed with **33 passed, 1 failed in 52.23 seconds**, exit code 1. The failed full-generation reproducibility test stopped in its first generation; no second completed output exists.

Exact failure: `No candidate satisfies the constraints after 100 deterministic attempts across 1 complete window/entity pools: day_of_week_01`.

Case: day-of-week aggregation of `PushEvent` records for `previous week`, fixed bounds `[2026-10-08, 2026-10-15)`. Relative expressions cannot be moved or converted to explicit intervals under the recorded rule. Therefore this case has exactly one admissible window and 100 repository positions. All 100 unique repositories were covered; no position was excluded for semantic duplication.

| Failed-case result | Repositories |
| --- | ---: |
| Nonzero baseline, but end + 1 produced the same result multiset | 55 |
| All-zero baseline metric | 45 |

The end-plus-one perturbation is `[2026-10-08, 2026-10-16)`, entirely within the snapshot. Its failures cannot be removed under the out-of-coverage exemption. This is actual per-repository result evidence; no unqueried global event-count claim is made.

### The original explicit-window blocker was passed

The corrected run retained all 100 original-window failures for `window_active_contributors_03_repo`, declared its full pool as 1,300 positions, and logged subsequent window attempts 2, 3, and 4. Execution then reached the later day-of-week case, proving the earlier semantic case completed. The accepted candidate is not reconstructed or invented from failure-only log rows.

### Complete partial-run event counts

| Event kind | Count |
| --- | ---: |
| Item-8 hard assertion failures | 1518 |
| Separately classified semantic-duplicate pool exclusions | 10 |
| Total logged candidate events | 1528 |

| Objective reason | Events |
| --- | ---: |
| all_zero_aggregate | 876 |
| duplicate_semantic_candidate | 10 |
| empty_reference | 28 |
| insensitive_both_minus_one | 1 |
| insensitive_both_plus_one | 14 |
| insensitive_end_minus_one | 117 |
| insensitive_end_plus_one | 103 |
| insensitive_start_minus_one | 8 |
| insensitive_start_plus_one | 371 |

Complete-pool failed-run log: `/tmp/v4_round1_repair_before/failed_complete_pool_regen_log.jsonl`.
Log SHA-256: `f3b6d7f80c819bf1e99ecd76138c5e90e481e921f82b64dda5ea0f779e5575d4`.
The previous 269-event log remains separately preserved at its original path and digest. Both logs are outside the repository so the official log associated with the still-current dataset remains intact.

### Exhausted relative-case inventory

| Attempt | Repository | Reason |
| ---: | --- | --- |
| 1 | avelino/awesome-go | insensitive_end_plus_one |
| 2 | Comfy-Org/ComfyUI | insensitive_end_plus_one |
| 3 | CyC2018/CS-Notes | all_zero_aggregate |
| 4 | n8n-io/n8n | insensitive_end_plus_one |
| 5 | ripienaar/free-for-dev | insensitive_end_plus_one |
| 6 | affaan-m/ECC | insensitive_end_plus_one |
| 7 | public-apis/public-apis | insensitive_end_plus_one |
| 8 | godotengine/godot | insensitive_end_plus_one |
| 9 | trimstray/the-book-of-secret-knowledge | all_zero_aggregate |
| 10 | airbnb/javascript | all_zero_aggregate |
| 11 | 2dust/v2rayN | all_zero_aggregate |
| 12 | vuejs/vue | all_zero_aggregate |
| 13 | langgenius/dify | insensitive_end_plus_one |
| 14 | vercel/next.js | insensitive_end_plus_one |
| 15 | kubernetes/kubernetes | insensitive_end_plus_one |
| 16 | trekhleb/javascript-algorithms | all_zero_aggregate |
| 17 | awesome-selfhosted/awesome-selfhosted | insensitive_end_plus_one |
| 18 | obra/superpowers | all_zero_aggregate |
| 19 | rustdesk/rustdesk | insensitive_end_plus_one |
| 20 | ossu/computer-science | all_zero_aggregate |
| 21 | morluto/rea | insensitive_end_plus_one |
| 22 | deepseek-ai/deepseek-harness | insensitive_end_plus_one |
| 23 | clash-verge-rev/clash-verge-rev | insensitive_end_plus_one |
| 24 | torvalds/linux | insensitive_end_plus_one |
| 25 | yangshun/tech-interview-handbook | all_zero_aggregate |
| 26 | Chalarangelo/30-seconds-of-code | all_zero_aggregate |
| 27 | labuladong/fucking-algorithm | all_zero_aggregate |
| 28 | openai/codex | insensitive_end_plus_one |
| 29 | Graphify-Labs/graphify | insensitive_end_plus_one |
| 30 | nilbuild/developer-roadmap | insensitive_end_plus_one |
| 31 | sindresorhus/awesome | all_zero_aggregate |
| 32 | NousResearch/hermes-agent | insensitive_end_plus_one |
| 33 | TheAlgorithms/Python | all_zero_aggregate |
| 34 | codecrafters-io/build-your-own-x | all_zero_aggregate |
| 35 | electron/electron | insensitive_end_plus_one |
| 36 | firecrawl/firecrawl | insensitive_end_plus_one |
| 37 | vinta/awesome-python | insensitive_end_plus_one |
| 38 | AUTOMATIC1111/stable-diffusion-webui | all_zero_aggregate |
| 39 | Shubhamsaboo/awesome-llm-apps | all_zero_aggregate |
| 40 | react/react-native | insensitive_end_plus_one |
| 41 | github/spec-kit | insensitive_end_plus_one |
| 42 | github/gitignore | all_zero_aggregate |
| 43 | twbs/bootstrap | insensitive_end_plus_one |
| 44 | EbookFoundation/free-programming-books | all_zero_aggregate |
| 45 | msitarzewski/agency-agents | all_zero_aggregate |
| 46 | justjavac/free-programming-books-zh_CN | all_zero_aggregate |
| 47 | 521xueweihan/HelloGitHub | all_zero_aggregate |
| 48 | nodejs/node | insensitive_end_plus_one |
| 49 | Significant-Gravitas/AutoGPT | insensitive_end_plus_one |
| 50 | practical-tutorials/project-based-learning | all_zero_aggregate |
| 51 | ollama/ollama | insensitive_end_plus_one |
| 52 | Genymobile/scrcpy | all_zero_aggregate |
| 53 | langchain-ai/langchain | insensitive_end_plus_one |
| 54 | langflow-ai/langflow | insensitive_end_plus_one |
| 55 | ohmyzsh/ohmyzsh | insensitive_end_plus_one |
| 56 | harry0703/MoneyPrinterTurbo | insensitive_end_plus_one |
| 57 | jackfrued/Python-100-Days | all_zero_aggregate |
| 58 | ultraworkers/claw-code | insensitive_end_plus_one |
| 59 | openclaw/openclaw | insensitive_end_plus_one |
| 60 | freeCodeCamp/freeCodeCamp | insensitive_end_plus_one |
| 61 | donnemartin/system-design-primer | all_zero_aggregate |
| 62 | anomalyco/opencode | insensitive_end_plus_one |
| 63 | excalidraw/excalidraw | insensitive_end_plus_one |
| 64 | x1xhlol/system-prompts-and-models-of-ai-tools | all_zero_aggregate |
| 65 | react/react | insensitive_end_plus_one |
| 66 | jlevy/the-art-of-command-line | all_zero_aggregate |
| 67 | rust-lang/rust | insensitive_end_plus_one |
| 68 | browser-use/browser-use | all_zero_aggregate |
| 69 | tensorflow/tensorflow | insensitive_end_plus_one |
| 70 | f/prompts.chat | all_zero_aggregate |
| 71 | DigitalPlatDev/FreeDomain | all_zero_aggregate |
| 72 | iptv-org/iptv | all_zero_aggregate |
| 73 | mattpocock/skills | insensitive_end_plus_one |
| 74 | microsoft/vscode | insensitive_end_plus_one |
| 75 | open-webui/open-webui | insensitive_end_plus_one |
| 76 | golang/go | insensitive_end_plus_one |
| 77 | yt-dlp/yt-dlp | all_zero_aggregate |
| 78 | krahets/hello-algo | insensitive_end_plus_one |
| 79 | shadcn-ui/ui | insensitive_end_plus_one |
| 80 | Hack-with-Github/Awesome-Hacking | all_zero_aggregate |
| 81 | flutter/flutter | insensitive_end_plus_one |
| 82 | anthropics/skills | all_zero_aggregate |
| 83 | getify/You-Dont-Know-JS | all_zero_aggregate |
| 84 | ggml-org/llama.cpp | insensitive_end_plus_one |
| 85 | VoltAgent/awesome-design-md | all_zero_aggregate |
| 86 | multica-ai/andrej-karpathy-skills | all_zero_aggregate |
| 87 | microsoft/generative-ai-for-beginners | all_zero_aggregate |
| 88 | microsoft/PowerToys | insensitive_end_plus_one |
| 89 | DietrichGebert/ponytail | insensitive_end_plus_one |
| 90 | farion1231/cc-switch | insensitive_end_plus_one |
| 91 | ytdl-org/youtube-dl | all_zero_aggregate |
| 92 | huggingface/transformers | insensitive_end_plus_one |
| 93 | 996icu/996.ICU | all_zero_aggregate |
| 94 | jwasham/coding-interview-university | all_zero_aggregate |
| 95 | Snailclimb/JavaGuide | all_zero_aggregate |
| 96 | garrytan/gstack | insensitive_end_plus_one |
| 97 | massgravel/Microsoft-Activation-Scripts | all_zero_aggregate |
| 98 | nextlevelbuilder/ui-ux-pro-max-skill | all_zero_aggregate |
| 99 | anthropics/claude-code | insensitive_end_plus_one |
| 100 | microsoft/markitdown | all_zero_aggregate |

### Delivered and not executed

- Generator and corresponding tests now implement the predeclared complete same-length window/entity pool and semantic uniqueness. Tests no longer force the former ten actual expressions or exactly 30 r2 questions; they assert coverage of every actual expression and preservation/replacement marking of the original 22 IDs.
- The seed remains 42; original window trials and objective failure evidence are retained. No reference-SQL family implementation, metric, family count, paraphrase count, sensitivity assertion, context.py, glossary, or frozen historical file was changed.
- No new formal question set, official regeneration log, overlap audit, or r2 review was published. The old 300-question set, old official log, and old 22-question review remain byte-identical to their pre-repair backups. Their published changed-question count is zero; this is not a claim that the extended battery passes the old set.
- Generation reached semantic slot 76 (zero-based) before failure, so 76 cases / 228 question records had been constructed in memory by the fixed loop order. Those records were not published or selected as a partial replacement.
- The actual new-entry gate was rerun as the generation precondition. The separate old-entry 86-question replay and complete pytest suite were not rerun after the hard stop; no earlier success count is presented as a current complete-suite result.
- Human Round 1 review text is still missing, and no round1 review document or human approval was fabricated.
- Continuing this particular relative-window/PushEvent case would require a new decision about one of the fixed constraints; neither selecting another relative meaning nor changing the metric or dropping the in-coverage perturbation is performed here.

## Adjudicated metric/window/battery ladder — recorded before execution

The latest human ruling authorizes the following finite fallback ladder. Seed 42, 100 semantic cases, 300 synchronized paraphrases, family/layer counts, targeted labels, nonempty/nonzero references, deterministic Top-N ties, and semantic uniqueness remain mandatory.

- Tier 0 preserves the existing preferred metric and original window/entity pool: preferred explicit window first, followed by every same-length explicit start in ascending order. Relative expressions retain their own fixed meaning.
- Tier 1, after that pool is exhausted, tries the remaining already-implemented event metrics in this fixed order: WatchEvent, PushEvent, IssuesEvent, PullRequestEvent, IssueCommentEvent (omit the preferred metric). It uses the same base window pool for each metric. These are the existing EVENT_TYPES in gen_v4_questions.py, used by the four targeted advanced and two adjacent families. The three window families each bind one glossary-defined metric; they have no alternative metric within that family. Catalog controls have no alternatives and no sensitivity relaxation.
- Tier 2, after all tier-1 candidates are exhausted, enumerates every remaining authorized expression: three named relative forms plus all 105 canonical explicit intervals within the actual 14-day snapshot. Sort by same expression type first, same length first, then absolute length difference, length, start date, end date, expression text. For each expression use the preferred metric followed by the remaining metrics above. An expression's meaning never changes; replacements update question, SQL, probe, overlap inventory, and review together.
- Every window/metric combination uses the same seed-derived entity order, without new RNG draws. Bounds are finite: 108 expression forms times the family's metric count times entity count; base-pool entries are included exactly once. Repeated effective semantic identities already assigned to another case remain ineligible and are separately logged.
- Tier 3 is allowed only after the entire strict pool is exhausted. Choose the first candidate in that same order that satisfied all non-battery constraints but failed at least one eligible sensitivity perturbation. Mark battery_relaxed=true for all three paraphrases. Record all six perturbation statuses, executed result rows and hashes, failed-perturbation names, excluded out-of-coverage cases, and strict-pool exhaustion. Count relaxation by semantic case, capped at two; a third required relaxation is a hard stop. No empty/zero/duplicate reference can be rescued by this tier.
- Evaluate every eligible perturbation for each otherwise-valid candidate, even after one insensitive result, so evidence is complete. Log all candidate failures, duplicate exclusions, and acceptances with preferred/actual metric, expression, tier, entity, and boundaries. The two earlier failure logs remain untouched.

Endpoint SQL parsing remains a future analysis-stage dependency, not an implemented capability of this phase. Human Round 1 comments remain pending and no round1.md or signature will be invented. Formal outputs are replaced only after complete generation and required validation; original review and backups remain unchanged.

## Completed adjudicated ladder run

The new human-authorized ladder resolved the previous hard stop. Both seed-42 full generations produced byte-identical question sets, regeneration logs, overlap audits, and r2 reviews. No seed or difficulty selection was used. The previous two failed-run logs remain separate evidence, not part of the final successful-run counts.

Validation: the full pytest suite passed 405 tests in 206.44 seconds (325 historical tests plus 35 boundary/replay tests and 45 generation tests). A separate pre-suite unit subset passed 44 tests with the full-generation test deselected; these are not added again to the suite total. The separate real old-entry replay passed 86/86 complete-context byte comparisons; its report is byte-identical to the existing v4_c21_replay.md. The separate new-entry real-function check passed all 345 cases (331 output comparisons and 14 required rejections), covering all 105 explicit intervals. Initial direct-file CLI invocations failed at package import before any check ran; module invocations completed successfully, without code changes.

Publication is performed only after these completed validations. Human Round 1 comments remain unavailable, so v4_sample_review_round1.md has not been created and no human sign-off or frozen status is claimed. Phase B wiring and SQL endpoint analysis remain unimplemented future work.

### Final counts

Questions: 300; semantic cases: 100; layers: {'window': 180, 'advanced_sql': 90, 'control': 30}; targeted labels: {'True': 240, 'False': 60}; paraphrases: {'literal': 100, 'colloquial': 100, 'distractor': 100}.

| Family | Questions |
| --- | ---: |
| catalog_lookup | 15 |
| consecutive_day_runs | 15 |
| daily_trend | 15 |
| day_of_week | 15 |
| day_over_day | 15 |
| language_composition | 15 |
| running_total | 15 |
| session_segmentation | 15 |
| window_active_contributors | 60 |
| window_collaboration_events | 60 |
| window_new_stars | 60 |

Accepted-case tiers: {'0': 97, '1': 3}. Battery-relaxed cases: 0 / 2. No eligible perturbation failure was waived in the published set.
Eligible perturbations: 342 across 90 window-bearing semantic cases, repeated as 1026 evidence records across their paraphrases. Excluded out-of-coverage perturbations: 198 semantic / 594 question records.
Distractor probes: 100; triggered: 90; probes never filter candidate selection.

Final-run log events: 1853; event types: {'candidate_accepted': 100, 'hard_assertion_failure': 1743, 'dedup_exclusion': 10}.

| Primary objective rejection reason | Candidates |
| --- | ---: |
| all_zero_aggregate | 932 |
| empty_reference | 76 |
| insensitive_both_minus_one | 1 |
| insensitive_both_plus_one | 15 |
| insensitive_end_minus_one | 138 |
| insensitive_end_plus_one | 156 |
| insensitive_start_minus_one | 8 |
| insensitive_start_plus_one | 417 |

The reason field names the first failed perturbation in fixed battery order; each otherwise-valid candidate stores the complete eligible battery, so additional failures are retained rather than suppressed. Accepted events and dedup exclusions are not counted as hard-assertion regenerations.

Uniqueness: 100 distinct family/parameter/effective-bound semantic identities, three paraphrases each; 300 distinct normalized full questions; zero normalized overlap with the 86 historical questions. Ten candidate duplicates were explicitly excluded, not published.

### Final form of every semantic case

| Case | Tier | Preferred / accepted event metric | Preferred / accepted window | Scope / entity | Accepted bounds | Relaxed |
| --- | ---: | --- | --- | --- | --- | --- |
| window_new_stars_00_repo | 0 | None / None | the last 7 days / the last 7 days | repo / firecrawl/firecrawl | ['2026-10-15', '2026-10-22'] | False |
| window_new_stars_00_language | 0 | None / None | the last 7 days / the last 7 days | language / Shell | ['2026-10-15', '2026-10-22'] | False |
| window_new_stars_01_repo | 0 | None / None | last week / last week | repo / awesome-selfhosted/awesome-selfhosted | ['2026-10-15', '2026-10-22'] | False |
| window_new_stars_01_language | 0 | None / None | last week / last week | language / Markdown | ['2026-10-15', '2026-10-22'] | False |
| window_new_stars_02_repo | 0 | None / None | previous week / previous week | repo / DietrichGebert/ponytail | ['2026-10-08', '2026-10-15'] | False |
| window_new_stars_02_language | 0 | None / None | previous week / previous week | language / Rust | ['2026-10-08', '2026-10-15'] | False |
| window_new_stars_03_repo | 0 | None / None | October 8 through October 9, 2026 / October 8 through October 9, 2026 | repo / openclaw/openclaw | ['2026-10-08', '2026-10-10'] | False |
| window_new_stars_03_language | 0 | None / None | October 8 through October 9, 2026 / October 8 through October 9, 2026 | language / Python | ['2026-10-08', '2026-10-10'] | False |
| window_new_stars_04_repo | 0 | None / None | October 8 through October 10, 2026 / October 8 through October 10, 2026 | repo / harry0703/MoneyPrinterTurbo | ['2026-10-08', '2026-10-11'] | False |
| window_new_stars_04_language | 0 | None / None | October 8 through October 10, 2026 / October 8 through October 10, 2026 | language / Python | ['2026-10-08', '2026-10-11'] | False |
| window_new_stars_05_repo | 0 | None / None | October 8 through October 12, 2026 / October 8 through October 12, 2026 | repo / harry0703/MoneyPrinterTurbo | ['2026-10-08', '2026-10-13'] | False |
| window_new_stars_05_language | 0 | None / None | October 8 through October 12, 2026 / October 8 through October 12, 2026 | language / JavaScript | ['2026-10-08', '2026-10-13'] | False |
| window_new_stars_06_repo | 0 | None / None | October 8 through October 14, 2026 / October 8 through October 14, 2026 | repo / morluto/rea | ['2026-10-08', '2026-10-15'] | False |
| window_new_stars_06_language | 0 | None / None | October 8 through October 14, 2026 / October 8 through October 14, 2026 | language / C | ['2026-10-08', '2026-10-15'] | False |
| window_new_stars_07_repo | 0 | None / None | October 8 through October 17, 2026 / October 8 through October 17, 2026 | repo / openai/codex | ['2026-10-08', '2026-10-18'] | False |
| window_new_stars_07_language | 0 | None / None | October 8 through October 17, 2026 / October 8 through October 17, 2026 | language / Jupyter Notebook | ['2026-10-08', '2026-10-18'] | False |
| window_new_stars_08_repo | 0 | None / None | October 8 through October 21, 2026 / October 8 through October 21, 2026 | repo / awesome-selfhosted/awesome-selfhosted | ['2026-10-08', '2026-10-22'] | False |
| window_new_stars_08_language | 0 | None / None | October 8 through October 21, 2026 / October 8 through October 21, 2026 | language / Python | ['2026-10-08', '2026-10-22'] | False |
| window_new_stars_09_repo | 0 | None / None | October 15 through October 21, 2026 / October 15 through October 21, 2026 | repo / farion1231/cc-switch | ['2026-10-15', '2026-10-22'] | False |
| window_new_stars_09_language | 0 | None / None | October 15 through October 21, 2026 / October 15 through October 21, 2026 | language / Python | ['2026-10-15', '2026-10-22'] | False |
| window_collaboration_events_00_repo | 0 | None / None | the last 7 days / the last 7 days | repo / morluto/rea | ['2026-10-15', '2026-10-22'] | False |
| window_collaboration_events_00_language | 0 | None / None | the last 7 days / the last 7 days | language / Python | ['2026-10-15', '2026-10-22'] | False |
| window_collaboration_events_01_repo | 0 | None / None | last week / last week | repo / godotengine/godot | ['2026-10-15', '2026-10-22'] | False |
| window_collaboration_events_01_language | 0 | None / None | last week / last week | language / TypeScript | ['2026-10-15', '2026-10-22'] | False |
| window_collaboration_events_02_repo | 0 | None / None | previous week / previous week | repo / langgenius/dify | ['2026-10-08', '2026-10-15'] | False |
| window_collaboration_events_02_language | 0 | None / None | previous week / previous week | language / Python | ['2026-10-08', '2026-10-15'] | False |
| window_collaboration_events_03_repo | 0 | None / None | October 8 through October 9, 2026 / October 8 through October 9, 2026 | repo / openai/codex | ['2026-10-08', '2026-10-10'] | False |
| window_collaboration_events_03_language | 0 | None / None | October 8 through October 9, 2026 / October 8 through October 9, 2026 | language / Dart | ['2026-10-08', '2026-10-10'] | False |
| window_collaboration_events_04_repo | 0 | None / None | October 8 through October 10, 2026 / October 8 through October 10, 2026 | repo / openai/codex | ['2026-10-08', '2026-10-11'] | False |
| window_collaboration_events_04_language | 0 | None / None | October 8 through October 10, 2026 / October 8 through October 10, 2026 | language / TypeScript | ['2026-10-08', '2026-10-11'] | False |
| window_collaboration_events_05_repo | 0 | None / None | October 8 through October 12, 2026 / October 8 through October 12, 2026 | repo / github/spec-kit | ['2026-10-08', '2026-10-13'] | False |
| window_collaboration_events_05_language | 0 | None / None | October 8 through October 12, 2026 / October 8 through October 12, 2026 | language / C++ | ['2026-10-08', '2026-10-13'] | False |
| window_collaboration_events_06_repo | 0 | None / None | October 8 through October 14, 2026 / October 8 through October 14, 2026 | repo / openclaw/openclaw | ['2026-10-08', '2026-10-15'] | False |
| window_collaboration_events_06_language | 0 | None / None | October 8 through October 14, 2026 / October 8 through October 14, 2026 | language / C++ | ['2026-10-08', '2026-10-15'] | False |
| window_collaboration_events_07_repo | 0 | None / None | October 8 through October 17, 2026 / October 8 through October 17, 2026 | repo / anthropics/claude-code | ['2026-10-08', '2026-10-18'] | False |
| window_collaboration_events_07_language | 0 | None / None | October 8 through October 17, 2026 / October 8 through October 17, 2026 | language / C | ['2026-10-08', '2026-10-18'] | False |
| window_collaboration_events_08_repo | 0 | None / None | October 8 through October 21, 2026 / October 8 through October 21, 2026 | repo / anthropics/claude-code | ['2026-10-08', '2026-10-22'] | False |
| window_collaboration_events_08_language | 0 | None / None | October 8 through October 21, 2026 / October 8 through October 21, 2026 | language / Python | ['2026-10-08', '2026-10-22'] | False |
| window_collaboration_events_09_repo | 0 | None / None | October 15 through October 21, 2026 / October 15 through October 21, 2026 | repo / electron/electron | ['2026-10-15', '2026-10-22'] | False |
| window_collaboration_events_09_language | 0 | None / None | October 15 through October 21, 2026 / October 15 through October 21, 2026 | language / C++ | ['2026-10-15', '2026-10-22'] | False |
| window_active_contributors_00_repo | 0 | None / None | the last 7 days / the last 7 days | repo / NousResearch/hermes-agent | ['2026-10-15', '2026-10-22'] | False |
| window_active_contributors_00_language | 0 | None / None | the last 7 days / the last 7 days | language / Rust | ['2026-10-15', '2026-10-22'] | False |
| window_active_contributors_01_repo | 0 | None / None | last week / last week | repo / huggingface/transformers | ['2026-10-15', '2026-10-22'] | False |
| window_active_contributors_01_language | 0 | None / None | last week / last week | language / JavaScript | ['2026-10-15', '2026-10-22'] | False |
| window_active_contributors_02_repo | 0 | None / None | previous week / previous week | repo / flutter/flutter | ['2026-10-08', '2026-10-15'] | False |
| window_active_contributors_02_language | 0 | None / None | previous week / previous week | language / Python | ['2026-10-08', '2026-10-15'] | False |
| window_active_contributors_03_repo | 0 | None / None | October 8 through October 9, 2026 / October 11 through October 12, 2026 | repo / langgenius/dify | ['2026-10-11', '2026-10-13'] | False |
| window_active_contributors_03_language | 0 | None / None | October 8 through October 9, 2026 / October 8 through October 9, 2026 | language / TypeScript | ['2026-10-08', '2026-10-10'] | False |
| window_active_contributors_04_repo | 0 | None / None | October 8 through October 10, 2026 / October 8 through October 10, 2026 | repo / ggml-org/llama.cpp | ['2026-10-08', '2026-10-11'] | False |
| window_active_contributors_04_language | 0 | None / None | October 8 through October 10, 2026 / October 8 through October 10, 2026 | language / Python | ['2026-10-08', '2026-10-11'] | False |
| window_active_contributors_05_repo | 0 | None / None | October 8 through October 12, 2026 / October 8 through October 12, 2026 | repo / openclaw/openclaw | ['2026-10-08', '2026-10-13'] | False |
| window_active_contributors_05_language | 0 | None / None | October 8 through October 12, 2026 / October 8 through October 12, 2026 | language / TypeScript | ['2026-10-08', '2026-10-13'] | False |
| window_active_contributors_06_repo | 0 | None / None | October 8 through October 14, 2026 / October 10 through October 16, 2026 | repo / openclaw/openclaw | ['2026-10-10', '2026-10-17'] | False |
| window_active_contributors_06_language | 0 | None / None | October 8 through October 14, 2026 / October 8 through October 14, 2026 | language / Dart | ['2026-10-08', '2026-10-15'] | False |
| window_active_contributors_07_repo | 0 | None / None | October 8 through October 17, 2026 / October 8 through October 17, 2026 | repo / rust-lang/rust | ['2026-10-08', '2026-10-18'] | False |
| window_active_contributors_07_language | 0 | None / None | October 8 through October 17, 2026 / October 8 through October 17, 2026 | language / Rust | ['2026-10-08', '2026-10-18'] | False |
| window_active_contributors_08_repo | 0 | None / None | October 8 through October 21, 2026 / October 8 through October 21, 2026 | repo / n8n-io/n8n | ['2026-10-08', '2026-10-22'] | False |
| window_active_contributors_08_language | 0 | None / None | October 8 through October 21, 2026 / October 8 through October 21, 2026 | language / Python | ['2026-10-08', '2026-10-22'] | False |
| window_active_contributors_09_repo | 0 | None / None | October 15 through October 21, 2026 / October 11 through October 17, 2026 | repo / openclaw/openclaw | ['2026-10-11', '2026-10-18'] | False |
| window_active_contributors_09_language | 0 | None / None | October 15 through October 21, 2026 / October 15 through October 21, 2026 | language / Python | ['2026-10-15', '2026-10-22'] | False |
| daily_trend_00 | 0 | WatchEvent / WatchEvent | the last 7 days / the last 7 days | repo / Hack-with-Github/Awesome-Hacking | ['2026-10-15', '2026-10-22'] | False |
| daily_trend_01 | 0 | PushEvent / PushEvent | previous week / previous week | repo / mattpocock/skills | ['2026-10-08', '2026-10-15'] | False |
| daily_trend_02 | 0 | IssuesEvent / IssuesEvent | October 8 through October 10, 2026 / October 8 through October 10, 2026 | repo / nodejs/node | ['2026-10-08', '2026-10-11'] | False |
| daily_trend_03 | 0 | PullRequestEvent / PullRequestEvent | October 8 through October 17, 2026 / October 8 through October 17, 2026 | repo / microsoft/vscode | ['2026-10-08', '2026-10-18'] | False |
| daily_trend_04 | 0 | IssueCommentEvent / IssueCommentEvent | October 8 through October 21, 2026 / October 8 through October 21, 2026 | repo / langgenius/dify | ['2026-10-08', '2026-10-22'] | False |
| running_total_00 | 0 | WatchEvent / WatchEvent | the last 7 days / the last 7 days | repo / ollama/ollama | ['2026-10-15', '2026-10-22'] | False |
| running_total_01 | 0 | PushEvent / PushEvent | previous week / previous week | repo / ollama/ollama | ['2026-10-08', '2026-10-15'] | False |
| running_total_02 | 0 | IssuesEvent / IssuesEvent | October 8 through October 10, 2026 / October 8 through October 10, 2026 | repo / electron/electron | ['2026-10-08', '2026-10-11'] | False |
| running_total_03 | 0 | PullRequestEvent / PullRequestEvent | October 8 through October 17, 2026 / October 8 through October 17, 2026 | repo / n8n-io/n8n | ['2026-10-08', '2026-10-18'] | False |
| running_total_04 | 0 | IssueCommentEvent / IssueCommentEvent | October 8 through October 21, 2026 / October 8 through October 21, 2026 | repo / Significant-Gravitas/AutoGPT | ['2026-10-08', '2026-10-22'] | False |
| day_over_day_00 | 0 | WatchEvent / WatchEvent | the last 7 days / the last 7 days | repo / AUTOMATIC1111/stable-diffusion-webui | ['2026-10-15', '2026-10-22'] | False |
| day_over_day_01 | 0 | PushEvent / PushEvent | previous week / previous week | repo / langgenius/dify | ['2026-10-08', '2026-10-15'] | False |
| day_over_day_02 | 0 | IssuesEvent / IssuesEvent | October 8 through October 10, 2026 / October 8 through October 10, 2026 | repo / react/react-native | ['2026-10-08', '2026-10-11'] | False |
| day_over_day_03 | 0 | PullRequestEvent / PullRequestEvent | October 8 through October 17, 2026 / October 8 through October 17, 2026 | repo / ultraworkers/claw-code | ['2026-10-08', '2026-10-18'] | False |
| day_over_day_04 | 0 | IssueCommentEvent / IssueCommentEvent | October 8 through October 21, 2026 / October 8 through October 21, 2026 | repo / ultraworkers/claw-code | ['2026-10-08', '2026-10-22'] | False |
| day_of_week_00 | 0 | WatchEvent / WatchEvent | the last 7 days / the last 7 days | repo / yangshun/tech-interview-handbook | ['2026-10-15', '2026-10-22'] | False |
| day_of_week_01 | 1 | PushEvent / WatchEvent | previous week / previous week | repo / Comfy-Org/ComfyUI | ['2026-10-08', '2026-10-15'] | False |
| day_of_week_02 | 0 | IssuesEvent / IssuesEvent | October 8 through October 10, 2026 / October 8 through October 10, 2026 | repo / langgenius/dify | ['2026-10-08', '2026-10-11'] | False |
| day_of_week_03 | 0 | PullRequestEvent / PullRequestEvent | October 8 through October 17, 2026 / October 8 through October 17, 2026 | repo / anomalyco/opencode | ['2026-10-08', '2026-10-18'] | False |
| day_of_week_04 | 0 | IssueCommentEvent / IssueCommentEvent | October 8 through October 21, 2026 / October 8 through October 21, 2026 | repo / golang/go | ['2026-10-08', '2026-10-22'] | False |
| session_segmentation_00 | 0 | WatchEvent / WatchEvent | the last 7 days / the last 7 days | repo / trimstray/the-book-of-secret-knowledge | ['2026-10-15', '2026-10-22'] | False |
| session_segmentation_01 | 1 | PushEvent / WatchEvent | previous week / previous week | repo / obra/superpowers | ['2026-10-08', '2026-10-15'] | False |
| session_segmentation_02 | 0 | IssuesEvent / IssuesEvent | October 8 through October 10, 2026 / October 8 through October 10, 2026 | repo / anthropics/claude-code | ['2026-10-08', '2026-10-11'] | False |
| session_segmentation_03 | 0 | PullRequestEvent / PullRequestEvent | October 8 through October 17, 2026 / October 8 through October 17, 2026 | repo / microsoft/vscode | ['2026-10-08', '2026-10-18'] | False |
| session_segmentation_04 | 0 | IssueCommentEvent / IssueCommentEvent | October 8 through October 21, 2026 / October 8 through October 21, 2026 | repo / kubernetes/kubernetes | ['2026-10-08', '2026-10-22'] | False |
| consecutive_day_runs_00 | 0 | WatchEvent / WatchEvent | the last 7 days / the last 7 days | repo / vinta/awesome-python | ['2026-10-15', '2026-10-22'] | False |
| consecutive_day_runs_01 | 1 | PushEvent / WatchEvent | previous week / previous week | repo / codecrafters-io/build-your-own-x | ['2026-10-08', '2026-10-15'] | False |
| consecutive_day_runs_02 | 0 | IssuesEvent / IssuesEvent | October 8 through October 10, 2026 / October 8 through October 10, 2026 | repo / NousResearch/hermes-agent | ['2026-10-08', '2026-10-11'] | False |
| consecutive_day_runs_03 | 0 | PullRequestEvent / PullRequestEvent | October 8 through October 17, 2026 / October 8 through October 17, 2026 | repo / rust-lang/rust | ['2026-10-08', '2026-10-18'] | False |
| consecutive_day_runs_04 | 0 | IssueCommentEvent / IssueCommentEvent | October 8 through October 21, 2026 / October 8 through October 21, 2026 | repo / NousResearch/hermes-agent | ['2026-10-08', '2026-10-22'] | False |
| catalog_lookup_00 | 0 | None / None | None / None | repo / github/spec-kit | None | False |
| catalog_lookup_01 | 0 | None / None | None / None | repo / github/gitignore | None | False |
| catalog_lookup_02 | 0 | None / None | None / None | repo / twbs/bootstrap | None | False |
| catalog_lookup_03 | 0 | None / None | None / None | repo / EbookFoundation/free-programming-books | None | False |
| catalog_lookup_04 | 0 | None / None | None / None | repo / msitarzewski/agency-agents | None | False |
| language_composition_00 | 0 | None / None | None / None | language / Batchfile | None | False |
| language_composition_01 | 0 | None / None | None / None | language / MDX | None | False |
| language_composition_02 | 0 | None / None | None / None | language / Python | None | False |
| language_composition_03 | 0 | None / None | None / None | language / Dart | None | False |
| language_composition_04 | 0 | None / None | None / None | language / JavaScript | None | False |

### Published question changes and r2 coverage

Previous question SHA-256: `1e33b109a3af2ffcd74926e49876332cd6173bc6a5476000b623fe9689877067`.
New question SHA-256: `829ec0475c1ba1c090c8b1926221124df092af8b35b81ccc2a0a92e1fa897dc1`.
Original 22-question review SHA-256 remains `8668908ccfc54b2ee89673a37574e9c6a2f6f00fb409c50661c8dbdffc8c6278`.
Original question, original review, and original log backups remain in /tmp/v4_round1_repair_before and /tmp/v4_ladder_before/eval. The original review file is not overwritten.

Counts and complete ID lists (record changes include metadata; substantive changes are the union of text, SQL, answer, and parameter changes):

```json
{
  "old_questions_sha256": "1e33b109a3af2ffcd74926e49876332cd6173bc6a5476000b623fe9689877067",
  "new_questions_sha256": "829ec0475c1ba1c090c8b1926221124df092af8b35b81ccc2a0a92e1fa897dc1",
  "original_review_sha256": "8668908ccfc54b2ee89673a37574e9c6a2f6f00fb409c50661c8dbdffc8c6278",
  "record_changed_ids": [
    "v4_001",
    "v4_002",
    "v4_003",
    "v4_004",
    "v4_005",
    "v4_006",
    "v4_007",
    "v4_008",
    "v4_009",
    "v4_010",
    "v4_011",
    "v4_012",
    "v4_013",
    "v4_014",
    "v4_015",
    "v4_016",
    "v4_017",
    "v4_018",
    "v4_019",
    "v4_020",
    "v4_021",
    "v4_022",
    "v4_023",
    "v4_024",
    "v4_025",
    "v4_026",
    "v4_027",
    "v4_028",
    "v4_029",
    "v4_030",
    "v4_031",
    "v4_032",
    "v4_033",
    "v4_034",
    "v4_035",
    "v4_036",
    "v4_037",
    "v4_038",
    "v4_039",
    "v4_040",
    "v4_041",
    "v4_042",
    "v4_043",
    "v4_044",
    "v4_045",
    "v4_046",
    "v4_047",
    "v4_048",
    "v4_049",
    "v4_050",
    "v4_051",
    "v4_052",
    "v4_053",
    "v4_054",
    "v4_055",
    "v4_056",
    "v4_057",
    "v4_058",
    "v4_059",
    "v4_060",
    "v4_061",
    "v4_062",
    "v4_063",
    "v4_064",
    "v4_065",
    "v4_066",
    "v4_067",
    "v4_068",
    "v4_069",
    "v4_070",
    "v4_071",
    "v4_072",
    "v4_073",
    "v4_074",
    "v4_075",
    "v4_076",
    "v4_077",
    "v4_078",
    "v4_079",
    "v4_080",
    "v4_081",
    "v4_082",
    "v4_083",
    "v4_084",
    "v4_085",
    "v4_086",
    "v4_087",
    "v4_088",
    "v4_089",
    "v4_090",
    "v4_091",
    "v4_092",
    "v4_093",
    "v4_094",
    "v4_095",
    "v4_096",
    "v4_097",
    "v4_098",
    "v4_099",
    "v4_100",
    "v4_101",
    "v4_102",
    "v4_103",
    "v4_104",
    "v4_105",
    "v4_106",
    "v4_107",
    "v4_108",
    "v4_109",
    "v4_110",
    "v4_111",
    "v4_112",
    "v4_113",
    "v4_114",
    "v4_115",
    "v4_116",
    "v4_117",
    "v4_118",
    "v4_119",
    "v4_120",
    "v4_121",
    "v4_122",
    "v4_123",
    "v4_124",
    "v4_125",
    "v4_126",
    "v4_127",
    "v4_128",
    "v4_129",
    "v4_130",
    "v4_131",
    "v4_132",
    "v4_133",
    "v4_134",
    "v4_135",
    "v4_136",
    "v4_137",
    "v4_138",
    "v4_139",
    "v4_140",
    "v4_141",
    "v4_142",
    "v4_143",
    "v4_144",
    "v4_145",
    "v4_146",
    "v4_147",
    "v4_148",
    "v4_149",
    "v4_150",
    "v4_151",
    "v4_152",
    "v4_153",
    "v4_154",
    "v4_155",
    "v4_156",
    "v4_157",
    "v4_158",
    "v4_159",
    "v4_160",
    "v4_161",
    "v4_162",
    "v4_163",
    "v4_164",
    "v4_165",
    "v4_166",
    "v4_167",
    "v4_168",
    "v4_169",
    "v4_170",
    "v4_171",
    "v4_172",
    "v4_173",
    "v4_174",
    "v4_175",
    "v4_176",
    "v4_177",
    "v4_178",
    "v4_179",
    "v4_180",
    "v4_181",
    "v4_182",
    "v4_183",
    "v4_184",
    "v4_185",
    "v4_186",
    "v4_187",
    "v4_188",
    "v4_189",
    "v4_190",
    "v4_191",
    "v4_192",
    "v4_193",
    "v4_194",
    "v4_195",
    "v4_196",
    "v4_197",
    "v4_198",
    "v4_199",
    "v4_200",
    "v4_201",
    "v4_202",
    "v4_203",
    "v4_204",
    "v4_205",
    "v4_206",
    "v4_207",
    "v4_208",
    "v4_209",
    "v4_210",
    "v4_211",
    "v4_212",
    "v4_213",
    "v4_214",
    "v4_215",
    "v4_216",
    "v4_217",
    "v4_218",
    "v4_219",
    "v4_220",
    "v4_221",
    "v4_222",
    "v4_223",
    "v4_224",
    "v4_225",
    "v4_226",
    "v4_227",
    "v4_228",
    "v4_229",
    "v4_230",
    "v4_231",
    "v4_232",
    "v4_233",
    "v4_234",
    "v4_235",
    "v4_236",
    "v4_237",
    "v4_238",
    "v4_239",
    "v4_240",
    "v4_241",
    "v4_242",
    "v4_243",
    "v4_244",
    "v4_245",
    "v4_246",
    "v4_247",
    "v4_248",
    "v4_249",
    "v4_250",
    "v4_251",
    "v4_252",
    "v4_253",
    "v4_254",
    "v4_255",
    "v4_256",
    "v4_257",
    "v4_258",
    "v4_259",
    "v4_260",
    "v4_261",
    "v4_262",
    "v4_263",
    "v4_264",
    "v4_265",
    "v4_266",
    "v4_267",
    "v4_268",
    "v4_269",
    "v4_270",
    "v4_271",
    "v4_272",
    "v4_273",
    "v4_274",
    "v4_275",
    "v4_276",
    "v4_277",
    "v4_278",
    "v4_279",
    "v4_280",
    "v4_281",
    "v4_282",
    "v4_283",
    "v4_284",
    "v4_285",
    "v4_286",
    "v4_287",
    "v4_288",
    "v4_289",
    "v4_290",
    "v4_291",
    "v4_292",
    "v4_293",
    "v4_294",
    "v4_295",
    "v4_296",
    "v4_297",
    "v4_298",
    "v4_299",
    "v4_300"
  ],
  "question_changed_ids": [
    "v4_013",
    "v4_014",
    "v4_015",
    "v4_019",
    "v4_020",
    "v4_021",
    "v4_022",
    "v4_023",
    "v4_024",
    "v4_025",
    "v4_026",
    "v4_027",
    "v4_040",
    "v4_041",
    "v4_042",
    "v4_058",
    "v4_059",
    "v4_060",
    "v4_091",
    "v4_092",
    "v4_093",
    "v4_106",
    "v4_107",
    "v4_108",
    "v4_118",
    "v4_119",
    "v4_120",
    "v4_121",
    "v4_122",
    "v4_123",
    "v4_127",
    "v4_128",
    "v4_129",
    "v4_130",
    "v4_131",
    "v4_132",
    "v4_133",
    "v4_134",
    "v4_135",
    "v4_136",
    "v4_137",
    "v4_138",
    "v4_139",
    "v4_140",
    "v4_141",
    "v4_145",
    "v4_146",
    "v4_147",
    "v4_151",
    "v4_152",
    "v4_153",
    "v4_154",
    "v4_155",
    "v4_156",
    "v4_157",
    "v4_158",
    "v4_159",
    "v4_160",
    "v4_161",
    "v4_162",
    "v4_163",
    "v4_164",
    "v4_165",
    "v4_166",
    "v4_167",
    "v4_168",
    "v4_175",
    "v4_176",
    "v4_177",
    "v4_229",
    "v4_230",
    "v4_231",
    "v4_244",
    "v4_245",
    "v4_246",
    "v4_250",
    "v4_251",
    "v4_252",
    "v4_259",
    "v4_260",
    "v4_261"
  ],
  "answer_changed_ids": [
    "v4_013",
    "v4_014",
    "v4_015",
    "v4_019",
    "v4_020",
    "v4_021",
    "v4_022",
    "v4_023",
    "v4_024",
    "v4_025",
    "v4_026",
    "v4_027",
    "v4_040",
    "v4_041",
    "v4_042",
    "v4_058",
    "v4_059",
    "v4_060",
    "v4_091",
    "v4_092",
    "v4_093",
    "v4_106",
    "v4_107",
    "v4_108",
    "v4_118",
    "v4_119",
    "v4_120",
    "v4_121",
    "v4_122",
    "v4_123",
    "v4_127",
    "v4_128",
    "v4_129",
    "v4_130",
    "v4_131",
    "v4_132",
    "v4_133",
    "v4_134",
    "v4_135",
    "v4_136",
    "v4_137",
    "v4_138",
    "v4_139",
    "v4_140",
    "v4_141",
    "v4_145",
    "v4_146",
    "v4_147",
    "v4_151",
    "v4_152",
    "v4_153",
    "v4_154",
    "v4_155",
    "v4_156",
    "v4_157",
    "v4_158",
    "v4_159",
    "v4_160",
    "v4_161",
    "v4_162",
    "v4_163",
    "v4_164",
    "v4_165",
    "v4_166",
    "v4_167",
    "v4_168",
    "v4_175",
    "v4_176",
    "v4_177",
    "v4_229",
    "v4_230",
    "v4_231",
    "v4_244",
    "v4_245",
    "v4_246",
    "v4_250",
    "v4_251",
    "v4_252",
    "v4_259",
    "v4_260",
    "v4_261"
  ],
  "reference_sql_changed_ids": [
    "v4_013",
    "v4_014",
    "v4_015",
    "v4_019",
    "v4_020",
    "v4_021",
    "v4_022",
    "v4_023",
    "v4_024",
    "v4_025",
    "v4_026",
    "v4_027",
    "v4_040",
    "v4_041",
    "v4_042",
    "v4_058",
    "v4_059",
    "v4_060",
    "v4_091",
    "v4_092",
    "v4_093",
    "v4_106",
    "v4_107",
    "v4_108",
    "v4_118",
    "v4_119",
    "v4_120",
    "v4_121",
    "v4_122",
    "v4_123",
    "v4_127",
    "v4_128",
    "v4_129",
    "v4_130",
    "v4_131",
    "v4_132",
    "v4_133",
    "v4_134",
    "v4_135",
    "v4_136",
    "v4_137",
    "v4_138",
    "v4_139",
    "v4_140",
    "v4_141",
    "v4_145",
    "v4_146",
    "v4_147",
    "v4_151",
    "v4_152",
    "v4_153",
    "v4_154",
    "v4_155",
    "v4_156",
    "v4_157",
    "v4_158",
    "v4_159",
    "v4_160",
    "v4_161",
    "v4_162",
    "v4_163",
    "v4_164",
    "v4_165",
    "v4_166",
    "v4_167",
    "v4_168",
    "v4_175",
    "v4_176",
    "v4_177",
    "v4_229",
    "v4_230",
    "v4_231",
    "v4_244",
    "v4_245",
    "v4_246",
    "v4_250",
    "v4_251",
    "v4_252",
    "v4_259",
    "v4_260",
    "v4_261"
  ],
  "parameters_changed_ids": [
    "v4_013",
    "v4_014",
    "v4_015",
    "v4_019",
    "v4_020",
    "v4_021",
    "v4_022",
    "v4_023",
    "v4_024",
    "v4_025",
    "v4_026",
    "v4_027",
    "v4_040",
    "v4_041",
    "v4_042",
    "v4_058",
    "v4_059",
    "v4_060",
    "v4_091",
    "v4_092",
    "v4_093",
    "v4_106",
    "v4_107",
    "v4_108",
    "v4_118",
    "v4_119",
    "v4_120",
    "v4_121",
    "v4_122",
    "v4_123",
    "v4_127",
    "v4_128",
    "v4_129",
    "v4_130",
    "v4_131",
    "v4_132",
    "v4_133",
    "v4_134",
    "v4_135",
    "v4_136",
    "v4_137",
    "v4_138",
    "v4_139",
    "v4_140",
    "v4_141",
    "v4_145",
    "v4_146",
    "v4_147",
    "v4_151",
    "v4_152",
    "v4_153",
    "v4_154",
    "v4_155",
    "v4_156",
    "v4_157",
    "v4_158",
    "v4_159",
    "v4_160",
    "v4_161",
    "v4_162",
    "v4_163",
    "v4_164",
    "v4_165",
    "v4_166",
    "v4_167",
    "v4_168",
    "v4_175",
    "v4_176",
    "v4_177",
    "v4_229",
    "v4_230",
    "v4_231",
    "v4_244",
    "v4_245",
    "v4_246",
    "v4_250",
    "v4_251",
    "v4_252",
    "v4_259",
    "v4_260",
    "v4_261"
  ],
  "substantive_changed_ids": [
    "v4_013",
    "v4_014",
    "v4_015",
    "v4_019",
    "v4_020",
    "v4_021",
    "v4_022",
    "v4_023",
    "v4_024",
    "v4_025",
    "v4_026",
    "v4_027",
    "v4_040",
    "v4_041",
    "v4_042",
    "v4_058",
    "v4_059",
    "v4_060",
    "v4_091",
    "v4_092",
    "v4_093",
    "v4_106",
    "v4_107",
    "v4_108",
    "v4_118",
    "v4_119",
    "v4_120",
    "v4_121",
    "v4_122",
    "v4_123",
    "v4_127",
    "v4_128",
    "v4_129",
    "v4_130",
    "v4_131",
    "v4_132",
    "v4_133",
    "v4_134",
    "v4_135",
    "v4_136",
    "v4_137",
    "v4_138",
    "v4_139",
    "v4_140",
    "v4_141",
    "v4_145",
    "v4_146",
    "v4_147",
    "v4_151",
    "v4_152",
    "v4_153",
    "v4_154",
    "v4_155",
    "v4_156",
    "v4_157",
    "v4_158",
    "v4_159",
    "v4_160",
    "v4_161",
    "v4_162",
    "v4_163",
    "v4_164",
    "v4_165",
    "v4_166",
    "v4_167",
    "v4_168",
    "v4_175",
    "v4_176",
    "v4_177",
    "v4_229",
    "v4_230",
    "v4_231",
    "v4_244",
    "v4_245",
    "v4_246",
    "v4_250",
    "v4_251",
    "v4_252",
    "v4_259",
    "v4_260",
    "v4_261"
  ],
  "metadata_only_changed_ids": [
    "v4_001",
    "v4_002",
    "v4_003",
    "v4_004",
    "v4_005",
    "v4_006",
    "v4_007",
    "v4_008",
    "v4_009",
    "v4_010",
    "v4_011",
    "v4_012",
    "v4_016",
    "v4_017",
    "v4_018",
    "v4_028",
    "v4_029",
    "v4_030",
    "v4_031",
    "v4_032",
    "v4_033",
    "v4_034",
    "v4_035",
    "v4_036",
    "v4_037",
    "v4_038",
    "v4_039",
    "v4_043",
    "v4_044",
    "v4_045",
    "v4_046",
    "v4_047",
    "v4_048",
    "v4_049",
    "v4_050",
    "v4_051",
    "v4_052",
    "v4_053",
    "v4_054",
    "v4_055",
    "v4_056",
    "v4_057",
    "v4_061",
    "v4_062",
    "v4_063",
    "v4_064",
    "v4_065",
    "v4_066",
    "v4_067",
    "v4_068",
    "v4_069",
    "v4_070",
    "v4_071",
    "v4_072",
    "v4_073",
    "v4_074",
    "v4_075",
    "v4_076",
    "v4_077",
    "v4_078",
    "v4_079",
    "v4_080",
    "v4_081",
    "v4_082",
    "v4_083",
    "v4_084",
    "v4_085",
    "v4_086",
    "v4_087",
    "v4_088",
    "v4_089",
    "v4_090",
    "v4_094",
    "v4_095",
    "v4_096",
    "v4_097",
    "v4_098",
    "v4_099",
    "v4_100",
    "v4_101",
    "v4_102",
    "v4_103",
    "v4_104",
    "v4_105",
    "v4_109",
    "v4_110",
    "v4_111",
    "v4_112",
    "v4_113",
    "v4_114",
    "v4_115",
    "v4_116",
    "v4_117",
    "v4_124",
    "v4_125",
    "v4_126",
    "v4_142",
    "v4_143",
    "v4_144",
    "v4_148",
    "v4_149",
    "v4_150",
    "v4_169",
    "v4_170",
    "v4_171",
    "v4_172",
    "v4_173",
    "v4_174",
    "v4_178",
    "v4_179",
    "v4_180",
    "v4_181",
    "v4_182",
    "v4_183",
    "v4_184",
    "v4_185",
    "v4_186",
    "v4_187",
    "v4_188",
    "v4_189",
    "v4_190",
    "v4_191",
    "v4_192",
    "v4_193",
    "v4_194",
    "v4_195",
    "v4_196",
    "v4_197",
    "v4_198",
    "v4_199",
    "v4_200",
    "v4_201",
    "v4_202",
    "v4_203",
    "v4_204",
    "v4_205",
    "v4_206",
    "v4_207",
    "v4_208",
    "v4_209",
    "v4_210",
    "v4_211",
    "v4_212",
    "v4_213",
    "v4_214",
    "v4_215",
    "v4_216",
    "v4_217",
    "v4_218",
    "v4_219",
    "v4_220",
    "v4_221",
    "v4_222",
    "v4_223",
    "v4_224",
    "v4_225",
    "v4_226",
    "v4_227",
    "v4_228",
    "v4_232",
    "v4_233",
    "v4_234",
    "v4_235",
    "v4_236",
    "v4_237",
    "v4_238",
    "v4_239",
    "v4_240",
    "v4_241",
    "v4_242",
    "v4_243",
    "v4_247",
    "v4_248",
    "v4_249",
    "v4_253",
    "v4_254",
    "v4_255",
    "v4_256",
    "v4_257",
    "v4_258",
    "v4_262",
    "v4_263",
    "v4_264",
    "v4_265",
    "v4_266",
    "v4_267",
    "v4_268",
    "v4_269",
    "v4_270",
    "v4_271",
    "v4_272",
    "v4_273",
    "v4_274",
    "v4_275",
    "v4_276",
    "v4_277",
    "v4_278",
    "v4_279",
    "v4_280",
    "v4_281",
    "v4_282",
    "v4_283",
    "v4_284",
    "v4_285",
    "v4_286",
    "v4_287",
    "v4_288",
    "v4_289",
    "v4_290",
    "v4_291",
    "v4_292",
    "v4_293",
    "v4_294",
    "v4_295",
    "v4_296",
    "v4_297",
    "v4_298",
    "v4_299",
    "v4_300"
  ],
  "original_review_ids": [
    "v4_001",
    "v4_006",
    "v4_061",
    "v4_066",
    "v4_121",
    "v4_126",
    "v4_181",
    "v4_186",
    "v4_196",
    "v4_201",
    "v4_211",
    "v4_216",
    "v4_226",
    "v4_231",
    "v4_241",
    "v4_246",
    "v4_256",
    "v4_261",
    "v4_271",
    "v4_276",
    "v4_286",
    "v4_291"
  ],
  "reviewed_replacement_ids": [
    "v4_121",
    "v4_231",
    "v4_246",
    "v4_261"
  ],
  "reviewed_metadata_only_ids": [
    "v4_001",
    "v4_006",
    "v4_061",
    "v4_066",
    "v4_126",
    "v4_181",
    "v4_186",
    "v4_196",
    "v4_201",
    "v4_211",
    "v4_216",
    "v4_226",
    "v4_241",
    "v4_256",
    "v4_271",
    "v4_276",
    "v4_286",
    "v4_291"
  ],
  "selected_ids": [
    "v4_001",
    "v4_006",
    "v4_061",
    "v4_066",
    "v4_121",
    "v4_126",
    "v4_181",
    "v4_186",
    "v4_196",
    "v4_201",
    "v4_211",
    "v4_216",
    "v4_226",
    "v4_231",
    "v4_241",
    "v4_246",
    "v4_256",
    "v4_261",
    "v4_271",
    "v4_276",
    "v4_286",
    "v4_291",
    "v4_127",
    "v4_079",
    "v4_262",
    "v4_031",
    "v4_160",
    "v4_190",
    "v4_238",
    "v4_115",
    "v4_139",
    "v4_157",
    "v4_175"
  ],
  "window_expressions": [
    "the last 7 days",
    "last week",
    "previous week",
    "October 8 through October 9, 2026",
    "October 8 through October 10, 2026",
    "October 8 through October 12, 2026",
    "October 8 through October 14, 2026",
    "October 8 through October 17, 2026",
    "October 8 through October 21, 2026",
    "October 15 through October 21, 2026",
    "October 11 through October 12, 2026",
    "October 10 through October 16, 2026",
    "October 11 through October 17, 2026"
  ]
}
```

The r2 package contains 33 questions. It retains all 22 original review IDs using their current versions, explicitly marks 4 substantive replacements, and covers every actual expression by window_expression x family stratification. This is a review package, not an approval record.

### Blind spots and scope

Battery relaxation was exercised only in isolated unit fixtures, never in the final 100 cases. Out-of-coverage perturbations remain uniformly excluded under the adjudicated rule; zero-count calendar skeletons are explicitly excluded from the claimed answer-neutrality rationale. Row-set sensitivity cannot prove correct SQL endpoints for every future answer; endpoint parsing is only a future analysis dependency. No experimental Agent, model API, accuracy evaluation, Phase B scheduler, or Git write command was run.

Files changed for this repair: gen_v4_questions.py (deterministic ladder and full battery evidence), test_v4_generation.py (tier/limit/synchronization/coverage tests), v4_questions.jsonl (300 regenerated questions), v4_regen_log.jsonl (complete successful-run candidate events), v4_overlap_audit.md (actual expression inventory), v4_sample_review_r2.md (required replacement and expression review), and this audit report (authorizations and evidence). No extra repository artifact was introduced beyond the requested r2 review.

### Final preservation verification

Compared with the fresh pre-ladder baseline, 17,064 existing files remain byte-identical. Exactly six existing files changed, all within the authorized generation/report scope; the requested r2 review is the sole new task artifact. No file is missing and all three recorded symlink targets are unchanged. The previously disclosed eval/.DS_Store metadata file remains outside task deliverables; no new nonmetadata file outside the requested scope was observed.

Frozen context.py, glossary, original glossary audit/adjudication, original 22-question review, historical question/results assets, and database are unchanged. The replay report remains byte-identical after the actual rerun.

Protected key SHA-256 values:

```json
{
  "agent/context.py": "72367ec27f81eda96a65dfa7c908f3f143bea922ed1f1d28ec7a1b2bb29a9ee4",
  "eval/glossary.md": "1a2ce44850529108249fe9970803b1745787ecf37c63136a062a11bb808c3d05",
  "eval/v4_glossary_audit.md": "1ad7371975afe60380fc38c112d2a34b9b672ec05c7c1a03099a5cc7e907d68a",
  "eval/v4_glossary_adjudication.md": "b7eb2aebfa33a5a40ba10b7e97814e49ca4e9ad48631a78775fe3ac2ec2a2248",
  "eval/v4_sample_review.md": "8668908ccfc54b2ee89673a37574e9c6a2f6f00fb409c50661c8dbdffc8c6278",
  "eval/v4_c21_replay.md": "9b9fc8b03415432e40ee2fd4169977b3c5ef24ab96f1f40b3cdde29306efc6a6"
}
```

Preserved earlier failed-run log SHA-256 values:

```json
{
  "/tmp/v4_round1_repair_before/failed_expanded_battery_regen_log.jsonl": "a7266d7a405d8c820a8e77fb0b2e79f191357f190e318699bdab4cf1f2e7ee1b",
  "/tmp/v4_round1_repair_before/failed_complete_pool_regen_log.jsonl": "f3b6d7f80c819bf1e99ecd76138c5e90e481e921f82b64dda5ea0f779e5575d4"
}
```

Final Git status (read-only inspection; tracked modifications listed here include earlier authorized Phase A work):

```text
 M agent/context.py
 M eval/check_bounds_consistency.py
 M eval/v4_bounds.py
 M tests/test_v4_bounds.py
?? eval/check_c21_replay.py
?? eval/check_v4_dedup.py
?? eval/gen_v4_questions.py
?? eval/row_normalize.py
?? eval/v4_c21_change.md
?? eval/v4_c21_replay.md
?? eval/v4_fk_audit.md
?? eval/v4_overlap_audit.md
?? eval/v4_questions.jsonl
?? eval/v4_regen_log.jsonl
?? eval/v4_sample_review.md
?? eval/v4_sample_review_r2.md
?? tests/test_v4_generation.py
```
