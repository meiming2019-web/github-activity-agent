"""Offline generator invariants, hard-assertion behavior, and byte reproducibility."""

from collections import Counter
from datetime import date, datetime, timedelta
from decimal import Decimal
import json
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from eval import gen_v4_questions as generator
from eval.check_v4_dedup import check_dedup, normalized_text
from eval.row_normalize import normalize_rows


@pytest.mark.parametrize("family", generator.WINDOW_FAMILIES + generator.TARGETED_ADVANCED + generator.ADJACENT + generator.CONTROLS)
def test_each_template_executes_through_real_readonly_allowlist(family):
    params = {"entity": "TypeScript" if family == "language_composition" else "openclaw/openclaw",
              "scope": "repo", "event_type": "WatchEvent"}
    sql, metrics = generator.reference_sql(family, params, date(2026, 10, 15), date(2026, 10, 22))
    columns, rows = generator.run_reference(sql)
    question = generator.question_text(family, params, "the last 7 days", "literal")
    generator.assert_reference(sql, columns, rows, metrics, question)
    assert rows


@pytest.mark.parametrize("family", generator.WINDOW_FAMILIES)
def test_language_rankings_have_explicit_deterministic_ties(family):
    params = {"entity": "TypeScript", "scope": "language", "event_type": None}
    sql, metrics = generator.reference_sql(family, params, date(2026, 10, 15), date(2026, 10, 22))
    columns, rows = generator.run_reference(sql)
    for layer in generator.PARAPHRASES:
        question = generator.question_text(family, params, "last week", layer)
        generator.assert_reference(sql, columns, rows, metrics, question)
        assert "break ties by repo_name ascending" in question
    assert 1 <= len(rows) <= 5


@pytest.mark.parametrize("rows,sql,question,reason", (
    ([], "SELECT 1 AS value", "Count records", "empty_reference"),
    ([[0]], "SELECT 0 AS value", "Count records", "all_zero_aggregate"),
    ([[1]], "SELECT 1 AS value LIMIT 5", "Rank records", "missing_top_n_tie_rule"),
))
def test_item8_assertions_reject_invalid_references(rows, sql, question, reason):
    with pytest.raises(generator.CandidateRejected, match=reason):
        generator.assert_reference(sql, ["value"], rows, ["value"], question)


def test_json_round_trip_and_sql_literal_are_lossless_for_supported_values():
    assert normalize_rows([(date(2026, 10, 8), datetime(2026, 10, 8, 1), Decimal('1.25'), float('nan'))]) == [
        ['2026-10-08', '2026-10-08T01:00:00', '1.25', None]
    ]
    assert generator.sql_literal("owner/o'repo") == "'owner/o''repo'"


def test_dedup_rejects_historical_and_internal_normalized_overlap():
    assert normalized_text("  Hello, WORLD! ") == "hello world"
    assert check_dedup([{"question": "Unique synthetic v4 dedup test case"}])["historical_overlap"] == 0
    with pytest.raises(AssertionError, match="Duplicate"):
        check_dedup([{"question": "Hello world"}, {"question": "HELLO, world!"}])
    historic = json.loads((generator.ROOT / 'eval/v3_questions.jsonl').read_text().splitlines()[0])
    with pytest.raises(AssertionError, match="historical"):
        check_dedup([historic])


def test_fixed_seed_and_finite_regeneration_failure(tmp_path, monkeypatch):
    with pytest.raises(ValueError, match="fixed at 42"):
        generator.generate(43, tmp_path / 'wrong.jsonl')
    monkeypatch.setattr(generator, 'check_bounds_consistency', AsyncMock(return_value={}))
    monkeypatch.setattr(generator, 'candidate_plan', lambda family, expression, event, start, end: [(0, (expression, *generator.window_bounds(expression)), event)])
    monkeypatch.setattr(generator, 'run_reference', Mock(side_effect=[
        (['first_event', 'last_event'], [['2026-10-08T00:02:49', '2026-10-21T23:58:01']]),
        (['name'], [['only/repo']]), (['language'], [['Python']]), (['value'], [[0]]),
    ]))
    with pytest.raises(RuntimeError, match="after 1 deterministic attempts"):
        generator.generate(42, tmp_path / 'failed.jsonl')
    assert not (tmp_path / 'failed.jsonl').exists()
    rejected = [json.loads(line) for line in (tmp_path / 'v4_regen_log.jsonl').read_text().splitlines()]
    assert len(rejected) == 1 and rejected[0]['reason'] == 'all_zero_aggregate'


