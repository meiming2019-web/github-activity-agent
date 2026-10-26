"""Clock-injected live windows and read-only metric definitions, isolated from eval."""

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re

from agent.context import lookup_glossary, tool_payload
from agent.live_server import LIVE_DATABASE, isolated_server

ROOT = Path(__file__).resolve().parents[1]
MONTHS = 'January February March April May June July August September October November December'.split()
MONTH = '(?:' + '|'.join(MONTHS) + ')'
EXPRESSION = re.compile(
    rf'\b(?:the last (?P<n>\d+) days|last week|previous week)\b|'
    rf'\b(?P<iso1>\d{{4}}-\d{{2}}-\d{{2}}) through (?P<iso2>\d{{4}}-\d{{2}}-\d{{2}})\b|'
    rf'\b(?P<m1>{MONTH}) (?P<d1>\d{{1,2}})(?:, (?P<y1>\d{{4}}))? through '
    rf'(?P<m2>{MONTH}) (?P<d2>\d{{1,2}}), (?P<y2>\d{{4}})\b', re.IGNORECASE)
TEMPORAL = re.compile(
    rf'\b(?:{MONTH}|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|'
    r'today|yesterday|tomorrow|tonight|last|previous|past|next|since|until|through|'
    r'ago|recent|recently|current|this|week|weeks|month|months|year|years|'
    r'quarter|quarters|fortnight|weekend|weekends|hour|hours|minute|minutes)\b|'
    r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b|\b\d+\s+days?\b|'
    r'今天|昨天|明天|最近|过去|上周|本周|上月|本月|今年|去年', re.IGNORECASE)
HINT = ('Use one window: the last N days (1-14), last week, previous week, '
        'or YYYY-MM-DD through YYYY-MM-DD (inclusive dates).')


def utc_now(clock=None):
    """Capture one aware instant, including clocks supplied in another timezone."""
    value = clock() if clock is not None else datetime.now(timezone.utc)
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError('Clock must return a timezone-aware datetime.')
    return value.astimezone(timezone.utc)


def mode():
    """Only the two explicit modes are accepted; absence preserves eval."""
    selected = os.environ.get('AGENT_MODE', 'eval')
    if selected not in ('eval', 'live'):
        raise ValueError('AGENT_MODE must be eval or live.')
    return selected


def switch_mode(state, selected):
    """Discard visible question/history when crossing a mode boundary."""
    if selected not in ('eval', 'live'):
        raise ValueError('AGENT_MODE must be eval or live.')
    previous = state.get('agent_mode', 'eval')
    if previous != selected:
        for key in ('question', 'demo_runs', 'last_demo'):
            state.pop(key, None)
    state['agent_mode'] = selected


def question_window(question, *, clock=None):
    """Parse documented forms; reject all recognized unsupported temporal syntax."""
    if not isinstance(question, str):
        raise ValueError('Question must be text. ' + HINT)
    today = utc_now(clock).date()
    matches = list(EXPRESSION.finditer(question))
    rest = list(question)
    bounds = []
    for match in matches:
        try:
            if match.group('n') is not None:
                count = int(match.group('n'))
                if not 1 <= count <= 14:
                    raise ValueError('N must be between 1 and 14.')
                start, end = today - timedelta(days=count), today
            elif match.group(0).lower() in ('last week', 'previous week'):
                end = today if match.group(0).lower() == 'last week' else today - timedelta(days=7)
                start = end - timedelta(days=7)
            else:
                if match.group('iso1'):
                    start = datetime.strptime(match.group('iso1'), '%Y-%m-%d').date()
                    final = datetime.strptime(match.group('iso2'), '%Y-%m-%d').date()
                else:
                    start = datetime(int(match.group('y1') or match.group('y2')),
                                     [m.lower() for m in MONTHS].index(match.group('m1').lower()) + 1,
                                     int(match.group('d1'))).date()
                    final = datetime(int(match.group('y2')),
                                     [m.lower() for m in MONTHS].index(match.group('m2').lower()) + 1,
                                     int(match.group('d2'))).date()
                end = final + timedelta(days=1)
                if start >= end:
                    raise ValueError('Explicit dates are reversed.')
                if end > today:
                    raise ValueError("Today's data is incomplete; use an inclusive end before today (UTC).")
                if end <= today - timedelta(days=14):
                    raise ValueError('Data has rolled out of retention; choose a range overlapping the preceding 14 complete UTC days.')
        except (ValueError, OverflowError) as error:
            raise ValueError(str(error) + ' ' + HINT) from None
        bounds.append((start.isoformat(), end.isoformat()))
        rest[match.start():match.end()] = ' ' * (match.end() - match.start())
    if TEMPORAL.search(''.join(rest)) or len(bounds) > 1:
        raise ValueError('Unsupported, malformed, or multiple time expressions. ' + HINT)
    return bounds[0] if bounds else None


