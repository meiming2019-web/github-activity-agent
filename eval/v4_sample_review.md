# v4 Manual Sample Review

Two questions per family, 22 questions total. Each pair uses different semantic cases; no reviewer decisions have been filled in.

## v4_001 — window_new_stars / literal

For the last 7 days, report new_stars for repository 'firecrawl/firecrawl' as value. Count distinct non-null WatchEvent actors, including bots; apply the definition separately per repository within the window.

```sql
SELECT COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'firecrawl/firecrawl'
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['value']`; reference row count: 1.

Glossary original:
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

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Sensitivity evidence (both boundaries shifted; grader multiset comparison):
```json
[
  {
    "shift_days": -1,
    "changed": true,
    "reference_sql": "SELECT COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'firecrawl/firecrawl'",
    "row_count": 1,
    "rows_sha256": "521488a321ba20132908087a5cfa920bd098afadef61d84ea0de2f7e8783f021"
  },
  {
    "shift_days": 1,
    "changed": true,
    "reference_sql": "SELECT COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-23' AND e.repo_name = 'firecrawl/firecrawl'",
    "row_count": 1,
    "rows_sha256": "51cc38ae7f7ec48474a2911c196358ba237244d842eee4f6032d6ad53816d731"
  }
]
```

Distractor injection probe:
```json
null
```

## v4_006 — window_new_stars / distractor

For the last 7 days, rank up to five 'Shell' repositories with positive new_stars; return repo_name and value. Order by value descending; break ties by repo_name ascending. Count distinct non-null WatchEvent actors, including bots; apply the definition separately per repository within the window. A repository creation year of 2017 is background only and must not filter the answer.

```sql
WITH metric AS (SELECT e.repo_name, COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND r.language = 'Shell' GROUP BY e.repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['repo_name', 'value']`; reference row count: 4.

Glossary original:
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

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Sensitivity evidence (both boundaries shifted; grader multiset comparison):
```json
[
  {
    "shift_days": -1,
    "changed": true,
    "reference_sql": "WITH metric AS (SELECT e.repo_name, COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND r.language = 'Shell' GROUP BY e.repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5",
    "row_count": 4,
    "rows_sha256": "ff8800a4e2ed7ed4d73a71c05c0d89bb8c4bb570948ae19b0712573344664b5e"
  },
  {
    "shift_days": 1,
    "changed": true,
    "reference_sql": "WITH metric AS (SELECT e.repo_name, COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-23' AND r.language = 'Shell' GROUP BY e.repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5",
    "row_count": 4,
    "rows_sha256": "e8917ede30cf66cda74dddc8ad945e7e382403b020806e47725faf0acee62ace"
  }
]
```

Distractor injection probe:
```json
{
  "triggered": true,
  "appended_line": "Question window: [2026-10-15, 2026-10-22)",
  "selection_policy": "leftmost canonical window; decorative standalone years ignored",
  "used_for_filtering": false
}
```

## v4_061 — window_collaboration_events / literal

For the last 7 days, report collaboration_events for repository 'morluto/rea' as value. Count IssuesEvent, PullRequestEvent, and IssueCommentEvent records; apply the definition separately per repository within the window.

```sql
SELECT COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'morluto/rea'
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['value']`; reference row count: 1.

Glossary original:
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

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Sensitivity evidence (both boundaries shifted; grader multiset comparison):
```json
[
  {
    "shift_days": -1,
    "changed": true,
    "reference_sql": "SELECT COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'morluto/rea'",
    "row_count": 1,
    "rows_sha256": "2fa2c8b080d5e916c4e0c20371f1e90d2014afaea0c54e64e7fb6974c4a056db"
  },
  {
    "shift_days": 1,
    "changed": true,
    "reference_sql": "SELECT COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-23' AND e.repo_name = 'morluto/rea'",
    "row_count": 1,
    "rows_sha256": "50f2233e4a2a3194806c957007177802d49be1f4c6df0d2b7751ed635025d6e3"
  }
]
```

Distractor injection probe:
```json
null
```

## v4_066 — window_collaboration_events / distractor

For the last 7 days, rank up to five 'Python' repositories with positive collaboration_events; return repo_name and value. Order by value descending; break ties by repo_name ascending. Count IssuesEvent, PullRequestEvent, and IssueCommentEvent records; apply the definition separately per repository within the window. A repository creation year of 2017 is background only and must not filter the answer.

```sql
WITH metric AS (SELECT e.repo_name, COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND r.language = 'Python' GROUP BY e.repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['repo_name', 'value']`; reference row count: 5.

