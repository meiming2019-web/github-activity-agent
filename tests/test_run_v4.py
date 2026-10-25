"""Offline schedule, persistence, and substituted transport tests; never call a model."""

import asyncio
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
import importlib.util
import json
import multiprocessing
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from eval import run_v4 as runner


def test_balanced_two_pass_schedule_is_reproducible_and_resume_never_redraws(tmp_path, monkeypatch):
    first, second = tmp_path / 'one.jsonl', tmp_path / 'two.jsonl'
    one = runner.prepare_schedule(first)
    assert one == runner.prepare_schedule(second) and first.read_bytes() == second.read_bytes()
    questions, digest = runner.load_questions()
    for number, expected in ((1, 50), (2, 10)):
        selected = [row for row in one if row['pass'] == number]
        assert len(selected) == expected * 6
        assert len(set(row['question_id'] for row in selected)) == len(selected)
        assert set(row['question_id'] for row in selected) <= {row['id'] for row in questions}
        assert set(Counter(tuple(row['order']) for row in selected).values()) == {expected}
    monkeypatch.setattr(runner.random, 'Random', Mock(side_effect=AssertionError('Resume redrew RNG')))
    before = first.read_bytes()
    assert runner.prepare_schedule(first) == one and first.read_bytes() == before
    rows = [json.loads(line) for line in before.splitlines()]
    assert runner.validate_schedule(rows, questions, digest) == one
    for key, value in [('seed', 43), ('question_sha256', 'wrong'), ('subset_seed', 0)]:
        altered = json.loads(json.dumps(rows)); altered[0][key] = value
        with pytest.raises(ValueError): runner.validate_schedule(altered, questions, digest)
    altered = json.loads(json.dumps(rows)); altered[-1]['question_id'] = altered[-2]['question_id']
    with pytest.raises(ValueError): runner.validate_schedule(altered, questions, digest)
    altered = json.loads(json.dumps(rows)); altered[1]['order'] = altered[2]['order']
    if altered[1]['order'] != rows[1]['order']:
        with pytest.raises(ValueError): runner.validate_schedule(altered, questions, digest)
    invalid = tmp_path / 'invalid.jsonl'; invalid.write_text('{}\n')
    with pytest.raises(ValueError): runner.load_questions(invalid)


def test_first_write_wins_across_threads_processes_and_resume(tmp_path):
    path = tmp_path / 'trials.jsonl'
    row = {'record_type': 'trial', 'question_id': 'q', 'config': 'C', 'pass': 1, 'recorded_at': 10, 'block': 1}
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda index: runner.write_first(path, {**row, 'attempt': index}), range(32)))
    assert sum(results) == 1 and len(path.read_text().splitlines()) == 1
    context = multiprocessing.get_context('fork')
    processes = [context.Process(target=runner.write_first, args=(path, {**row, 'question_id': 'p', 'attempt': index})) for index in range(6)]
    for process in processes: process.start()
    for process in processes:
        process.join(10); assert process.exitcode == 0
    assert len(path.read_text().splitlines()) == 2
    assert runner.recorded_keys(path) == {('q', 'C', 1), ('p', 'C', 1)}
    assert not runner.write_first(path, {**row, 'status': 'different'})
    assert runner.write_first(path, {**row, 'pass': 2})
    assert len(path.read_text().splitlines()) == 3


def test_blocks_and_torn_record_stop_without_repair(tmp_path):
    path = tmp_path / 'blocks.jsonl'
    assert runner.recorded_keys(path) == set() and not path.exists()
    assert runner.begin_block(path, 100) == 1
    assert runner.begin_block(path, 7300) == 1
    assert runner.begin_block(path, 7301) == 2
    assert len(path.read_text().splitlines()) == 2
    broken = tmp_path / 'broken.jsonl'; broken.write_text('{"unfinished":')
    before = broken.read_bytes()
    with pytest.raises(ValueError, match='Incomplete'): runner.recorded_keys(broken)
    assert broken.read_bytes() == before


