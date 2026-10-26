"""Exploratory legacy A/B collection, then explicitly gated offline description."""

import argparse
import asyncio
from contextlib import redirect_stderr
from copy import deepcopy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'eval/results/runs_v4_ab_exploratory.jsonl'
REPORT = ROOT / 'eval/v4_ab_exploratory.md'
CONFIGS = ('A', 'B')
HARNESS = 'legacy-ab-53121bb04092'
# Existing published ledgers, not a replacement baseline.
PROTECTED = {
    'agent/loop.py': ('53121bb040921547e87583aa23b234f68bef320a6703f29b0477fc3884c90f93', 'eval/c3_on_v2.md'),
    'eval/run_experiment.py': ('d9a2ffc5c419b22d9d47dceefe13bc15ccf6a8005ccfb4400853afd443c79465', 'eval/c3_on_v2.md'),
    'agent/mcp_server.py': ('3b55d233b1f8f27c1398df53a75065a456456e97219ac2607e9eb03d44b4d41f', 'eval/c3_on_v2.md'),
    'eval/grader.py': ('34fdf04fb0a75836f78a0e2ec4c90fef4d9b7b5f6c4cab730b00abcbe502dd57', 'eval/c3_on_v2.md'),
    'agent/error_feedback.py': ('68fbbafdc74a7902ea4c12a6c92cb525fc6daff5ee50a9a2c4d514df90cdf230', 'eval/c3_on_v2.md'),
    'agent/context.py': ('72367ec27f81eda96a65dfa7c908f3f143bea922ed1f1d28ec7a1b2bb29a9ee4', 'eval/v4_c21_change.md'),
    'eval/glossary.md': ('1a2ce44850529108249fe9970803b1745787ecf37c63136a062a11bb808c3d05', 'eval/c3_on_v2.md'),
    'eval/v4_questions.jsonl': ('829ec0475c1ba1c090c8b1926221124df092af8b35b81ccc2a0a92e1fa897dc1', 'eval/v4_preregister.md'),
    'data/github.duckdb': ('2a063cab4176b97cfd00ea8e92932c64346127ba1da4b120452fb48236c25812', 'eval/v4_preregister.md'),
    'eval/score_v4.py': ('95a0f4ec4ccf5e3f4f501a2ff24e5fd001a35b142b22f01c1b0ea728616e3c1d', 'Phase D completion ledger'),
    'eval/run_v4.py': ('80d0f9f67d427842ef3b9f9e6e220eedcc11279ef63307cfb0a61453f11b7a51', 'eval/v4_preregister.md'),
    'eval/v4_sql_bounds.py': ('331fa061ba46bb4cf53c52102eeddd3d0e423a557b3328469e0edbc34f32805f', 'eval/v4_preregister.md'),
    'eval/results/runs_v4.jsonl': ('b08c2881f8253d8d1e7d65b849f4fcd76499a2b0d467afe0a7f74140e7832240', 'Phase C completion ledger'),
    'eval/results/runs_v4_pass2.jsonl': ('8ff2597534c7459349107c0a55e8819f9c3b96f7a31700083ddddd59c44156a3', 'Phase C completion ledger'),
    'eval/v4_report.md': ('6d0555e8c513767983af96a9379e5c86923bfd714f0819e7950082b866ff2ca2', 'Phase D completion ledger'),
}


def sha256(path):
    """Hash bytes without executing SQL or touching credentials."""
    with Path(path).open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def verify_frozen(root=ROOT):
    """Fail closed against existing authoritative ledgers before collection/scoring."""
    actual = {}
    for name, (expected, ledger) in PROTECTED.items():
        actual[name] = sha256(Path(root) / name)
        if actual[name] != expected:
            raise ValueError(f'Frozen mismatch: {name}; ledger {ledger}')
    return actual


def load_questions(root=ROOT):
    """Read the frozen question universe in strict question_id order."""
    rows = [json.loads(line) for line in (Path(root)/'eval/v4_questions.jsonl').read_text().splitlines()]
    questions = sorted((r for r in rows if r.get('record_type') == 'question'), key=lambda r:r['id'])
    if len(questions) != 300 or len({q['id'] for q in questions}) != 300:
        raise ValueError('Expected 300 unique frozen questions')
    if any(q['snapshot_sha256'] != PROTECTED['data/github.duckdb'][0] for q in questions):
        raise ValueError('Per-question snapshot hash mismatch')
    return questions


