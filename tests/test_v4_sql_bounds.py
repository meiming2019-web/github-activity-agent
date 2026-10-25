"""Independent synthetic AST cases; no model, database, or reference grading."""

import ast
from pathlib import Path

import pytest

from eval.v4_sql_bounds import analyze_sql

BOUNDS = ['2026-10-08', '2026-10-15']
WINDOW = "created_at >= TIMESTAMP '2026-10-08' AND created_at < TIMESTAMP '2026-10-15'"


@pytest.mark.parametrize('predicate,expected', [
    (WINDOW, 'correct'),
    ("created_at >= '2026-10-09' AND created_at < '2026-10-15'", 'start_wrong'),
    ("created_at >= '2026-10-08' AND created_at < '2026-10-16'", 'end_wrong'),
    ("created_at >= '2026-10-09' AND created_at < '2026-10-16'", 'both_wrong'),
    ("created_at < '2026-10-15'", 'start_wrong'),
    ("created_at >= '2026-10-08'", 'end_wrong'),
    ("actor = 'created_at'", 'no_window_predicate'),
    ("DATE '2026-10-08' <= created_at AND DATE '2026-10-15' > created_at", 'correct'),
    ("created_at > '2026-10-08' AND created_at < '2026-10-15'", 'start_wrong'),
    ("created_at >= '2026-10-08' AND created_at <= '2026-10-15'", 'end_wrong'),
    ("created_at >= '2026-10-08' AND created_at <= '2026-10-14 23:59:59.999999'", 'correct'),
    ("created_at BETWEEN DATE '2026-10-08' AND DATE '2026-10-14'", 'end_wrong'),
    ("created_at BETWEEN TIMESTAMP '2026-10-08' AND TIMESTAMP '2026-10-15'", 'end_wrong'),
    ("CAST(created_at AS DATE) BETWEEN DATE '2026-10-08' AND DATE '2026-10-14'", 'correct'),
    ("created_at::DATE >= '2026-10-08' AND created_at::DATE <= '2026-10-14'", 'correct'),
    ("DATE(created_at) > '2026-10-07' AND DATE(created_at) < '2026-10-15'", 'correct'),
    ("CAST(created_at AS DATE) >= '2026-10-08 12:00:00'", 'unparseable'),
    ("created_at >= DATE '2026-10-07' + INTERVAL '1 day' AND created_at < DATE '2026-10-16' - INTERVAL '1 day'", 'correct'),
    (WINDOW + " AND created_at >= DATE '2026-10-01'", 'correct'),
    (WINDOW + " AND created_at >= DATE '2026-10-09'", 'start_wrong'),
    (WINDOW + " AND created_at < DATE '2026-10-07'", 'unparseable'),
    (f"({WINDOW} AND type = 'PushEvent') OR ({WINDOW} AND type = 'WatchEvent')", 'correct'),
    (f"({WINDOW}) OR type = 'PushEvent'", 'unparseable'),
    (f"({WINDOW}) OR (created_at >= '2026-10-09' AND created_at < '2026-10-15')", 'unparseable'),
    (f"NOT ({WINDOW})", 'unparseable'),
    ("created_at >= CURRENT_DATE", 'unparseable'),
    ("created_at >= $start", 'unparseable'),
    ("DATE_TRUNC('day', created_at) >= DATE '2026-10-08'", 'unparseable'),
    ("created_at + INTERVAL '1 day' >= DATE '2026-10-08'", 'unparseable'),
    ("created_at IS NOT NULL", 'unparseable'),
    ("created_at IN (DATE '2026-10-08')", 'unparseable'),
    ("created_at >= TIMESTAMPTZ '2026-10-08 00:00:00+00:00'", 'unparseable'),
    ("created_at >= '2026-10-08T00:00:00+00:00'", 'unparseable'),
    ("created_at >= '2026-10-08 00:00:00.000000001'", 'unparseable'),
    ("created_at >= DATE '2026-02-30'", 'unparseable'),
    ("created_at >= DATE '2026-10-08' + INTERVAL '1 month'", 'unparseable'),
    ("CAST(CAST(created_at AS DATE) AS TIMESTAMP) >= DATE '2026-10-08'", 'unparseable'),
])
def test_primary_categories_and_exact_endpoint_types(predicate, expected):
    result = analyze_sql('SELECT COUNT(*) FROM events WHERE ' + predicate, BOUNDS)
    assert result['classification'] == expected, result