def test_five_workers_keep_trios_adjacent_resume_and_print_only_progress(tmp_path, capsys):
    questions = [{'id': f'q{i}', 'question': f'Question {i}'} for i in range(10)]
    assignments = [{'question_id': row['id'], 'order': list(runner.CONFIGS), 'worker': i % 5, 'pass': 1} for i, row in enumerate(questions)]
    seen = {i: [] for i in range(5)}; concurrent = 0; peak = 0
    async def trial(question, config):
        nonlocal concurrent, peak
        number = int(question['id'][1:]) % 5
        seen[number].append((question['id'], config)); concurrent += 1; peak = max(peak, concurrent)
        await asyncio.sleep(0)
        concurrent -= 1
        if question['id'] == 'q0' and config == 'C': raise RuntimeError('PRIVATE_TRANSPORT_DETAIL')
        return {'status': 'completed', 'answer_sql': 'PRIVATE_SQL', 'submitted': True}
    path = tmp_path / 'offline.jsonl'
    assert asyncio.run(runner.collect(questions, assignments, trial, path, clock=lambda: 100)) == 30
    assert peak == 5
    for worker, visits in seen.items():
        assert visits == [(f'q{i}', config) for i in (worker, worker + 5) for config in runner.CONFIGS]
    before = path.read_bytes()
    assert asyncio.run(runner.collect(questions, assignments, AsyncMock(side_effect=AssertionError('rerun')), path, clock=lambda: 101)) == 30
    assert path.read_bytes() == before
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 30 and all(line.startswith('Completed pairs: ') for line in lines)
    rows = [json.loads(line) for line in before.splitlines() if json.loads(line)['record_type'] == 'trial']
    assert len(rows) == 30 and all(row['harness_version'] == 'c2.1' for row in rows)
    assert rows[0]['status'] == 'transport_error'


def test_pass2_gate_and_formal_paths_reject_mock_writes(tmp_path):
    questions, _ = runner.load_questions()
    path = tmp_path / 'pass1.jsonl'; second = tmp_path / 'pass2.jsonl'
    rows = [{'record_type': 'trial', 'question_id': question['id'], 'config': config, 'pass': 1, 'recorded_at': 0, 'block': 1}
            for question in questions for config in runner.CONFIGS]
    path.write_text(''.join(json.dumps(row) + '\n' for row in rows[:-1]))
    assignment = [{'question_id': questions[0]['id'], 'order': list(runner.CONFIGS), 'worker': 0, 'pass': 2}]
    fake = AsyncMock(return_value={'status': 'completed'})
    with pytest.raises(ValueError, match='incomplete'):
        asyncio.run(runner.collect(questions, assignment, fake, second, pass1_path=path, full_questions=questions))
    assert not second.exists() and fake.await_count == 0
    path.write_text(''.join(json.dumps(row) + '\n' for row in rows))
    runner.require_pass1_complete(path, questions)
    assert asyncio.run(runner.collect(questions, assignment, fake, second, pass1_path=path, full_questions=questions)) == 3
    with pytest.raises(ValueError, match='complete 300'): runner.require_pass1_complete(path, questions[:1])
    with pytest.raises(ValueError, match='completion evidence'):
        asyncio.run(runner.collect(questions, assignment, fake, second))
    for target in (runner.RESULTS, runner.PASS2_RESULTS):
        before = target.exists()
        with pytest.raises(ValueError, match='cannot write formal'):
            asyncio.run(runner.collect(questions, [{**assignment[0], 'pass': 1}], fake, target))
        assert target.exists() == before
    with pytest.raises(ValueError, match='authorized result path'):
        asyncio.run(runner.collect(questions, [{**assignment[0], 'pass': 1}], fake, second, offline=False))
    with pytest.raises(ValueError, match='exactly one'):
        asyncio.run(runner.collect(questions, [], fake, second))
    with pytest.raises(ValueError, match='Duplicate'):
        asyncio.run(runner.collect(questions, [{**assignment[0], 'pass': 1}] * 2, fake, second))


def test_real_trial_wiring_uses_fresh_traces_and_c31_only_changes_feedback(monkeypatch):
    from agent import context, loop
    monkeypatch.setattr(context, 'shared_context', AsyncMock(return_value='STATIC'))
    injected = AsyncMock(return_value='QUESTION_BOUNDARY')
    monkeypatch.setattr(context, 'c2_date_context_for_question', injected)
    calls = []
    async def fake_loop(client, session, trace, api_key, **kwargs):
        calls.append((trace, kwargs))
        assert kwargs['lookup_glossary']('new_stars')
        trace['status'] = 'completed'
        return trace
    monkeypatch.setattr(loop, 'run_loop', fake_loop)
    question = {'id': 'q', 'question': 'For last week, count records.'}
    for config in runner.CONFIGS:
        result = asyncio.run(runner.run_trial(question, config, object(), object(), 'synthetic-key'))
        assert result['harness_version'] == 'c2.1' and result['response_models'] == []
    assert len({id(trace) for trace, _ in calls}) == 3
    assert calls[0][1]['config'] == calls[1][1]['config'] == 'C'
    assert calls[2][1]['config'] == 'C3'
    assert calls[1][1]['system_context'] == calls[2][1]['system_context']
    assert 'QUESTION_BOUNDARY' not in calls[0][1]['system_context']
    assert injected.await_count == 2
    with pytest.raises(ValueError): asyncio.run(runner.run_trial(question, 'unknown', None, None, ''))