Glossary original:
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

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Sensitivity evidence (both boundaries shifted; grader multiset comparison):
```json
[
  {
    "shift_days": -1,
    "changed": true,
    "reference_sql": "WITH metric AS (SELECT e.repo_name, COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND r.language = 'Python' GROUP BY e.repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5",
    "row_count": 5,
    "rows_sha256": "a9632a0e3460a6108f07f52f6175893c6875e018c3467a12a6b95f2c40168096"
  },
  {
    "shift_days": 1,
    "changed": true,
    "reference_sql": "WITH metric AS (SELECT e.repo_name, COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-23' AND r.language = 'Python' GROUP BY e.repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5",
    "row_count": 5,
    "rows_sha256": "d62db7c4f8c41f5d9afcf05471e7ab7964c822d35265f2daf28f6ec2e685f5f1"
  }
]
```

Distractor injection probe:
```json
{
  "triggered": true,
  "appended_line": "Question window: [2026-10-15, 2026-10-22)",
  "selection_policy": "leftmost canonical window; decorative standalone years ignored",
  "used_for_filtering": false
}
```

## v4_121 — window_active_contributors / literal

For the last 7 days, report active_contributors for repository 'morluto/rea' as value. Count non-null actors with at least three PushEvent, IssuesEvent, PullRequestEvent, or IssueCommentEvent records, excluding case-insensitive [bot] suffixes; apply the definition separately per repository within the window.

```sql
WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'morluto/rea' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['value']`; reference row count: 1.

Glossary original:
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

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Sensitivity evidence (both boundaries shifted; grader multiset comparison):
```json
[
  {
    "shift_days": -1,
    "changed": true,
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'morluto/rea' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows_sha256": "cdeb7c05a0964529754c21cc14bac320ed1d761e3db3f47050a402bd8a32b883"
  },
  {
    "shift_days": 1,
    "changed": true,
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-23' AND e.repo_name = 'morluto/rea' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows_sha256": "a9aa85acf18adf4f2e42f1cb876a854cf82b70587922457d888db0e2df100099"
  }
]
```

Distractor injection probe:
```json
null
```

## v4_126 — window_active_contributors / distractor

For the last 7 days, rank up to five 'Rust' repositories with positive active_contributors; return repo_name and value. Order by value descending; break ties by repo_name ascending. Count non-null actors with at least three PushEvent, IssuesEvent, PullRequestEvent, or IssueCommentEvent records, excluding case-insensitive [bot] suffixes; apply the definition separately per repository within the window. A repository creation year of 2017 is background only and must not filter the answer.

```sql
WITH metric AS (WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND r.language = 'Rust' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT repo_name, COUNT(*) AS value FROM qualified GROUP BY repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['repo_name', 'value']`; reference row count: 4.

Glossary original:
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

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Sensitivity evidence (both boundaries shifted; grader multiset comparison):
```json
[
  {
    "shift_days": -1,
    "changed": true,
    "reference_sql": "WITH metric AS (WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND r.language = 'Rust' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT repo_name, COUNT(*) AS value FROM qualified GROUP BY repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5",
    "row_count": 3,
    "rows_sha256": "f1c1bec8669168cc3b875426672876e873e0b740e72e6cfdd377eeaf7e2a7fcf"
  },
  {
    "shift_days": 1,
    "changed": true,
    "reference_sql": "WITH metric AS (WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-23' AND r.language = 'Rust' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT repo_name, COUNT(*) AS value FROM qualified GROUP BY repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5",
    "row_count": 4,
    "rows_sha256": "32ca90f340f7a11cee4e20ebf257f6084ad1651f4726e3381ec9f654a7be0852"
  }
]
```

Distractor injection probe:
```json
{
  "triggered": true,
  "appended_line": "Question window: [2026-10-15, 2026-10-22)",
  "selection_policy": "leftmost canonical window; decorative standalone years ignored",
  "used_for_filtering": false
}
```

## v4_181 — daily_trend / literal

For the last 7 days, using WatchEvent records for 'Hack-with-Github/Awesome-Hacking', return each UTC date as day and its event_count, including zero-count dates, ordered by day ascending.

```sql
WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-15', TIMESTAMP '2026-10-21', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'Hack-with-Github/Awesome-Hacking' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count FROM daily ORDER BY day ASC
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['day', 'event_count']`; reference row count: 7.