class CaptureClient:
    """Transparent protocol capture; excludes credentials and private reasoning fields."""

    def __init__(self, client, key):
        self.client, self.key = client, key
        self.records, self.models = [], []
        self.api_errors = 0
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    async def create(self, **kwargs):
        from agent.loop import sanitize
        from openai import APIError
        entry = {'request': sanitize(deepcopy(kwargs), self.key)}
        self.records.append(entry)
        try:
            response = await self.client.chat.completions.create(**kwargs)
        except Exception as error:
            self.api_errors += isinstance(error, APIError)
            entry.update(error_type=type(error).__name__, error_message=sanitize(str(error), self.key))
            raise
        self.models.append(getattr(response,'model',None))
        choices=[]
        for choice in response.choices:
            message=choice.message
            choices.append({'content':message.content, 'tool_calls':[
                {'id':c.id,'type':c.type,'function':{'name':c.function.name,'arguments':c.function.arguments}}
                for c in (message.tool_calls or [])]})
        entry['response'] = sanitize({'model':getattr(response,'model',None),'choices':choices,
                                     'usage':None if response.usage is None else {
                                         k:getattr(response.usage,k,None) for k in ('prompt_tokens','completion_tokens','total_tokens')}},self.key)
        return response


class CaptureSession:
    """Preserve original MCP outcomes, including A's failed query text, without edits."""

    def __init__(self, session, key):
        self.session, self.key, self.records = session, key, []

    async def list_tools(self):
        return await self.session.list_tools()

    async def call_tool(self, name, arguments):
        from agent.loop import sanitize
        entry={'name':name,'arguments':sanitize(deepcopy(arguments),self.key)}
        self.records.append(entry)
        try:
            result=await self.session.call_tool(name,arguments=arguments)
        except Exception as error:
            entry.update(error_type=type(error).__name__,error_message=sanitize(str(error),self.key))
            raise
        entry['result']=sanitize({'is_error':result.is_error,'structured_content':result.structured_content,
                                  'content':[{'type':b.type,'text':b.text} for b in result.content if b.type=='text']},self.key)
        return result


async def legacy_trial(question, config, client, session, key):
    """Call the real frozen run_config; do not reimplement baseline or bounded loop."""
    from agent import loop
    from eval.run_experiment import run_config, shared_context, REFERENCE_DATE
    if config not in CONFIGS:
        raise ValueError('Only legacy A/B is authorized')
    proxy, observed = CaptureClient(client,key), CaptureSession(session,key)
    trace=loop.new_trace(question['question'],REFERENCE_DATE)
    try:
        shared=await shared_context(observed)
        glossary=(ROOT/'eval/glossary.md').read_text()
        trace=await run_config(config,proxy,observed,question['question'],shared,glossary,key)
    except Exception as error:
        trace.update(status='transport_error',final_answer=f'{type(error).__name__}: {loop.sanitize(str(error),key)}')
    return loop.sanitize({**trace,'response_models':proxy.models,'api_error_count':proxy.api_errors,
                          'api_retry_count':0,'legacy_api_trace':proxy.records,'legacy_tool_trace':observed.records,
                          'harness_version':HARNESS},key)


async def live_trial(question, config, key):
    """Explicit authorized network transport with fresh client/session for every trial."""
    import sys
    from agent import loop
    from agent.context import REFERENCE_DATE
    trace=loop.new_trace(question['question'],REFERENCE_DATE)
    try:
        parameters=loop.StdioServerParameters(command=sys.executable,args=['-B',str(ROOT/'agent/mcp_server.py')],
                                              cwd=str(ROOT),env=loop.get_default_environment())
        async with loop.AsyncOpenAI(api_key=key,base_url='https://api.deepseek.com',max_retries=0,timeout=60.0) as client:
            async with loop.stdio_client(parameters) as (reader,writer):
                async with loop.ClientSession(reader,writer,read_timeout_seconds=20) as session:
                    await session.initialize()
                    return await legacy_trial(question,config,client,session,key)
    except Exception as error:
        return loop.sanitize({**trace,'status':'transport_error','final_answer':f'{type(error).__name__}: {str(error)}',
                              'response_models':[],'api_error_count':0,'api_retry_count':0,
                              'legacy_api_trace':[],'legacy_tool_trace':[],'harness_version':HARNESS},key)


