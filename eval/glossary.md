# Glossary

Frozen reference for metric definitions, time conventions, and dataset scope.
Written before the test question set existed; changes after the freeze commit are not allowed.

## 1. Time conventions

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

## 2. Dataset scope

- Source: GH Archive hourly public-event files, ingested into a local DuckDB database.
- Coverage: 14 full UTC days, `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- Universe: the top-100 GitHub repositories by stars, frozen in the `repos` table.
  The `events` table contains only events whose repository is in this universe.
  Not every tracked repository necessarily has events inside the window.
- This is a filtered subset of GitHub activity, not global GitHub activity.
- `ingest_log` is an internal ingestion audit table. It is not part of the analysis
  schema and must not be used to answer questions.

## 3. Metric definitions

### new_stars

For each repository and requested time window, count distinct non-null actor values on WatchEvent records. Count actor values as stored, including bots. This is not a net change in the repository's star count.

### collaboration_events

Count event records whose type is IssuesEvent, PullRequestEvent, or IssueCommentEvent within the requested time window and grouping. Count records, not distinct issues or pull requests; do not filter actors.

### active_contributors

For each repository and requested time window, count distinct non-null actor values with at least three event records in total across PushEvent, IssuesEvent, PullRequestEvent, and IssueCommentEvent. Exclude actor logins ending in the literal suffix [bot], case-insensitively. Otherwise group actor values as stored; assess the three-event threshold separately in each time window.

## 4. Tables and columns

### events

One row per public GitHub event for a tracked repository.

- `event_id` TEXT — unique event identifier from GH Archive.
- `repo_id` BIGINT — joins to `repos.repo_id`.
- `repo_name` TEXT — repository full name as stored in the event (e.g. `owner/repo`).
- `type` TEXT — GH Archive event type; see the event type list below.
- `actor` TEXT — GitHub login of the event's actor as stored; may be NULL.
  Automated accounts conventionally end in the literal suffix `[bot]`.
- `created_at` TIMESTAMP — event time, UTC.
- `payload_json` TEXT — raw event payload JSON.

### repos

One row per tracked repository; a point-in-time catalog snapshot.

- `repo_id` BIGINT — primary key.
- `name` TEXT — repository full name (`owner/repo`).
- `language` TEXT — primary language reported by GitHub; may be NULL.
- `topics` TEXT — repository topics.
- `stars`, `forks`, `open_issues` BIGINT — catalog counts as of `fetched_at`.
  They are snapshot values, not live counts, and not restricted to the event window.
- `created_at` TIMESTAMP — repository creation time, UTC; may be NULL.
- `fetched_at` TIMESTAMP — when this catalog snapshot was fetched.

## 5. Event types

The `type` column uses GH Archive event type names. Types that actually appear in
this dataset are listed in `event_types.txt` next to this file (generated from the
database at freeze time). Common meanings:

- `PushEvent` — one or more commits pushed to a branch.
- `WatchEvent` — a user starred the repository.
- `IssuesEvent` — an issue was opened, closed, reopened, labeled, etc.
- `IssueCommentEvent` — a comment on an issue or pull request.
- `PullRequestEvent` — a pull request was opened, closed, merged, etc.
- `PullRequestReviewEvent` — a pull request review was submitted.
- `PullRequestReviewCommentEvent` — a comment on a pull request review.
- `CreateEvent` — a branch or tag was created.
- `DeleteEvent` — a branch or tag was deleted.
- `ForkEvent` — the repository was forked.
- `ReleaseEvent` — a release was published.
- `CommitCommentEvent` — a comment on a commit.
- `GollumEvent` — a wiki page was created or updated.
- `PublicEvent` — a private repository was made public.
- `MemberEvent` — a collaborator was added or removed.
- `SponsorshipEvent` — a sponsorship listing event.

## 6. Conventions and caveats

- Actor values are counted as stored (case-sensitive) unless a metric definition says
  otherwise. Bot accounts are included unless a definition excludes them.
- "Repository" without qualification means a row in `repos`; join via `repo_id`.
- Star-related catalog fields (`stars`) describe the snapshot at `fetched_at`; the
  metric `new_stars` describes event activity inside a window. They answer different
  questions and must not be mixed.
- Questions asking to "include zero-count repositories" imply an outer join from
  `repos` to aggregated events.