Glossary original:
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

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Sensitivity evidence (both boundaries shifted; grader multiset comparison):
```json
[
  {
    "shift_days": -1,
    "changed": true,
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-14', TIMESTAMP '2026-10-20', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'Hack-with-Github/Awesome-Hacking' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count FROM daily ORDER BY day ASC",
    "row_count": 7,
    "rows_sha256": "693c2a3f0ef5a4625d38c1d00c663e1adeda773405ad275c6fb5bbf42f6a0dd6"
  },
  {
    "shift_days": 1,
    "changed": true,
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-16', TIMESTAMP '2026-10-22', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-23' AND e.repo_name = 'Hack-with-Github/Awesome-Hacking' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count FROM daily ORDER BY day ASC",
    "row_count": 7,
    "rows_sha256": "9840ef0f0cfe076772853c07a1919909e17dc7b514ff873024d1d710eb82eed4"
  }
]
```

Distractor injection probe:
```json
null
```

## v4_186 — daily_trend / distractor

For previous week, using PushEvent records for 'mattpocock/skills', return each UTC date as day and its event_count, including zero-count dates, ordered by day ascending. A repository creation year of 2017 is background only and must not filter the answer.

```sql
WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-08', TIMESTAMP '2026-10-14', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-15' AND e.repo_name = 'mattpocock/skills' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count FROM daily ORDER BY day ASC
```

Code-computed boundaries: `['2026-10-08', '2026-10-15']`.
Reference columns: `['day', 'event_count']`; reference row count: 7.

Glossary original:
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

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Sensitivity evidence (both boundaries shifted; grader multiset comparison):
```json
[
  {
    "shift_days": -1,
    "changed": true,
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-07', TIMESTAMP '2026-10-13', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-07' AND e.created_at < TIMESTAMP '2026-10-14' AND e.repo_name = 'mattpocock/skills' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count FROM daily ORDER BY day ASC",
    "row_count": 7,
    "rows_sha256": "b67794e5c7598beed63f9557c7197a34bfd6d9e4492738a7a1d947d2357c55df"
  },
  {
    "shift_days": 1,
    "changed": true,
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-09', TIMESTAMP '2026-10-15', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-16' AND e.repo_name = 'mattpocock/skills' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count FROM daily ORDER BY day ASC",
    "row_count": 7,
    "rows_sha256": "35f2b66ec891b80b235bb89827739e7b0f1dd5580f257c6d398db634ab8331b2"
  }
]
```

Distractor injection probe:
```json
{
  "triggered": true,
  "appended_line": "Question window: [2026-10-08, 2026-10-15)",
  "selection_policy": "leftmost canonical window; decorative standalone years ignored",
  "used_for_filtering": false
}
```

## v4_196 — running_total / literal

For the last 7 days, using WatchEvent records for 'ollama/ollama', return each UTC date as day, event_count, and running_count accumulated from the window start, including zero-count dates, ordered by day ascending.

```sql
WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-15', TIMESTAMP '2026-10-21', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'ollama/ollama' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count, SUM(event_count) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_count FROM daily ORDER BY day ASC
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['day', 'event_count', 'running_count']`; reference row count: 7.

Glossary original:
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

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Sensitivity evidence (both boundaries shifted; grader multiset comparison):
```json
[
  {
    "shift_days": -1,
    "changed": true,
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-14', TIMESTAMP '2026-10-20', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'ollama/ollama' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count, SUM(event_count) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_count FROM daily ORDER BY day ASC",
    "row_count": 7,
    "rows_sha256": "24063135447c7f29673ce649b53f33e7d36d7c1cf5af2596a0bf1df42a1c18ac"
  },
  {
    "shift_days": 1,
    "changed": true,
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-16', TIMESTAMP '2026-10-22', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-23' AND e.repo_name = 'ollama/ollama' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count, SUM(event_count) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_count FROM daily ORDER BY day ASC",
    "row_count": 7,
    "rows_sha256": "54f1ae68a27eb4efefadfb91895871af90613eaf13a361ec8be8db0165fe6248"
  }
]
```

Distractor injection probe:
```json
null
```

## v4_201 — running_total / distractor

For previous week, using PushEvent records for 'ollama/ollama', return each UTC date as day, event_count, and running_count accumulated from the window start, including zero-count dates, ordered by day ascending. A repository creation year of 2017 is background only and must not filter the answer.

```sql
WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-08', TIMESTAMP '2026-10-14', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-15' AND e.repo_name = 'ollama/ollama' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count, SUM(event_count) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_count FROM daily ORDER BY day ASC
```

Code-computed boundaries: `['2026-10-08', '2026-10-15']`.
Reference columns: `['day', 'event_count', 'running_count']`; reference row count: 7.

