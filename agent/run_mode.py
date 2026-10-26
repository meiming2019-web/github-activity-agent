"""Explicit mode-aware CLI and isolated live UI adapter; no services on import."""

import argparse
import asyncio
from copy import deepcopy
import json
from pathlib import Path
import sys
from time import perf_counter

from agent import loop
from agent.live_context import live_date_context_for_question, metric_lookup, mode, question_window, utc_now
from agent.live_server import LIVE_DATABASE, live_path

ROOT = Path(__file__).resolve().parents[1]


async def run_live(question, on_update=None, *, clock=None, database=LIVE_DATABASE):
    """Capture one clock and fresh live state; reject syntax before credentials/services."""
    now = utc_now(clock)
    trace = loop.new_trace(question, now.date().isoformat())
    trace['mode'] = 'live'
    started = perf_counter()
    api_key = ''
    timings, setup = {}, []

    def snapshot():
        return loop.sanitize({'trace': deepcopy(trace), 'tool_timings_ms': dict(timings),
                              'setup_steps': deepcopy(setup), 'elapsed_ms': (perf_counter()-started)*1000,
                              'rounds': len(trace['api_responses'])}, api_key)

    def notify():
        if on_update is not None:
            on_update(snapshot())

    try:
        question_window(question, clock=lambda: now)
        database = live_path(database)
        if not database.is_file():
            raise ValueError('Live database missing; run scripts/ingest_live.py first.')
        # API access is only on explicit UI submission/CLI execution, never module import.
        from dotenv import dotenv_values
        api_key = (dotenv_values(ROOT / '.env').get('DEEPSEEK_API_KEY') or '').strip()
        if not api_key:
            raise ValueError('DEEPSEEK_API_KEY is missing or empty.')
        parameters = loop.StdioServerParameters(command=sys.executable,
                     args=['-B', '-m', 'agent.live_server'], cwd=str(ROOT), env=loop.get_default_environment())
        # The public runtime has one fixed live DB; alternate paths are for offline substituted transports only.
        if database != LIVE_DATABASE.resolve():
            raise ValueError('The live transport uses only data/github_live.duckdb.')
        async with loop.AsyncOpenAI(api_key=api_key, base_url='https://api.deepseek.com', max_retries=0, timeout=60.0) as client:
            async with loop.stdio_client(parameters) as (reader, writer):
                async with loop.ClientSession(reader, writer, read_timeout_seconds=20) as session:
                    await session.initialize()
                    from ui.app import TimedSession
                    timed = TimedSession(session, trace, timings, setup, notify)
                    glossary = (ROOT / 'eval/glossary.md').read_text(encoding='utf-8')
                    shared = await live_date_context_for_question(question, timed, glossary, clock=lambda: now, database=database)
                    trace['live_coverage'] = json.loads(shared.split('\n')[1])['coverage']
                    def lookup(term):
                        return metric_lookup(glossary, term)
                    notify()
                    trace = await loop.run_loop(client, timed, trace, api_key, config='C',
                                                system_context=shared, lookup_glossary=lookup)
    except Exception as error:
        trace['status'] = 'error'
        trace['final_answer'] = f'Agent stopped: {loop.sanitize(str(error), api_key)}'
    notify()
    return snapshot()


def main(argv=None):
    """Eval uses the unchanged UI path and frozen date; no eval trace file is written."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('question')
    args = parser.parse_args(argv)
    if not args.question.strip():
        parser.error('question must not be empty')
    selected = mode()
    if selected == 'live':
        result = asyncio.run(run_live(args.question))
    else:
        from ui.app import run_demo
        result = asyncio.run(run_demo(args.question))
    # Output is redacted and remains on stdout: no shared eval/live disk history.
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return 0 if result['trace']['status'] == 'completed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