def metric_lookup(glossary, term):
    """Read metric section verbatim from the original source; omit frozen rules."""
    match = re.search(r'^## 3\. Metric definitions\s*\n(.*?)(?=^## |\Z)', glossary, re.M | re.S)
    if match is None:
        raise ValueError('Metric definitions section is missing.')
    return lookup_glossary('## Metric definitions\n' + match.group(1), term)


def coverage(database=LIVE_DATABASE, *, clock=None):
    """Expose committed archive-hour gaps, not inferred zero-event coverage."""
    now = utc_now(clock)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start = today - timedelta(days=14)
    server = isolated_server(database)
    result = server.execute_select('SELECT source_file, ingested_at FROM ingest_log ORDER BY source_file',
                                   server.METADATA_TABLES, 400)
    if result.truncated:
        raise ValueError('Unexpected ingestion ledger size; coverage cannot be established.')
    hours = {datetime.strptime(name.removesuffix('.json.gz'), '%Y-%m-%d-%H').replace(tzinfo=timezone.utc)
             for name, _ in result.rows}
    expected = [start + timedelta(hours=i) for i in range(14 * 24)]
    missing = [h.isoformat() for h in expected if h not in hours]
    return {'retention_start': start.isoformat(), 'complete_days_end_exclusive': today.isoformat(),
            'missing_complete_day_hours': missing, 'complete_day_hours_ingested': len(expected) - len(missing),
            'last_ingested_at': max((stamp for _, stamp in result.rows), default=None),
            'caveat': 'Data is as of ingestion time. Missing or expired hours are unavailable, not verified zero activity. '
                      'Requested overlapping intervals are not clamped. Today is an ingestion buffer, excluded from windows.'}


async def live_date_context_for_question(question_text, session, glossary, *, clock=None, database=LIVE_DATABASE):
    """Build dynamic context without invoking the frozen static date builder."""
    now = utc_now(clock)
    window = question_window(question_text, clock=lambda: now)
    tables = {}
    for table in ('events', 'repos'):
        description = tool_payload(await session.call_tool('describe_table', arguments={'table': table}))
        sample = tool_payload(await session.call_tool('sample_values', arguments={'table': table}))
        tables[table] = {'columns': description['columns'], 'sample_rows': sample['rows']}
    metric_lookup(glossary, 'Metric definitions')  # Validate the source without copying definitions.
    payload = {'mode': 'live', 'reference_date': now.date().isoformat(), 'reference_instant': now.isoformat(),
               'time_conventions': 'UTC, half-open windows. Today is incomplete and excluded. Use injected literal dates. '
                                   'last week is the last 7 complete days; previous week is the preceding 7 days. '
                                   'Explicit end dates are inclusive. Never silently clamp a requested interval.',
               'repo_metadata': 'repo metadata frozen at 2026-10-22; original fetched_at values retained',
               'coverage': coverage(database, clock=lambda: now), 'tables': tables,
               'metric_source': 'Use lookup_glossary for metric definitions from the read-only glossary.'}
    result = 'LIVE CONTEXT\n' + json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if window:
        result += f'\nQuestion window: [{window[0]}, {window[1]})'
    return result