Glossary original:
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

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Sensitivity evidence (both boundaries shifted; grader multiset comparison):
```json
[
  {
    "shift_days": -1,
    "changed": true,
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-07', TIMESTAMP '2026-10-13', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-07' AND e.created_at < TIMESTAMP '2026-10-14' AND e.repo_name = 'ollama/ollama' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count, SUM(event_count) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_count FROM daily ORDER BY day ASC",
    "row_count": 7,
    "rows_sha256": "139615348dbed0f0f1cddbde844ed5f05dacb485a0f3c985538fdcd385c4a892"
  },
  {
    "shift_days": 1,
    "changed": true,
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-09', TIMESTAMP '2026-10-15', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-16' AND e.repo_name = 'ollama/ollama' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count, SUM(event_count) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_count FROM daily ORDER BY day ASC",
    "row_count": 7,
    "rows_sha256": "12ab226d74853ef34934559f8decb649f3c34799fee34b681cc84539b686148d"
  }
]
```

Distractor injection probe:
```json
{
  "triggered": true,
  "appended_line": "Question window: [2026-10-08, 2026-10-15)",
  "selection_policy": "leftmost canonical window; decorative standalone years ignored",
  "used_for_filtering": false
}
```

## v4_211 — day_over_day / literal

For the last 7 days, using WatchEvent records for 'AUTOMATIC1111/stable-diffusion-webui', return each UTC date as day, event_count, previous_count, and change (current minus previous); include zero-count dates and use NULL for previous_count and change on the first date; order by day ascending.

```sql
WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-15', TIMESTAMP '2026-10-21', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'AUTOMATIC1111/stable-diffusion-webui' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) , compared AS (SELECT day, event_count, LAG(event_count) OVER (ORDER BY day) AS previous_count FROM daily) SELECT day, event_count, previous_count, event_count - previous_count AS change FROM compared ORDER BY day ASC
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['day', 'event_count', 'previous_count', 'change']`; reference row count: 7.

Glossary original:
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

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Sensitivity evidence (both boundaries shifted; grader multiset comparison):
```json
[
  {
    "shift_days": -1,
    "changed": true,
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-14', TIMESTAMP '2026-10-20', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'AUTOMATIC1111/stable-diffusion-webui' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) , compared AS (SELECT day, event_count, LAG(event_count) OVER (ORDER BY day) AS previous_count FROM daily) SELECT day, event_count, previous_count, event_count - previous_count AS change FROM compared ORDER BY day ASC",
    "row_count": 7,
    "rows_sha256": "967d503a6dbebf91129069aa6d0e2af07b85fac68911b055cd2ffd9695ea5c7f"
  },
  {
    "shift_days": 1,
    "changed": true,
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-16', TIMESTAMP '2026-10-22', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-23' AND e.repo_name = 'AUTOMATIC1111/stable-diffusion-webui' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) , compared AS (SELECT day, event_count, LAG(event_count) OVER (ORDER BY day) AS previous_count FROM daily) SELECT day, event_count, previous_count, event_count - previous_count AS change FROM compared ORDER BY day ASC",
    "row_count": 7,
    "rows_sha256": "2e3f4eb036645b0d24c939f9b43e9d8371bf4600dc9d40dd37c37ea9bbb2a279"
  }
]
```

Distractor injection probe:
```json
null
```

## v4_216 — day_over_day / distractor

For previous week, using PushEvent records for 'langgenius/dify', return each UTC date as day, event_count, previous_count, and change (current minus previous); include zero-count dates and use NULL for previous_count and change on the first date; order by day ascending. A repository creation year of 2017 is background only and must not filter the answer.

```sql
WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-08', TIMESTAMP '2026-10-14', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-15' AND e.repo_name = 'langgenius/dify' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) , compared AS (SELECT day, event_count, LAG(event_count) OVER (ORDER BY day) AS previous_count FROM daily) SELECT day, event_count, previous_count, event_count - previous_count AS change FROM compared ORDER BY day ASC
```

Code-computed boundaries: `['2026-10-08', '2026-10-15']`.
Reference columns: `['day', 'event_count', 'previous_count', 'change']`; reference row count: 7.