def test_response_fingerprint_proxy_is_transparent():
    response = SimpleNamespace(model='synthetic-model', choices=[])
    create = AsyncMock(return_value=response)
    proxy = runner.FingerprintClient(SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create))))
    assert asyncio.run(proxy.chat.completions.create(model='requested', messages=[])) is response
    assert proxy.models == ['synthetic-model']
    create.assert_awaited_once_with(model='requested', messages=[])


def test_live_transport_construction_is_fully_substituted(monkeypatch):
    from agent import loop
    session = SimpleNamespace(initialize=AsyncMock())
    client = object()
    @asynccontextmanager
    async def managed(value):
        yield value
    factory = Mock(return_value=managed(client))
    monkeypatch.setattr(loop, 'AsyncOpenAI', factory)
    monkeypatch.setattr(loop, 'get_default_environment', lambda: {})
    monkeypatch.setattr(loop, 'stdio_client', lambda params: managed(('reader', 'writer')))
    monkeypatch.setattr(loop, 'ClientSession', lambda *args, **kwargs: managed(session))
    fake = AsyncMock(return_value={'status': 'synthetic'})
    monkeypatch.setattr(runner, 'run_trial', fake)
    assert asyncio.run(runner.live_trial({'id': 'q'}, 'C', 'synthetic-key')) == {'status': 'synthetic'}
    assert session.initialize.await_count == 1 and fake.await_count == 1
    assert factory.call_args.kwargs['max_retries'] == 0


def test_explicit_execute_and_development_smoke_use_only_substitutes(tmp_path, monkeypatch):
    questions, _ = runner.load_questions()
    assignment = [{'question_id': questions[0]['id'], 'order': list(runner.CONFIGS), 'worker': 0, 'pass': number} for number in (1, 2)]
    monkeypatch.setattr(runner, 'prepare_schedule', lambda: assignment)
    fake_trial = AsyncMock(return_value={'status': 'synthetic'})
    monkeypatch.setattr(runner, 'live_trial', fake_trial)
    calls = []
    async def fake_collect(rows, schedule, trial, path, **kwargs):
        calls.append((schedule, path, kwargs))
        await trial(rows[0], 'C')
        return 3
    monkeypatch.setattr(runner, 'collect', fake_collect)
    for number in (1, 2): assert asyncio.run(runner.execute_pass(number, 'synthetic-key')) == 3
    assert calls[0][1] == runner.RESULTS and calls[1][1] == runner.PASS2_RESULTS
    assert calls[1][2]['full_questions'] == questions
    assert asyncio.run(runner.smoke('d01', tmp_path / 'smoke.jsonl', 'synthetic-key')) == 3
    assert calls[-1][0][0]['question_id'] == 'd01'
    for question, path in [('v4_001', tmp_path / 'x'), ('d01', runner.RESULTS), ('d02', runner.PASS2_RESULTS)]:
        with pytest.raises(ValueError): asyncio.run(runner.smoke(question, path, 'synthetic-key'))
    with pytest.raises(ValueError): asyncio.run(runner.execute_pass(3, 'synthetic-key'))
    with pytest.raises(ValueError): asyncio.run(runner.execute_pass(1, ''))


def test_cli_and_import_have_no_implicit_execution(monkeypatch, capsys):
    import getpass
    prepared = Mock(return_value=[])
    monkeypatch.setattr(runner, 'prepare_schedule', prepared)
    key = Mock(return_value='synthetic-key'); monkeypatch.setattr(getpass, 'getpass', key)
    executed = AsyncMock(return_value=0); smoked = AsyncMock(return_value=0)
    monkeypatch.setattr(runner, 'execute_pass', executed); monkeypatch.setattr(runner, 'smoke', smoked)
    assert runner.main(['--prepare']) == 0 and key.call_count == 0
    assert runner.main(['--execute-pass1']) == 0
    assert runner.main(['--execute-pass2']) == 0
    assert runner.main(['--smoke', 'd01', '--smoke-output', '/tmp/synthetic-smoke']) == 0
    assert executed.await_args_list[0].args[0] == 1 and executed.await_args_list[1].args[0] == 2
    with pytest.raises(SystemExit): runner.main([])
    with pytest.raises(SystemExit): runner.main(['--smoke', 'd01'])
    spec = importlib.util.spec_from_file_location('isolated_v4_runner', runner.__file__)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    assert key.call_count == 3 and executed.await_count == 2 and smoked.await_count == 1