def test_full_generation_reproducibility_structure_sensitivity_and_probes(tmp_path):
    first = tmp_path / 'first' / 'questions.jsonl'
    second = tmp_path / 'second' / 'questions.jsonl'
    one = generator.generate(42, first)
    two = generator.generate(42, second)
    assert one == two
    assert first.read_bytes() == second.read_bytes()
    for name in ('v4_regen_log.jsonl', 'v4_overlap_audit.md'):
        assert (first.parent / name).read_bytes() == (second.parent / name).read_bytes()
    data = [json.loads(line) for line in first.read_text().splitlines()]
    meta, questions = data[0], data[1:]
    assert meta['seed'] == 42 and len(questions) == 300
    assert Counter(row['layer'] for row in questions) == {'window': 180, 'advanced_sql': 90, 'control': 30}
    assert sum(row['targeted'] for row in questions) == 240
    assert Counter(row['paraphrase_id'] for row in questions) == {'literal': 100, 'colloquial': 100, 'distractor': 100}
    assert len({row['template_family_id'] for row in questions}) == 11
    assert all(row['reference_rows'] for row in questions)
    for row in questions:
        if row['bounds'] is None:
            assert row['sensitivity_excluded'] == []
            continue
        start, end = (date.fromisoformat(value) for value in row['bounds'])
        expected = {(a, b) for a, b in ((1, 0), (0, -1), (0, 1), (-1, 0), (1, 1), (-1, -1))
                    if date(2026, 10, 8) <= start + timedelta(days=a) <= end + timedelta(days=b) <= date(2026, 10, 22)}
        actual = {(probe['start_shift_days'], probe['end_shift_days']) for probe in row['sensitivity']}
        assert actual == expected
        assert all(probe['eligible'] for probe in row['sensitivity'])
        assert row['battery_relaxed'] or all(probe['changed'] for probe in row['sensitivity'])
        assert row['failed_perturbations'] == [probe['perturbation'] for probe in row['sensitivity'] if not probe['changed']]
        assert len(row['sensitivity']) + len(row['sensitivity_excluded']) == 6
        assert all(not probe['eligible'] and 'reference_sql' not in probe for probe in row['sensitivity_excluded'])
    assert all(row['sensitivity'] == [] for row in questions if row['bounds'] is None)
    for row in questions:
        if row['paraphrase_id'] == 'distractor':
            assert row['distractor_probe']['used_for_filtering'] is False
            assert row['distractor_probe']['triggered'] == (row['bounds'] is not None)
    old_review = generator.ROOT / 'eval/v4_sample_review.md'
    old_bytes = old_review.read_bytes()
    first_review = first.parent / 'v4_sample_review_r2.md'
    second_review = second.parent / 'v4_sample_review_r2.md'
    before_questions = generator.ROOT / 'eval/v4_questions.jsonl'
    summary = generator.write_round2_review(before_questions, first, old_review, first_review)
    again = generator.write_round2_review(before_questions, second, old_review, second_review)
    assert summary == again and first_review.read_bytes() == second_review.read_bytes()
    assert old_review.read_bytes() == old_bytes
    assert len(summary['original_review_ids']) == 22
    assert set(summary['original_review_ids']) <= set(summary['selected_ids'])
    assert set(summary['reviewed_replacement_ids']) <= set(summary['selected_ids'])
    actual_expressions = {row['window_expression'] for row in questions if row['window_expression'] is not None}
    old_id_windows = {row['window_expression'] for row in questions if row['id'] in summary['original_review_ids']}
    expected_review_size = 22 + len(actual_expressions - old_id_windows)
    assert set(summary['window_expressions']) == actual_expressions
    assert len(summary['selected_ids']) == expected_review_size
    assert first_review.read_text().count('## v4_') == expected_review_size
    semantic_cases = {row['semantic_case_id']: row for row in questions}
    semantic_keys = [json.dumps([row['template_family_id'], row['parameters'], row['bounds']], sort_keys=True)
                     for row in semantic_cases.values()]
    assert len(semantic_keys) == len(set(semantic_keys)) == 100
    log = [json.loads(line) for line in (first.parent / 'v4_regen_log.jsonl').read_text().splitlines()]
    original_failed_window = [row for row in log if row['semantic_case_id'] == 'window_active_contributors_03_repo' and row['window_attempt'] == 1 and row['event_kind'] == 'hard_assertion_failure']
    assert len(original_failed_window) == len({row['entity'] for row in original_failed_window}) == 100
    assert all(row['window_expression'] == 'October 8 through October 9, 2026' for row in original_failed_window)
    assert any(row['window_expression'] != row['preferred_window_expression'] for row in questions if row['bounds'])
    for event in log:
        assert event['event_kind'] in {'hard_assertion_failure', 'dedup_exclusion', 'candidate_accepted', 'battery_relaxed_acceptance'}
        if event['event_kind'] == 'dedup_exclusion':
            assert event['reason'] == 'duplicate_semantic_candidate' and event['reference_sql'] is None
        else:
            assert event['reason'] != 'duplicate_semantic_candidate'
        assert event['attempt'] <= event['candidate_pool_positions']
        if event['sensitivity']:
            assert len(event['sensitivity']) + len(event['sensitivity_excluded']) == 6
            assert all('rows' in probe and 'rows_sha256' in probe for probe in event['sensitivity'])
    accepted = [event for event in log if event['event_kind'] in {'candidate_accepted', 'battery_relaxed_acceptance'}]
    assert len(accepted) == len({event['semantic_case_id'] for event in accepted}) == 100
    relaxed = [row for row in semantic_cases.values() if row['battery_relaxed']]
    assert len(relaxed) <= 2 and meta['battery_relaxed_semantic_cases'] == len(relaxed)
    for case in semantic_cases:
        variants = [row for row in questions if row['semantic_case_id'] == case]
        assert len(variants) == 3
        for key in ('parameters', 'bounds', 'reference_rows', 'reference_sql', 'window_expression', 'fallback_tier', 'battery_relaxed', 'sensitivity'):
            assert all(row[key] == variants[0][key] for row in variants)