Glossary original:
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

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Sensitivity evidence (both boundaries shifted; grader multiset comparison):
```json
[
  {
    "shift_days": -1,
    "changed": true,
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-07', TIMESTAMP '2026-10-13', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-07' AND e.created_at < TIMESTAMP '2026-10-14' AND e.repo_name = 'langgenius/dify' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) , compared AS (SELECT day, event_count, LAG(event_count) OVER (ORDER BY day) AS previous_count FROM daily) SELECT day, event_count, previous_count, event_count - previous_count AS change FROM compared ORDER BY day ASC",
    "row_count": 7,
    "rows_sha256": "e61f78fb763a55351103ad1ab673766082eb84e433af30f1311d6960fcda8802"
  },
  {
    "shift_days": 1,
    "changed": true,
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-09', TIMESTAMP '2026-10-15', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-16' AND e.repo_name = 'langgenius/dify' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) , compared AS (SELECT day, event_count, LAG(event_count) OVER (ORDER BY day) AS previous_count FROM daily) SELECT day, event_count, previous_count, event_count - previous_count AS change FROM compared ORDER BY day ASC",
    "row_count": 7,
    "rows_sha256": "67c19dec3d5635d24aded5a5329a98958eca523968a2bff9651df482f5e910ec"
  }
]
```

Distractor injection probe:
```json
{
  "triggered": true,
  "appended_line": "Question window: [2026-10-08, 2026-10-15)",
  "selection_policy": "leftmost canonical window; decorative standalone years ignored",
  "used_for_filtering": false
}
```

## v4_226 — day_of_week / literal

For the last 7 days, using WatchEvent records for 'yangshun/tech-interview-handbook', sum daily counts by weekday (Sunday=0 and Saturday=6) for dates present in the window; return weekday and event_count, including zero-count groups, ordered by weekday ascending.

```sql
WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-15', TIMESTAMP '2026-10-21', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'yangshun/tech-interview-handbook' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT EXTRACT(DOW FROM day) AS weekday, SUM(event_count) AS event_count FROM daily GROUP BY 1 ORDER BY weekday ASC
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['weekday', 'event_count']`; reference row count: 7.

Glossary original:
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

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Sensitivity evidence (both boundaries shifted; grader multiset comparison):
```json
[
  {
    "shift_days": -1,
    "changed": true,
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-14', TIMESTAMP '2026-10-20', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'yangshun/tech-interview-handbook' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT EXTRACT(DOW FROM day) AS weekday, SUM(event_count) AS event_count FROM daily GROUP BY 1 ORDER BY weekday ASC",
    "row_count": 7,
    "rows_sha256": "9771c015150cb198ad1aec35ec2ed8643332784deee5a3586c0b2e9545d60753"
  },
  {
    "shift_days": 1,
    "changed": true,
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-16', TIMESTAMP '2026-10-22', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-23' AND e.repo_name = 'yangshun/tech-interview-handbook' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT EXTRACT(DOW FROM day) AS weekday, SUM(event_count) AS event_count FROM daily GROUP BY 1 ORDER BY weekday ASC",
    "row_count": 7,
    "rows_sha256": "5738db0a800e36e442b9538413bf3cdacf16c76abdd21915a4813283216185af"
  }
]
```

Distractor injection probe:
```json
null
```

## v4_231 — day_of_week / distractor

For previous week, using PushEvent records for 'Comfy-Org/ComfyUI', sum daily counts by weekday (Sunday=0 and Saturday=6) for dates present in the window; return weekday and event_count, including zero-count groups, ordered by weekday ascending. A repository creation year of 2017 is background only and must not filter the answer.

```sql
WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-08', TIMESTAMP '2026-10-14', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-15' AND e.repo_name = 'Comfy-Org/ComfyUI' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT EXTRACT(DOW FROM day) AS weekday, SUM(event_count) AS event_count FROM daily GROUP BY 1 ORDER BY weekday ASC
```

Code-computed boundaries: `['2026-10-08', '2026-10-15']`.
Reference columns: `['weekday', 'event_count']`; reference row count: 7.

Glossary original:
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

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Sensitivity evidence (both boundaries shifted; grader multiset comparison):
```json
[
  {
    "shift_days": -1,
    "changed": true,
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-07', TIMESTAMP '2026-10-13', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-07' AND e.created_at < TIMESTAMP '2026-10-14' AND e.repo_name = 'Comfy-Org/ComfyUI' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT EXTRACT(DOW FROM day) AS weekday, SUM(event_count) AS event_count FROM daily GROUP BY 1 ORDER BY weekday ASC",
    "row_count": 7,
    "rows_sha256": "f748d9ac6924001be22bcf2914f7eda683261968551e94b1e148be3be6ce8fa6"
  },
  {
    "shift_days": 1,
    "changed": true,
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-09', TIMESTAMP '2026-10-15', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-16' AND e.repo_name = 'Comfy-Org/ComfyUI' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT EXTRACT(DOW FROM day) AS weekday, SUM(event_count) AS event_count FROM daily GROUP BY 1 ORDER BY weekday ASC",
    "row_count": 7,
    "rows_sha256": "877e9005062e412de0f2861486fce875db0bee09fe68b61920084ab2cdbe1ba4"
  }
]
```