@pytest.mark.parametrize('sql,expected', [
    ('SELECT COUNT(*) FROM events', 'no_window_predicate'),
    ('SELECT CAST(created_at AS DATE) AS day, COUNT(*) FROM events GROUP BY 1', 'no_window_predicate'),
    (f'SELECT * FROM events e WHERE {WINDOW.replace("created_at", "e.created_at")}', 'correct'),
    (f'SELECT * FROM events e JOIN repos r ON e.repo_id=r.repo_id WHERE {WINDOW.replace("created_at", "e.created_at")}', 'correct'),
    (f'SELECT * FROM events e JOIN repos r ON e.repo_id=r.repo_id WHERE {WINDOW}', 'unparseable'),
    (f'WITH x AS (SELECT * FROM events WHERE {WINDOW}) SELECT COUNT(*) FROM x', 'correct'),
    (f'WITH x AS (SELECT created_at AS ts FROM events) SELECT * FROM x WHERE {WINDOW.replace("created_at", "ts")}', 'correct'),
    (f'SELECT * FROM (SELECT created_at AS ts FROM events) x WHERE {WINDOW.replace("created_at", "x.ts")}', 'correct'),
    ("WITH x AS (SELECT created_at::DATE AS day FROM events) SELECT * FROM x WHERE day BETWEEN DATE '2026-10-08' AND DATE '2026-10-14'", 'correct'),
    ("WITH unused AS (SELECT * FROM events WHERE created_at >= CURRENT_DATE) SELECT * FROM repos", 'no_window_predicate'),
    (f'WITH x AS (SELECT created_at AS ts FROM events LIMIT 10) SELECT * FROM x WHERE {WINDOW.replace("created_at", "ts")}', 'unparseable'),
    (f'WITH x AS (SELECT DISTINCT created_at AS ts FROM events) SELECT * FROM x WHERE {WINDOW.replace("created_at", "ts")}', 'unparseable'),
    (f'WITH x AS (SELECT created_at AS ts, count(*) FROM events GROUP BY 1) SELECT * FROM x WHERE {WINDOW.replace("created_at", "ts")}', 'unparseable'),
    (f'WITH x AS (SELECT * FROM events) SELECT * FROM x a JOIN x b ON a.repo_id=b.repo_id WHERE {WINDOW.replace("created_at", "a.created_at")}', 'unparseable'),
    (f'SELECT * FROM events a JOIN events b ON a.repo_id=b.repo_id WHERE {WINDOW.replace("created_at", "a.created_at")}', 'unparseable'),
    ('SELECT (SELECT MAX(created_at) FROM events) FROM repos', 'unparseable'),
    ('SELECT * FROM events UNION SELECT * FROM events', 'unparseable'),
    (f'SELECT * FROM events e LEFT JOIN repos r ON {WINDOW.replace("created_at", "e.created_at")}', 'unparseable'),
    (f'SELECT * FROM events e JOIN repos r ON {WINDOW.replace("created_at", "e.created_at")}', 'correct'),
    (f'SELECT * FROM repos WHERE {WINDOW}', 'unparseable'),
    ('SELECT * FROM events; SELECT * FROM events;', 'unparseable'),
    ('DELETE FROM events', 'unparseable'),
    ('SELECT ( FROM events', 'unparseable'),
    ('', 'unparseable'),
    (None, 'unparseable'),
])
def test_scope_lineage_and_unknown_are_conservative(sql, expected):
    assert analyze_sql(sql, BOUNDS)['classification'] == expected