@pytest.mark.parametrize("start,end,eligible", (
    (10, 15, {"start_plus_one", "end_minus_one", "end_plus_one", "start_minus_one", "both_plus_one", "both_minus_one"}),
    (8, 15, {"start_plus_one", "end_minus_one", "end_plus_one", "both_plus_one"}),
    (15, 22, {"start_plus_one", "end_minus_one", "start_minus_one", "both_minus_one"}),
    (8, 22, {"start_plus_one", "end_minus_one"}),
    (8, 9, {"start_plus_one", "end_minus_one", "end_plus_one", "both_plus_one"}),
))
def test_six_endpoint_battery_coverage_and_exclusion(start, end, eligible):
    cases = generator.sensitivity_cases(date(2026, 10, start), date(2026, 10, end), date(2026, 10, 8), date(2026, 10, 22))
    assert len(cases) == 6
    assert {case['perturbation'] for case in cases if case['eligible']} == eligible
    assert all(case['exclusion_reason'] == 'outside_snapshot_coverage' for case in cases if not case['eligible'])
    if start == 8 and end == 9:
        assert cases[0]['bounds'] == ['2026-10-09', '2026-10-09']
        assert cases[1]['bounds'] == ['2026-10-08', '2026-10-08']


def test_round2_distinguishes_replacement_from_evidence_only_changes(tmp_path):
    source = generator.ROOT / 'eval/v4_questions.jsonl'
    original = [json.loads(line) for line in source.read_text().splitlines()]
    previous = json.loads(json.dumps(original))
    current = json.loads(json.dumps(original))
    for row in current[1:]:
        row.setdefault('sensitivity_excluded', [])
    previous[1]['question'] = 'A deliberately different synthetic former question.'
    previous[1]['reference_rows'] = [[-1]]
    current[6]['sensitivity'] = []
    current[6]['sensitivity_excluded'] = [{'reason': 'synthetic evidence-only change'}]
    before = tmp_path / 'before.jsonl'; after = tmp_path / 'after.jsonl'
    before.write_text(''.join(json.dumps(row) + '\n' for row in previous))
    after.write_text(''.join(json.dumps(row) + '\n' for row in current))
    output = tmp_path / 'review.md'
    summary = generator.write_round2_review(before, after, generator.ROOT / 'eval/v4_sample_review.md', output)
    assert 'v4_001' in summary['reviewed_replacement_ids']
    assert 'v4_001' in summary['question_changed_ids'] and 'v4_001' in summary['answer_changed_ids']
    assert 'v4_006' in summary['metadata_only_changed_ids']
    assert 'v4_006' not in summary['reviewed_replacement_ids']
    assert 'REPLACEMENT OF AN ORIGINAL 22-QUESTION REVIEW ID' in output.read_text()
    actual_expressions = {row['window_expression'] for row in current[1:] if row['window_expression'] is not None}
    reviewed_expressions = {row['window_expression'] for row in current[1:] if row['id'] in summary['original_review_ids']}
    assert len(summary['selected_ids']) == 22 + len(actual_expressions - reviewed_expressions)
    assert set(summary['window_expressions']) == actual_expressions