Distractor injection probe:
```json
{
  "triggered": true,
  "appended_line": "Question window: [2026-10-08, 2026-10-15)",
  "selection_policy": "leftmost canonical window; decorative standalone years ignored",
  "used_for_filtering": false
}
```

## v4_241 — session_segmentation / literal

For the last 7 days, using WatchEvent records for 'trimstray/the-book-of-secret-knowledge', return session_count after ordering these records by created_at and event_id ascending; the first record starts a session, and a gap strictly greater than 30 minutes starts another session.

```sql
WITH ordered AS (SELECT e.created_at, LAG(e.created_at) OVER (ORDER BY e.created_at, e.event_id) AS previous_at FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'trimstray/the-book-of-secret-knowledge' AND e.type = 'WatchEvent') SELECT SUM(CASE WHEN previous_at IS NULL OR created_at - previous_at > INTERVAL '30 minutes' THEN 1 ELSE 0 END) AS session_count FROM ordered
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['session_count']`; reference row count: 1.

Glossary original:
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

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Sensitivity evidence (both boundaries shifted; grader multiset comparison):
```json
[
  {
    "shift_days": -1,
    "changed": true,
    "reference_sql": "WITH ordered AS (SELECT e.created_at, LAG(e.created_at) OVER (ORDER BY e.created_at, e.event_id) AS previous_at FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'trimstray/the-book-of-secret-knowledge' AND e.type = 'WatchEvent') SELECT SUM(CASE WHEN previous_at IS NULL OR created_at - previous_at > INTERVAL '30 minutes' THEN 1 ELSE 0 END) AS session_count FROM ordered",
    "row_count": 1,
    "rows_sha256": "1220e80a7a8fb1bcece94f15115f1d7a81ee034c624c43a2168434f6b4265cef"
  },
  {
    "shift_days": 1,
    "changed": true,
    "reference_sql": "WITH ordered AS (SELECT e.created_at, LAG(e.created_at) OVER (ORDER BY e.created_at, e.event_id) AS previous_at FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-23' AND e.repo_name = 'trimstray/the-book-of-secret-knowledge' AND e.type = 'WatchEvent') SELECT SUM(CASE WHEN previous_at IS NULL OR created_at - previous_at > INTERVAL '30 minutes' THEN 1 ELSE 0 END) AS session_count FROM ordered",
    "row_count": 1,
    "rows_sha256": "5bd2881bfa6bb6e4feb436faf966e3a18c1155a0b2d479a60cdb80a8233f833d"
  }
]
```

Distractor injection probe:
```json
null
```

## v4_246 — session_segmentation / distractor

For previous week, using PushEvent records for 'rustdesk/rustdesk', return session_count after ordering these records by created_at and event_id ascending; the first record starts a session, and a gap strictly greater than 30 minutes starts another session. A repository creation year of 2017 is background only and must not filter the answer.

```sql
WITH ordered AS (SELECT e.created_at, LAG(e.created_at) OVER (ORDER BY e.created_at, e.event_id) AS previous_at FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-15' AND e.repo_name = 'rustdesk/rustdesk' AND e.type = 'PushEvent') SELECT SUM(CASE WHEN previous_at IS NULL OR created_at - previous_at > INTERVAL '30 minutes' THEN 1 ELSE 0 END) AS session_count FROM ordered
```

Code-computed boundaries: `['2026-10-08', '2026-10-15']`.
Reference columns: `['session_count']`; reference row count: 1.

Glossary original:
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

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Sensitivity evidence (both boundaries shifted; grader multiset comparison):
```json
[
  {
    "shift_days": -1,
    "changed": true,
    "reference_sql": "WITH ordered AS (SELECT e.created_at, LAG(e.created_at) OVER (ORDER BY e.created_at, e.event_id) AS previous_at FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-07' AND e.created_at < TIMESTAMP '2026-10-14' AND e.repo_name = 'rustdesk/rustdesk' AND e.type = 'PushEvent') SELECT SUM(CASE WHEN previous_at IS NULL OR created_at - previous_at > INTERVAL '30 minutes' THEN 1 ELSE 0 END) AS session_count FROM ordered",
    "row_count": 1,
    "rows_sha256": "77471ebe3613f4714666523fa961eb443f57dc2396a31528afdbbea86fadc8f8"
  },
  {
    "shift_days": 1,
    "changed": true,
    "reference_sql": "WITH ordered AS (SELECT e.created_at, LAG(e.created_at) OVER (ORDER BY e.created_at, e.event_id) AS previous_at FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-16' AND e.repo_name = 'rustdesk/rustdesk' AND e.type = 'PushEvent') SELECT SUM(CASE WHEN previous_at IS NULL OR created_at - previous_at > INTERVAL '30 minutes' THEN 1 ELSE 0 END) AS session_count FROM ordered",
    "row_count": 1,
    "rows_sha256": "77471ebe3613f4714666523fa961eb443f57dc2396a31528afdbbea86fadc8f8"
  }
]
```