def history(text, questions):
    """Validate first-write-wins identities and retain terminal failures unchanged."""
    if text and not text.endswith('\n'):
        raise ValueError('Torn result record: manual recovery required; do not rerun')
    rows=[json.loads(line) for line in text.splitlines()]
    required={(q['id'],c) for q in questions for c in CONFIGS}
    records={}
    for row in rows:
        if row.get('record_type') not in ('block','trial') or row.get('harness_version') != HARNESS:
            raise ValueError('Unexpected exploratory record type/version')
        if row['record_type']=='trial':
            pair=(row['question_id'],row['config'])
            if pair not in required or pair in records or row.get('pass') != 1:
                raise ValueError('Duplicate/foreign exploratory identity')
            records[pair]=row
    return rows,records


def append_record(output, row):
    """Durably append under the collector's process-wide exclusive file lock."""
    output.seek(0,2)
    output.write(json.dumps(row,ensure_ascii=False,allow_nan=False,sort_keys=True)+'\n')
    output.flush();os.fsync(output.fileno())


async def collect(questions, trial, path, *, offline=True, clock=time.time):
    """One sequential worker, sorted questions, A then B; no implicit scoring."""
    path=Path(path)
    if offline and path.resolve().is_relative_to((ROOT/'eval/results').resolve()):
        raise ValueError('Offline fixtures cannot write formal results')
    if not offline and path.resolve()!=RESULTS.resolve():
        raise ValueError('Only the exploratory result path is authorized')
    if len({q['id'] for q in questions})!=len(questions):
        raise ValueError('Duplicate input question')
    questions=sorted(questions,key=lambda q:q['id'])
    path.parent.mkdir(parents=True,exist_ok=True)
    # A nonblocking whole-run lock prevents a second collector making duplicate API requests.
    with path.open('a+',encoding='utf-8') as output:
        fcntl.flock(output.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        try:
            output.seek(0);rows,completed=history(output.read(),questions)
            total=len(questions)*2
            if len(completed)==total:
                print(f'Completed pairs: {total}/{total}',flush=True);return total
            now=clock()
            block=max((r['block'] for r in rows),default=0)
            if not rows or now-max(r['recorded_at'] for r in rows)>7200:
                block+=1
                append_record(output,{'record_type':'block','block':block,'recorded_at':now,
                                      'reason':'initial' if not rows else 'interruption_over_two_hours','harness_version':HARNESS})
            for question in questions:
                for config in CONFIGS:
                    if (question['id'],config) in completed:continue
                    started=clock()
                    try:
                        trace=await trial(question,config)
                    except Exception as error:
                        # Live transport owns sanitization and full traces. This outer fallback
                        # retains an offline/collector exception type without exposing its text.
                        trace={'status':'transport_error','submitted':False,'answer_sql':None,
                               'final_answer':type(error).__name__,'api_error_count':0,'api_retry_count':0,
                               'response_models':[],'tool_calls':[],'legacy_api_trace':[],'legacy_tool_trace':[]}
                    record={**trace,'record_type':'trial','question_id':question['id'],'config':config,'pass':1,
                            'worker':0,'block':block,'started_at':started,'recorded_at':clock(),'harness_version':HARNESS}
                    append_record(output,record);completed[(question['id'],config)]=record
                    print(f'Completed pairs: {len(completed)}/{total}',flush=True)
            return len(completed)
        finally:
            fcntl.flock(output.fileno(),fcntl.LOCK_UN)


def describe(questions, records):
    """Score only a complete collection using the unchanged frozen v4 row logic."""
    required={(q['id'],c) for q in questions for c in CONFIGS}
    if set(records)!=required:
        raise ValueError('All trials must be terminal before any scoring')
    from collections import Counter
    from eval.score_v4 import grade_rows, submitted_sql
    from eval.v4_sql_bounds import analyze_sql
    lines=['# v4 legacy A/B exploratory results','','Exploratory, not pre-registered; results MUST NOT be merged into v4 confirmatory conclusions.','',
           '## Frozen code and collection','',
           'The clean-worktree gate passed before new files were created. All required hashes matched existing published ledgers. A/B call the actual frozen eval.run_experiment.run_config entry: full glossary for both, original one-shot for A, original bounded loop for B, with no lookup_glossary. No C-family trial is run. Historical v2 production-time uncommitted state remains unverifiable; this is reuse of the identified current frozen legacy paths, not a claim of recovered historical provider state.','',
           f'Harness identifier: `{HARNESS}`; it identifies the frozen loop content, not a historical run-record label. Strict sorted question_id order; A then B; one worker; every trial has a fresh client/session/conversation. First-write-wins includes terminal failures. No outcome was scored before all 600 records landed.','',
           '| File | SHA-256 | Existing ledger |','| --- | --- | --- |']
    lines += [f'| {name} | {digest} | {ledger} |' for name,(digest,ledger) in PROTECTED.items()]
    lines += ['','## Descriptive row-set accuracy','','| Stratum | n | A | B |','| --- | --- | --- | --- |']
    verdict={(q['id'],c):grade_rows(q,records[(q['id'],c)]) for q in questions for c in CONFIGS}
    for layer in ('all','window','advanced_sql','control'):
        selected=[q for q in questions if layer=='all' or q['layer']==layer]
        cells=[]
        for c in CONFIGS:
            n=sum(verdict[(q['id'],c)] is None for q in selected)
            cells.append(f'{n}/{len(selected)} ({100*n/len(selected):.2f}%)' if selected else '0/0')
        lines.append(f"| {layer} | {len(selected)} | {' | '.join(cells)} |")
    lines += ['','## Boundary classifications and non-submission','','| Config | Window n | No final SQL | Correct | start_wrong | end_wrong | both_wrong | no_window_predicate | unparseable | All-strata no submission |','| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for c in CONFIGS:
        windows=[q for q in questions if q['layer']=='window'];categories=Counter();missing=0
        for q in windows:
            sql=submitted_sql(records[(q['id'],c)])
            if sql is None:missing+=1
            else:categories[analyze_sql(sql,q['bounds'])['classification']]+=1
        counts=[categories[k] for k in ('correct','start_wrong','end_wrong','both_wrong','no_window_predicate','unparseable')]
        no_submit=sum(records[(q['id'],c)].get('submitted') is not True for q in questions)
        lines.append('| '+' | '.join(map(str,[c,len(windows),missing,*counts,no_submit]))+' |')
    lines += ['','Boundary counts use the frozen parser on committed final SQL only. No final SQL is excluded, never counted as correct. Unparseable is not proof of a semantic boundary error. No parser repair, gold reconstruction, reference-SQL execution, hypothesis test, or confirmatory comparison is performed. All row scores use the same precomputed reference rows and unchanged score_v4.grade_rows logic.','',
              '## Collection health and trace limits','','| Config | Terminal trials | API errors | API retries | Response models |','| --- | --- | --- | --- | --- |']
    for c in CONFIGS:
        rs=[r for (qid,cfg),r in records.items() if cfg==c]
        models=Counter(m for r in rs for m in r.get('response_models',[]))
        lines.append(f"| {c} | {len(rs)} | {sum(r.get('api_error_count',0) for r in rs)} | {sum(r.get('api_retry_count',0) for r in rs)} | {dict(models)} |")
    lines += ['','Original legacy traces are retained with additive legacy_api_trace/legacy_tool_trace protocol capture. This captures failed one-shot SQL without changing answer_sql or treating an attempted query as a submission. Request/response protocol content and MCP outcomes are preserved with key redaction; SDK-private reasoning and authentication headers are not captured. The trial fields match the v4 record envelope (pass=1, worker=0, block/time/harness), in a separate exploratory file.','',
              'A process crash after an external request but before durable recording cannot prove exactly-once external execution. Such an uncertain interrupted trial requires manual examination before resume; no blind retry is authorized. A second concurrent collector is rejected before any trial. Recorded failures are never retried.','']
    return '\n'.join(lines)


def score_complete(root=ROOT):
    """Explicit post-collection action, writing only the exploratory report."""
    root=Path(root);verify_frozen(root);questions=load_questions(root)
    path=root/'eval/results/runs_v4_ab_exploratory.jsonl'
    _,records=history(path.read_text(),questions)
    report=describe(questions,records)
    target=root/'eval/v4_ab_exploratory.md'
    target.write_text(report,encoding='utf-8')
    return target


def main(argv=None):
    """No implicit network or scoring; the user explicitly selects either phase."""
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--execute',action='store_true');mode.add_argument('--score',action='store_true')
    args=parser.parse_args(argv)
    verify_frozen()
    if args.score:
        path=score_complete();print(f'Exploratory report: {path}; SHA-256 {sha256(path)}');return 0
    from dotenv import dotenv_values
    key=(dotenv_values(ROOT/'.env').get('DEEPSEEK_API_KEY') or '').strip()
    if not key:raise ValueError('No existing API credential')
    questions=load_questions()
    async def trial(question,config):
        return await live_trial(question,config,key)
    # Preserve error messages in redacted trace fields, never print SQL or judgments.
    with open(os.devnull,'w') as sink, redirect_stderr(sink):
        asyncio.run(collect(questions,trial,RESULTS,offline=False))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