@pytest.mark.parametrize("expression,count", (
    (None, 1), ("the last 7 days", 1), ("last week", 1), ("previous week", 1),
    ("October 8 through October 9, 2026", 13),
    ("October 12 through October 13, 2026", 13),
    ("October 8 through October 21, 2026", 1),
))
def test_complete_same_length_window_pool_preserves_preference_and_relative_meaning(expression, count):
    windows = generator.candidate_windows(expression, date(2026, 10, 8), date(2026, 10, 22))
    assert len(windows) == count and windows[0][0] == expression
    if expression is None:
        assert windows == [(None, None, None)]
        return
    first_start, first_end = generator.window_bounds(expression)
    assert windows[0][1:] == (first_start, first_end)
    assert all(end - start == first_end - first_start for _, start, end in windows)
    assert len({start for _, start, _ in windows}) == count
    assert [start for _, start, _ in windows[1:]] == sorted(start for _, start, _ in windows[1:])
    assert all(date(2026, 10, 8) <= start < end <= date(2026, 10, 22) for _, start, end in windows)
    if expression not in generator.WINDOW_EXPRESSIONS[:3]:
        assert count == 14 - (first_end - first_start).days + 1


@pytest.mark.parametrize("family,event,total", (("day_of_week", "PushEvent", 540), ("window_new_stars", None, 108), ("catalog_lookup", None, 1)))
def test_ladder_plan_complete_authorized_metric_and_window_order(family, event, total):
    expression = None if family == "catalog_lookup" else "previous week"
    plan = generator.candidate_plan(family, expression, event, date(2026, 10, 8), date(2026, 10, 22))
    assert len(plan) == total
    assert len({(window[0], metric) for _, window, metric in plan}) == total
    assert plan[0][0] == 0 and plan[0][1][0] == expression and plan[0][2] == event
    assert [tier for tier, _, _ in plan] == sorted(tier for tier, _, _ in plan)
    if family == 'day_of_week':
        tier1 = [(window[0], metric) for tier, window, metric in plan if tier == 1]
        assert tier1 == [('previous week', metric) for metric in generator.EVENT_TYPES if metric != 'PushEvent']
        assert [window[0] for tier, window, metric in plan if tier == 2][:5] == ['last week'] * 5
    if family == 'window_new_stars':
        assert all(tier != 1 and metric is None for tier, _, metric in plan)