Distractor injection probe:
```json
{
  "triggered": true,
  "appended_line": "Question window: [2026-10-08, 2026-10-15)",
  "selection_policy": "leftmost canonical window; decorative standalone years ignored",
  "used_for_filtering": false
}
```

## v4_256 — consecutive_day_runs / literal

For the last 7 days, using WatchEvent records for 'vinta/awesome-python', return every maximal run of consecutive active UTC dates as first_date, last_date, and active_days; a date is active if it contains at least one matching record; order by first_date ascending.

```sql
WITH active_days AS (SELECT DISTINCT CAST(e.created_at AS DATE) AS day FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'vinta/awesome-python' AND e.type = 'WatchEvent'), numbered AS (SELECT day, day - CAST(ROW_NUMBER() OVER (ORDER BY day) AS INTEGER) AS island FROM active_days) SELECT MIN(day) AS first_date, MAX(day) AS last_date, COUNT(*) AS active_days FROM numbered GROUP BY island ORDER BY first_date ASC
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['first_date', 'last_date', 'active_days']`; reference row count: 2.

Glossary original:
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

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Sensitivity evidence (both boundaries shifted; grader multiset comparison):
```json
[
  {
    "shift_days": -1,
    "changed": true,
    "reference_sql": "WITH active_days AS (SELECT DISTINCT CAST(e.created_at AS DATE) AS day FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'vinta/awesome-python' AND e.type = 'WatchEvent'), numbered AS (SELECT day, day - CAST(ROW_NUMBER() OVER (ORDER BY day) AS INTEGER) AS island FROM active_days) SELECT MIN(day) AS first_date, MAX(day) AS last_date, COUNT(*) AS active_days FROM numbered GROUP BY island ORDER BY first_date ASC",
    "row_count": 1,
    "rows_sha256": "b22dbd46bfffaf7d94a0838e3a8399bf1dc52076c1172cc16bcceba07eec8067"
  },
  {
    "shift_days": 1,
    "changed": true,
    "reference_sql": "WITH active_days AS (SELECT DISTINCT CAST(e.created_at AS DATE) AS day FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-23' AND e.repo_name = 'vinta/awesome-python' AND e.type = 'WatchEvent'), numbered AS (SELECT day, day - CAST(ROW_NUMBER() OVER (ORDER BY day) AS INTEGER) AS island FROM active_days) SELECT MIN(day) AS first_date, MAX(day) AS last_date, COUNT(*) AS active_days FROM numbered GROUP BY island ORDER BY first_date ASC",
    "row_count": 2,
    "rows_sha256": "1ec5449ef3b54b8b3ec99c7871ac6f2e73cc53afef995627adfc4d194265c90c"
  }
]
```

Distractor injection probe:
```json
null
```

## v4_261 — consecutive_day_runs / distractor

For previous week, using PushEvent records for 'electron/electron', return every maximal run of consecutive active UTC dates as first_date, last_date, and active_days; a date is active if it contains at least one matching record; order by first_date ascending. A repository creation year of 2017 is background only and must not filter the answer.

```sql
WITH active_days AS (SELECT DISTINCT CAST(e.created_at AS DATE) AS day FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-15' AND e.repo_name = 'electron/electron' AND e.type = 'PushEvent'), numbered AS (SELECT day, day - CAST(ROW_NUMBER() OVER (ORDER BY day) AS INTEGER) AS island FROM active_days) SELECT MIN(day) AS first_date, MAX(day) AS last_date, COUNT(*) AS active_days FROM numbered GROUP BY island ORDER BY first_date ASC
```

Code-computed boundaries: `['2026-10-08', '2026-10-15']`.
Reference columns: `['first_date', 'last_date', 'active_days']`; reference row count: 2.

