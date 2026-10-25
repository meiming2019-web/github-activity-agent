"""Prepare both passes or explicitly collect one v4 pass; imports never launch an experiment."""

import argparse
import asyncio
from collections import Counter
from contextlib import contextmanager
import fcntl
import hashlib
from itertools import permutations
import json
from pathlib import Path
import random
import time

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = ROOT / 'eval/v4_questions.jsonl'
SCHEDULE = ROOT / 'eval/v4_schedule.jsonl'
RESULTS = ROOT / 'eval/results/runs_v4.jsonl'
PASS2_RESULTS = ROOT / 'eval/results/runs_v4_pass2.jsonl'
SUBSET_SEED = 4201
PASS2_ORDER_SEED = 4202
SEED = 42
CONFIGS = ('C', 'C2.1', 'C3.1')
WORKERS = 5


def load_questions(path=QUESTIONS):
    """Read the frozen question records without loading credentials or a database."""
    data = Path(path).read_bytes()
    rows = [json.loads(line) for line in data.splitlines() if line.strip()]
    questions = [row for row in rows if row.get('record_type') == 'question']
    if len(questions) != 300 or len({row['id'] for row in questions}) != 300:
        raise ValueError('The formal v4 schedule requires 300 unique questions')
    return questions, hashlib.sha256(data).hexdigest()