@pytest.mark.parametrize('predicate,expected', [
    ("CAST(created_at AS DATE) = DATE '2026-10-08'", 'correct'),
    ("created_at = DATE '2026-10-08'", 'end_wrong'),
])
def test_single_day_equality_differs_by_column_type(predicate, expected):
    assert analyze_sql('SELECT * FROM events WHERE ' + predicate, ['2026-10-08', '2026-10-09'])['classification'] == expected


@pytest.mark.parametrize('sql,observed,secondary', [
    ('SELECT * FROM repos', False, 'parsed'),
    (f'SELECT * FROM events WHERE {WINDOW}', True, 'parsed'),
    ('SELECT * FROM events WHERE created_at >= CURRENT_DATE', True, 'unparseable'),
    ('broken SQL', None, 'unparseable'),
])
def test_controls_keep_primary_path_but_expose_extra_filters(sql, observed, secondary):
    result = analyze_sql(sql, None)
    assert result['classification'] == 'no_window_predicate'
    assert result['observed_time_filter'] is observed
    assert result['secondary_parse_status'] == secondary


@pytest.mark.parametrize('end,expected', [
    ("DATE '2026-10-14'", 'correct'),
    ("TIMESTAMP '2026-10-15' - INTERVAL '1 day'", 'correct'),
    ("DATE '2026-10-15'", 'wrong'),
    ('CURRENT_DATE', 'unparseable'),
])
def test_calendar_end_is_secondary_not_a_window_proof(end, expected):
    sql = f"WITH counts AS (SELECT * FROM events WHERE {WINDOW}) SELECT * FROM counts CROSS JOIN generate_series(DATE '2026-10-08', {end}, INTERVAL '1 day') t(day)"
    result = analyze_sql(sql, BOUNDS)
    assert result['classification'] == 'correct'
    assert result['generate_series_end'] == expected
    assert analyze_sql(sql, None)['classification'] == 'no_window_predicate'


def test_invalid_authorized_bounds_and_parser_has_no_frozen_imports():
    assert analyze_sql('SELECT * FROM events', ['2026-10-15', '2026-10-08'])['classification'] == 'unparseable'
    path = Path(__file__).resolve().parents[1] / 'eval/v4_sql_bounds.py'
    tree = ast.parse(path.read_text())
    imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    assert not any(name and (name.startswith('agent') or name.startswith('eval')) for name in imports)


@pytest.mark.parametrize('sql', [
    "WITH x(ts) AS (SELECT created_at FROM events) SELECT * FROM x WHERE ts >= DATE '2026-10-08'",
    "SELECT created_at::DATE AS day FROM events WHERE day >= DATE '2026-10-08'",
    "SELECT * FROM other.events WHERE created_at >= DATE '2026-10-08'",
])
def test_unsupported_temporal_alias_or_external_source_is_unknown(sql):
    assert analyze_sql(sql, BOUNDS)['classification'] == 'unparseable'


def test_date_function_literal_and_single_day_cast():
    sql = "SELECT * FROM events WHERE DATE(created_at) BETWEEN DATE('2026-10-08') AND DATE('2026-10-14')"
    assert analyze_sql(sql, BOUNDS)['classification'] == 'correct'


@pytest.mark.parametrize('projection', [
    "COUNT(*) FILTER (WHERE created_at >= DATE '2026-10-09')",
    "SUM(CASE WHEN created_at < DATE '2026-10-14' THEN 1 ELSE 0 END)",
])
def test_embedded_temporal_filters_never_receive_a_false_correct(projection):
    sql = f'SELECT {projection} FROM events WHERE {WINDOW}'
    assert analyze_sql(sql, BOUNDS)['classification'] == 'unparseable'
    control = analyze_sql(sql, None)
    assert control['classification'] == 'no_window_predicate' and control['observed_time_filter'] is True