Glossary original:
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

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Sensitivity evidence (both boundaries shifted; grader multiset comparison):
```json
[
  {
    "shift_days": -1,
    "changed": true,
    "reference_sql": "WITH active_days AS (SELECT DISTINCT CAST(e.created_at AS DATE) AS day FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-07' AND e.created_at < TIMESTAMP '2026-10-14' AND e.repo_name = 'electron/electron' AND e.type = 'PushEvent'), numbered AS (SELECT day, day - CAST(ROW_NUMBER() OVER (ORDER BY day) AS INTEGER) AS island FROM active_days) SELECT MIN(day) AS first_date, MAX(day) AS last_date, COUNT(*) AS active_days FROM numbered GROUP BY island ORDER BY first_date ASC",
    "row_count": 2,
    "rows_sha256": "96501217ccdac352c1577a5043be18072243b1ca868de6fc950034dcfbf2eec1"
  },
  {
    "shift_days": 1,
    "changed": true,
    "reference_sql": "WITH active_days AS (SELECT DISTINCT CAST(e.created_at AS DATE) AS day FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-16' AND e.repo_name = 'electron/electron' AND e.type = 'PushEvent'), numbered AS (SELECT day, day - CAST(ROW_NUMBER() OVER (ORDER BY day) AS INTEGER) AS island FROM active_days) SELECT MIN(day) AS first_date, MAX(day) AS last_date, COUNT(*) AS active_days FROM numbered GROUP BY island ORDER BY first_date ASC",
    "row_count": 2,
    "rows_sha256": "12cba412483fd4060df27f3939a080ba1b382cf0433c6d902cde1575b6543703"
  }
]
```

Distractor injection probe:
```json
{
  "triggered": true,
  "appended_line": "Question window: [2026-10-08, 2026-10-15)",
  "selection_policy": "leftmost canonical window; decorative standalone years ignored",
  "used_for_filtering": false
}
```

## v4_271 — catalog_lookup / literal

Read the catalog entry for 'github/spec-kit': return repo_name, stars, forks, and open_issues.

```sql
SELECT name AS repo_name, stars, forks, open_issues FROM repos WHERE name = 'github/spec-kit'
```

Code-computed boundaries: `None`.
Reference columns: `['repo_name', 'stars', 'forks', 'open_issues']`; reference row count: 1.

Glossary original:
```text
No effective time semantics; no time-boundary glossary entry applies.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Sensitivity evidence (both boundaries shifted; grader multiset comparison):
```json
[]
```

Distractor injection probe:
```json
null
```

## v4_276 — catalog_lookup / distractor

Read the catalog entry for 'github/gitignore': return repo_name, stars, forks, and open_issues. A repository creation year of 2017 is background only and must not filter the answer.

```sql
SELECT name AS repo_name, stars, forks, open_issues FROM repos WHERE name = 'github/gitignore'
```

Code-computed boundaries: `None`.
Reference columns: `['repo_name', 'stars', 'forks', 'open_issues']`; reference row count: 1.

Glossary original:
```text
No effective time semantics; no time-boundary glossary entry applies.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Sensitivity evidence (both boundaries shifted; grader multiset comparison):
```json
[]
```

Distractor injection probe:
```json
{
  "triggered": false,
  "appended_line": null,
  "selection_policy": "leftmost canonical window; decorative standalone years ignored",
  "used_for_filtering": false
}
```

## v4_286 — language_composition / literal

For catalog language 'Batchfile', return repo_count and total_stars summed across its repositories.

```sql
SELECT COUNT(*) AS repo_count, SUM(stars) AS total_stars FROM repos WHERE language = 'Batchfile'
```

Code-computed boundaries: `None`.
Reference columns: `['repo_count', 'total_stars']`; reference row count: 1.

Glossary original:
```text
No effective time semantics; no time-boundary glossary entry applies.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Sensitivity evidence (both boundaries shifted; grader multiset comparison):
```json
[]
```

Distractor injection probe:
```json
null
```

## v4_291 — language_composition / distractor

For catalog language 'MDX', return repo_count and total_stars summed across its repositories. A repository creation year of 2017 is background only and must not filter the answer.

```sql
SELECT COUNT(*) AS repo_count, SUM(stars) AS total_stars FROM repos WHERE language = 'MDX'
```

Code-computed boundaries: `None`.
Reference columns: `['repo_count', 'total_stars']`; reference row count: 1.

Glossary original:
```text
No effective time semantics; no time-boundary glossary entry applies.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Sensitivity evidence (both boundaries shifted; grader multiset comparison):
```json
[]
```

Distractor injection probe:
```json
{
  "triggered": false,
  "appended_line": null,
  "selection_policy": "leftmost canonical window; decorative standalone years ignored",
  "used_for_filtering": false
}
```