def validate_schedule(rows, questions, digest):
    """Verify both persisted passes without redrawing a subset or any order."""
    meta, assignments = rows[0], rows[1:]
    if meta != {'record_type': 'metadata', 'seed': SEED, 'subset_seed': SUBSET_SEED,
                'pass2_order_seed': PASS2_ORDER_SEED, 'question_sha256': digest,
                'configs': list(CONFIGS), 'workers': WORKERS, 'passes': [1, 2]}:
        raise ValueError('Schedule metadata mismatch')
    if len(assignments) != 360 or any(row['pass'] not in (1, 2) for row in assignments):
        raise ValueError('Schedule must contain 300 pass-1 and 60 pass-2 assignments')
    ids = [question['id'] for question in questions]
    for pass_number, count in ((1, 300), (2, 60)):
        selected = [row for row in assignments if row['pass'] == pass_number]
        selected_ids = [row['question_id'] for row in selected]
        if len(selected) != count or len(set(selected_ids)) != count or not set(selected_ids) <= set(ids):
            raise ValueError('Invalid pass subset')
        if selected_ids != sorted(selected_ids, key=ids.index):
            raise ValueError('Question order differs from the frozen source order')
        for index, row in enumerate(selected):
            if set(row) != {'question_id', 'order', 'worker', 'pass'} or row['worker'] != index % WORKERS or sorted(row['order']) != sorted(CONFIGS):
                raise ValueError('Invalid persisted schedule assignment')
        if Counter(tuple(row['order']) for row in selected) != Counter({order: count // 6 for order in permutations(CONFIGS)}):
            raise ValueError('The six config permutations must be exactly balanced within each pass')
    return assignments


def prepare_schedule(path=SCHEDULE, questions_path=QUESTIONS):
    """Create both passes once; resume only reads and verifies the existing bytes."""
    questions, digest = load_questions(questions_path)
    path = Path(path)
    if path.exists():
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        return validate_schedule(rows, questions, digest)
    subset_ids = set(random.Random(SUBSET_SEED).sample([row['id'] for row in questions], 60))
    rows = [{'record_type': 'metadata', 'seed': SEED, 'subset_seed': SUBSET_SEED,
             'pass2_order_seed': PASS2_ORDER_SEED, 'question_sha256': digest,
             'configs': list(CONFIGS), 'workers': WORKERS, 'passes': [1, 2]}]
    for pass_number, selected, seed in ((1, questions, SEED),
            (2, [row for row in questions if row['id'] in subset_ids], PASS2_ORDER_SEED)):
        orders = list(permutations(CONFIGS)) * (len(selected) // 6)
        random.Random(seed).shuffle(orders)
        rows += [{'question_id': question['id'], 'order': list(order), 'worker': index % WORKERS, 'pass': pass_number}
                 for index, (question, order) in enumerate(zip(selected, orders))]
    validate_schedule(rows, questions, digest)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('x', encoding='utf-8') as output:
            output.write(''.join(json.dumps(row, sort_keys=True) + '\n' for row in rows))
    except FileExistsError:
        return prepare_schedule(path, questions_path)
    return rows[1:]


@contextmanager
def _locked_history(path):
    """Serialize cross-process history checks and append/fsync under flock."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+', encoding='utf-8') as output:
        fcntl.flock(output.fileno(), fcntl.LOCK_EX)
        try:
            output.seek(0)
            text = output.read()
            if text and not text.endswith('\n'):
                raise ValueError('Incomplete trailing result record; manual recovery required')
            rows = [json.loads(line) for line in text.splitlines()]
            yield output, rows
        finally:
            fcntl.flock(output.fileno(), fcntl.LOCK_UN)


def _append(output, row):
    """Durably append one JSON line while its caller holds the history lock."""
    import os
    output.seek(0, 2)
    output.write(json.dumps(row, ensure_ascii=False, allow_nan=False, sort_keys=True) + '\n')
    output.flush()
    os.fsync(output.fileno())


def write_first(path, record):
    """Commit only the first record for a question/config/pass, including errors."""
    key = tuple(record[name] for name in ('question_id', 'config', 'pass'))
    with _locked_history(path) as (output, history):
        if any(row.get('record_type') == 'trial' and tuple(row[name] for name in ('question_id', 'config', 'pass')) == key for row in history):
            return False
        _append(output, record)
        return True


def begin_block(path, now):
    """Record an initial block or a new block after strictly over two hours."""
    with _locked_history(path) as (output, history):
        if not history:
            block, reason = 1, 'initial'
        else:
            latest = max(row['recorded_at'] for row in history)
            previous = max(row['block'] for row in history)
            if now - latest <= 7200:
                return previous
            block, reason = previous + 1, 'interruption_over_two_hours'
        _append(output, {'record_type': 'block', 'block': block, 'recorded_at': now,
                         'reason': reason, 'harness_version': 'c2.1'})
        return block


def recorded_keys(path):
    """Read committed trial identities without scoring or aggregating outcomes."""
    if not Path(path).exists():
        return set()
    with _locked_history(path) as (_, history):
        return {(row['question_id'], row['config'], row['pass']) for row in history if row.get('record_type') == 'trial'}


def require_pass1_complete(path, questions):
    """Pass 2 is blocked until all 900 pass-1 trial records exist, regardless of outcome."""
    if len(questions) != 300 or len({row['id'] for row in questions}) != 300:
        raise ValueError('Pass-2 gate requires the complete 300-question universe')
    required = {(row['id'], config, 1) for row in questions for config in CONFIGS}
    if not required <= recorded_keys(path):
        raise ValueError('Pass 1 is incomplete; pass 2 cannot start')


async def collect(questions, assignments, trial, path, *, offline=True, clock=time.time, pass1_path=None, full_questions=None):
    """Five workers; each assigned question's three fresh trials remain adjacent."""
    path = Path(path)
    pass_numbers = {row['pass'] for row in assignments}
    if len(pass_numbers) != 1 or not pass_numbers <= {1, 2}:
        raise ValueError('Collect exactly one declared pass at a time')
    pass_number = next(iter(pass_numbers))
    if pass_number == 2:
        if pass1_path is None or full_questions is None:
            raise ValueError('Pass-2 completion evidence is required')
        require_pass1_complete(pass1_path, full_questions)
    if offline and path.resolve() in {RESULTS.resolve(), PASS2_RESULTS.resolve()}:
        raise ValueError('Offline/mock collection cannot write formal results')
    if not offline and path.resolve() != (RESULTS if pass_number == 1 else PASS2_RESULTS).resolve():
        raise ValueError('Each live pass has exactly one authorized result path')
    by_id = {question['id']: question for question in questions}
    if len(by_id) != len(questions) or len({row['question_id'] for row in assignments}) != len(assignments):
        raise ValueError('Duplicate question assignments')
    if any(row['question_id'] not in by_id or row['pass'] != pass_number or row['worker'] not in range(WORKERS) or sorted(row['order']) != sorted(CONFIGS) for row in assignments):
        raise ValueError('Unsupported assignment')
    completed = recorded_keys(path)
    block = begin_block(path, clock())
    total = len(assignments) * 3
    done = sum((row['question_id'], config, pass_number) in completed for row in assignments for config in CONFIGS)
    async def worker(number):
        nonlocal done
        for assignment in assignments:
            if assignment['worker'] != number:
                continue
            question = by_id[assignment['question_id']]
            for config in assignment['order']:
                key = (question['id'], config, pass_number)
                if key in completed:
                    continue
                started = clock()
                try:
                    trace = await trial(question, config)
                except Exception:
                    # Do not print exception messages, credentials, traces, or scores.
                    trace = {'status': 'transport_error', 'submitted': False, 'answer_sql': None}
                record = {**trace, 'record_type': 'trial', 'question_id': question['id'], 'config': config,
                          'pass': pass_number, 'worker': number, 'block': block, 'recorded_at': clock(),
                          'started_at': started, 'harness_version': 'c2.1'}
                if write_first(path, record):
                    completed.add(key); done += 1
                print(f'Completed pairs: {done}/{total}', flush=True)
    await asyncio.gather(*(worker(number) for number in range(WORKERS)))
    return done


class FingerprintClient:
    """Transparent request delegate that retains response.model, not credentials."""

    def __init__(self, client):
        from types import SimpleNamespace
        self.client = client
        self.models = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    async def create(self, **kwargs):
        response = await self.client.chat.completions.create(**kwargs)
        self.models.append(getattr(response, 'model', None))
        return response


async def run_trial(question, config, client, session, api_key):
    """Use the real frozen loop with new state and the authorized C2.1 entry."""
    from agent import loop
    from agent.context import REFERENCE_DATE, shared_context, lookup_glossary, c2_date_context_for_question
    if config not in CONFIGS:
        raise ValueError('Unknown v4 configuration')
    glossary = (ROOT / 'eval/glossary.md').read_text()
    shared = await shared_context(session)
    context = shared + ('\n\nUse lookup_glossary for definitions. Available topics include new_stars, '
                        'collaboration_events, active_contributors, time conventions, dataset scope, event types.')
    if config != 'C':
        context += '\n\n' + await c2_date_context_for_question(question['question'], session, glossary)
    proxy = FingerprintClient(client)
    trace = await loop.run_loop(proxy, session, loop.new_trace(question['question'], REFERENCE_DATE), api_key,
                                config='C3' if config == 'C3.1' else 'C', system_context=context,
                                lookup_glossary=lambda term: lookup_glossary(glossary, term))
    return loop.sanitize({**trace, 'response_models': proxy.models, 'harness_version': 'c2.1'}, api_key)


async def live_trial(question, config, api_key):
    """Explicit future network entry; never invoked by preparation or offline tests."""
    import sys
    from agent import loop
    parameters = loop.StdioServerParameters(command=sys.executable,
        args=['-B', str(ROOT / 'agent/mcp_server.py')], cwd=str(ROOT), env=loop.get_default_environment())
    async with loop.AsyncOpenAI(api_key=api_key, base_url='https://api.deepseek.com', max_retries=0, timeout=60.0) as client:
        async with loop.stdio_client(parameters) as (reader, writer):
            async with loop.ClientSession(reader, writer, read_timeout_seconds=20) as session:
                await session.initialize()
                return await run_trial(question, config, client, session, api_key)


async def execute_pass(pass_number, api_key):
    """Explicit future collection entry; enforce the pass-1 completion gate for pass 2."""
    if pass_number not in (1, 2):
        raise ValueError('Only the two frozen passes exist')
    if not api_key:
        raise ValueError('An explicitly supplied API key is required')
    questions, _ = load_questions()
    assignments = [row for row in prepare_schedule() if row['pass'] == pass_number]
    async def trial(question, config):
        return await live_trial(question, config, api_key)
    return await collect(questions, assignments, trial, RESULTS if pass_number == 1 else PASS2_RESULTS,
                         offline=False, pass1_path=RESULTS, full_questions=questions)


async def smoke(question_id, path, api_key):
    """Future d01-d15 smoke only; never write the formal result path."""
    path = Path(path)
    if question_id not in {f'd{number:02}' for number in range(1, 16)} or path.resolve() in {RESULTS.resolve(), PASS2_RESULTS.resolve()} or path.resolve().is_relative_to((ROOT / 'eval/results').resolve()):
        raise ValueError('Smoke requires a development ID and a nonformal output path')
    questions = [json.loads(line) for line in (ROOT / 'eval/github_dev_questions.jsonl').read_text().splitlines()]
    question = next(row for row in questions if row['id'] == question_id)
    async def trial(row, config):
        return await live_trial(row, config, api_key)
    return await collect([question], [{'question_id': question_id, 'order': list(CONFIGS), 'worker': 0, 'pass': 1}], trial, path)


def main(argv=None):
    """No default execution: preparation, formal collection, and smoke are explicit."""
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--prepare', action='store_true')
    modes.add_argument('--execute-pass1', action='store_true')
    modes.add_argument('--execute-pass2', action='store_true')
    modes.add_argument('--smoke', choices=[f'd{number:02}' for number in range(1, 16)])
    parser.add_argument('--smoke-output', type=Path)
    args = parser.parse_args(argv)
    if args.prepare:
        prepare_schedule()
        print('Schedule prepared: pass 1 = 900 pairs; pass 2 = 180 pairs. No trials executed.')
        return 0
    if args.smoke and args.smoke_output is None:
        parser.error('--smoke-output is required')
    import getpass
    key = getpass.getpass('API key for explicitly authorized future execution: ')
    asyncio.run(smoke(args.smoke, args.smoke_output, key) if args.smoke else execute_pass(2 if args.execute_pass2 else 1, key))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