@pytest.mark.parametrize("success_tier,relaxed_count,zero,duplicate_first", (
    (0, 0, False, False), (1, 0, False, False), (2, 0, False, False),
    (None, 0, False, False), (None, 1, False, False), (None, 2, False, False),
    (None, 0, True, False), (1, 0, False, True),
))
def test_ladder_exhaustion_evidence_and_semantic_case_relaxation_cap(monkeypatch, success_tier, relaxed_count, zero, duplicate_first):
    start, end = date(2026, 10, 10), date(2026, 10, 13)
    windows = [('October 10 through October 12, 2026', start, end),
               ('October 11 through October 13, 2026', start + timedelta(days=1), end + timedelta(days=1))]
    plan = [(0, windows[0], 'WatchEvent'), (1, windows[0], 'PushEvent'), (2, windows[1], 'WatchEvent')]
    monkeypatch.setattr(generator, 'candidate_plan', lambda *args: plan)
    def fake_sql(family, params, first, stop):
        return json.dumps([params['event_type'], first.isoformat(), stop.isoformat()]), ['value']
    def fake_reference(sql):
        metric, first, stop = json.loads(sql)
        tier = 1 if metric == 'PushEvent' else 2 if first == '2026-10-11' and stop == '2026-10-14' else 0
        baseline = (metric, first, stop) in [('WatchEvent', '2026-10-10', '2026-10-13'), ('PushEvent', '2026-10-10', '2026-10-13'), ('WatchEvent', '2026-10-11', '2026-10-14')]
        if zero:
            return ['value'], [[0]]
        # Distinct metric/window baselines must also have distinct fixture values,
        # because one candidate's shifted window can be another one's baseline.
        if metric == 'PushEvent':
            value = 10 if baseline or success_tier != 1 else 11
        elif success_tier in (0, 2):
            preferred = ('2026-10-10', '2026-10-13') if success_tier == 0 else ('2026-10-11', '2026-10-14')
            value = 10 if (first, stop) == preferred else 11
        else:
            value = 10
        return ['value'], [[value]]
    monkeypatch.setattr(generator, 'reference_sql', fake_sql)
    monkeypatch.setattr(generator, 'run_reference', fake_reference)
    assigned = {}
    if duplicate_first:
        params = {'entity': 'repo', 'scope': 'repo', 'event_type': 'WatchEvent'}
        assigned[json.dumps(['day_of_week', params, ['2026-10-10', '2026-10-13']], sort_keys=True)] = 'earlier_case'
    log = []
    args = ('day_of_week', 'synthetic_case', windows[0][0], 'repo', 'WatchEvent', ['repo'], 0,
            date(2026, 10, 8), date(2026, 10, 22), 42, 'fixture_snapshot', assigned, log, relaxed_count)
    if zero or (success_tier is None and relaxed_count == 2):
        with pytest.raises(RuntimeError, match='non-battery assertions' if zero else 'cap of 2'):
            generator.select_candidate(*args)
        assert len(log) == 3
        assert not any(event['event_kind'].endswith('acceptance') for event in log)
        return
    selected = generator.select_candidate(*args)
    expected = 3 if success_tier is None else success_tier
    assert selected['fallback_tier'] == expected
    assert selected['battery_relaxed'] == (expected == 3)
    if expected == 3:
        assert len(log) == 4 and log[-1]['strict_positions_exhausted'] == 3
        assert log[-1]['relaxed_semantic_case_number'] == relaxed_count + 1
        assert len(selected['failed_perturbations']) == 6
    if duplicate_first:
        assert log[0]['event_kind'] == 'dedup_exclusion'
    for event in log:
        if event['sensitivity']:
            assert len(event['sensitivity']) == 6
            assert all('rows' in item for item in event['sensitivity'])
