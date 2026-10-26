"""Offline verification of real frozen legacy wiring and exploratory isolation."""

import asyncio
from contextlib import asynccontextmanager
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock

from mcp.types import CallToolResult, ListToolsResult, TextContent, Tool
import pytest

from eval import run_v4_ab as ab


@pytest.fixture(autouse=True)
def no_services(monkeypatch):
    from agent import loop
    import dotenv
    def forbidden(*args,**kwargs):raise AssertionError('Real service/credential access forbidden')
    monkeypatch.setattr(loop,'AsyncOpenAI',forbidden)
    monkeypatch.setattr(loop,'stdio_client',forbidden)
    monkeypatch.setattr(loop,'load_dotenv',forbidden)
    monkeypatch.setattr(dotenv,'dotenv_values',forbidden)


def response(sql='SELECT 2 AS value', calls=None):
    return NS(model='fake-model',choices=[NS(message=NS(content=sql,tool_calls=calls))],usage=NS(prompt_tokens=5,completion_tokens=2,total_tokens=7))


def submit(sql='SELECT 2 AS value'):
    return NS(id='submit-id',type='function',function=NS(name='submit_answer',arguments=json.dumps({'sql':sql})))


class Client:
    def __init__(self,responses):
        self.responses=iter(responses);self.requests=[]
        self.chat=NS(completions=NS(create=self.create))
    async def create(self,**kwargs):
        self.requests.append(deepcopy(kwargs));result=next(self.responses)
        if isinstance(result,Exception):raise result
        return result


class Session:
    def __init__(self,error=None):self.calls=[];self.error=error
    async def list_tools(self):
        return ListToolsResult(tools=[Tool(name='run_query',input_schema={'type':'object','properties':{'sql':{'type':'string'}}})])
    async def call_tool(self,name,arguments):
        self.calls.append((name,deepcopy(arguments)))
        if name=='run_query' and self.error:
            return CallToolResult(content=[TextContent(type='text',text=self.error)],is_error=True)
        payload={'columns':['value'],'rows':[[2]],'truncated':False,'elapsed_ms':1.0}
        return CallToolResult(content=[],structured_content=payload)


@pytest.mark.parametrize('config',['A','B'])
def test_wrapper_uses_actual_frozen_entry_and_preserves_all_original_trace_fields(config,tmp_path,monkeypatch):
    from eval import run_experiment as legacy
    glossary='FULL OFFLINE GLOSSARY';(tmp_path/'eval').mkdir();(tmp_path/'eval/glossary.md').write_text(glossary)
    monkeypatch.setattr(ab,'ROOT',tmp_path)
    monkeypatch.setattr(legacy,'c2_date_context',AsyncMock(side_effect=AssertionError('No C2 injection')))
    monkeypatch.setattr(legacy,'grade_run',lambda *a:pytest.fail('No grading'))
    sequence=[response()] if config=='A' else [response(None,[submit()]),response('Done')]
    direct_client,wrapped_client=Client(deepcopy(sequence)),Client(deepcopy(sequence))
    direct_session,wrapped_session=Session(),Session()
    async def direct():
        shared=await legacy.shared_context(direct_session)
        return await legacy.run_config(config,direct_client,direct_session,'question',shared,glossary,'dummy-key')
    expected=asyncio.run(direct())
    got=asyncio.run(ab.legacy_trial({'id':'q','question':'question'},config,wrapped_client,wrapped_session,'dummy-key'))
    assert {k:got[k] for k in expected}==expected
    assert wrapped_client.requests==direct_client.requests and wrapped_session.calls==direct_session.calls
    assert len(got['legacy_api_trace'])==(1 if config=='A' else 2)
    assert got['harness_version']==ab.HARNESS and got['api_retry_count']==0
    assert all('FULL GLOSSARY\n'+glossary in r['messages'][0]['content'] for r in wrapped_client.requests)
    assert all('lookup_glossary' not in {t['function']['name'] for t in r.get('tools',[])} for r in wrapped_client.requests)


def test_failed_a_sql_and_errors_preserved_and_key_redacted(tmp_path,monkeypatch):
    (tmp_path/'eval').mkdir();(tmp_path/'eval/glossary.md').write_text('glossary')
    monkeypatch.setattr(ab,'ROOT',tmp_path)
    result=asyncio.run(ab.legacy_trial({'question':'question'},'A',Client([response('SELECT forbidden()')]),Session('Error executing tool run_query: dummy-key denied'),'dummy-key'))
    assert result['submitted'] is False and result['answer_sql'] is None
    assert result['legacy_tool_trace'][-1]['arguments']=={'sql':'SELECT forbidden()'}
    assert result['legacy_tool_trace'][-1]['result']['is_error'] is True
    assert 'dummy-key' not in json.dumps(result) and '[REDACTED]' in json.dumps(result)
    with pytest.raises(ValueError):asyncio.run(ab.legacy_trial({'question':'q'},'C',None,None,''))


def test_capture_client_api_failure_and_no_retry():
    from openai import APIConnectionError
    import httpx2 as httpx
    error=APIConnectionError(request=httpx.Request('POST','https://offline.invalid'),message='dummy-key disconnected')
    raw=Client([error]);proxy=ab.CaptureClient(raw,'dummy-key')
    with pytest.raises(APIConnectionError):asyncio.run(proxy.create(model='frozen',messages=[]))
    assert len(raw.requests)==1 and proxy.api_errors==1
    assert proxy.records[0]['error_type']=='APIConnectionError'
    assert 'dummy-key' not in json.dumps(proxy.records)


def test_capture_session_exception_and_setup_failure():
    session=NS(call_tool=AsyncMock(side_effect=RuntimeError('dummy-key tool failure')))
    proxy=ab.CaptureSession(session,'dummy-key')
    with pytest.raises(RuntimeError):asyncio.run(proxy.call_tool('run_query',{'sql':'SELECT 1'}))
    assert proxy.records[0]['error_message']=='[REDACTED] tool failure'
    result=asyncio.run(ab.legacy_trial({'question':'q'},'A',object(),session,'dummy-key'))
    assert result['status']=='transport_error' and result['legacy_tool_trace']
    assert 'dummy-key' not in json.dumps(result)


def test_live_transport_fresh_and_setup_error_sanitized(monkeypatch):
    from agent import loop
    session=NS(initialize=AsyncMock());client=object();seen=[]
    @asynccontextmanager
    async def managed(value):yield value
    def factory(**kwargs):seen.append(kwargs);return managed(client)
    monkeypatch.setattr(loop,'AsyncOpenAI',factory)
    monkeypatch.setattr(loop,'get_default_environment',lambda:{})
    monkeypatch.setattr(loop,'stdio_client',lambda p:managed(('r','w')))
    monkeypatch.setattr(loop,'ClientSession',lambda *a,**k:managed(session))
    trial=AsyncMock(return_value={'status':'completed'});monkeypatch.setattr(ab,'legacy_trial',trial)
    assert asyncio.run(ab.live_trial({'question':'q'},'A','dummy-key'))=={'status':'completed'}
    assert seen[0]=={'api_key':'dummy-key','base_url':'https://api.deepseek.com','max_retries':0,'timeout':60.0}
    session.initialize.assert_awaited_once()
    session.initialize=AsyncMock(side_effect=RuntimeError('dummy-key setup failure'))
    failed=asyncio.run(ab.live_trial({'question':'q'},'B','dummy-key'))
    assert failed['status']=='transport_error' and 'dummy-key' not in json.dumps(failed)


def test_hash_and_verify_existing_ledgers(tmp_path,monkeypatch):
    p=tmp_path/'f';p.write_text('frozen');digest=hashlib.sha256(p.read_bytes()).hexdigest()
    monkeypatch.setattr(ab,'PROTECTED',{'f':(digest,'existing-ledger')})
    assert ab.verify_frozen(tmp_path)=={'f':digest}
    p.write_text('changed')
    with pytest.raises(ValueError,match='Frozen mismatch'):ab.verify_frozen(tmp_path)


def test_load_questions_sorted_unique_and_snapshot_guard(tmp_path):
    p=tmp_path/'eval/v4_questions.jsonl';p.parent.mkdir()
    qs=[{'record_type':'question','id':f'q{i:03}','snapshot_sha256':ab.PROTECTED['data/github.duckdb'][0]} for i in reversed(range(300))]
    p.write_text(''.join(json.dumps(q)+'\n' for q in qs))
    assert ab.load_questions(tmp_path)[0]['id']=='q000'
    qs[0]['snapshot_sha256']='bad';p.write_text(''.join(json.dumps(q)+'\n' for q in qs))
    with pytest.raises(ValueError,match='snapshot'):ab.load_questions(tmp_path)
    p.write_text('{}\n')
    with pytest.raises(ValueError,match='300'):ab.load_questions(tmp_path)


def test_collect_strict_order_complete_raw_failures_resume_and_blind_stdout(tmp_path,capsys):
    path=tmp_path/'ab.jsonl';questions=[{'id':'q2'},{'id':'q1'}];seen=[]
    async def trial(q,c):
        seen.append((q['id'],c))
        if c=='A':raise RuntimeError('PRIVATE DETAILS')
        return {'status':'completed','answer_sql':'PRIVATE SQL','answer_rows':[[3]],'submitted':True,'tool_calls':[{'original':'trace'}]}
    assert asyncio.run(ab.collect(questions,trial,path,clock=lambda:100))==4
    assert seen==[('q1','A'),('q1','B'),('q2','A'),('q2','B')]
    before=path.read_bytes()
    assert asyncio.run(ab.collect(questions,AsyncMock(side_effect=AssertionError('rerun')),path))==4
    assert path.read_bytes()==before
    _,records=ab.history(path.read_text(),questions)
    assert records[('q1','A')]['status']=='transport_error'
    assert records[('q1','B')]['tool_calls']==[{'original':'trace'}]
    assert all(line.startswith('Completed pairs: ') for line in capsys.readouterr().out.splitlines())


@pytest.mark.parametrize('fault',['duplicate','foreign','pass','harness','torn','record_type'])
def test_history_rejects_bad_records(fault):
    row={'record_type':'trial','question_id':'q','config':'A','pass':1,'harness_version':ab.HARNESS}
    if fault=='foreign':row['config']='C'
    if fault=='pass':row['pass']=2
    if fault=='harness':row['harness_version']='c2.1'
    if fault=='record_type':row['record_type']='unknown'
    text=json.dumps(row)+'\n'
    if fault=='duplicate':text+=text
    if fault=='torn':text=text.rstrip()
    with pytest.raises(ValueError):ab.history(text,[{'id':'q'}])


def test_concurrent_collectors_block_before_duplicate_requests(tmp_path):
    async def scenario():
        started=asyncio.Event();release=asyncio.Event();calls=[]
        async def trial(q,c):calls.append(c);started.set();await release.wait();return {}
        path=tmp_path/'ab.jsonl';qs=[{'id':'q'}]
        first=asyncio.create_task(ab.collect(qs,trial,path))
        await started.wait()
        with pytest.raises(BlockingIOError):await ab.collect(qs,trial,path)
        release.set();assert await first==2
        assert calls==['A','B']
    asyncio.run(scenario())


def test_paths_duplicate_questions_and_long_gap_block(tmp_path):
    trial=AsyncMock(return_value={})
    with pytest.raises(ValueError):asyncio.run(ab.collect([],trial,ab.RESULTS))
    with pytest.raises(ValueError):asyncio.run(ab.collect([],trial,tmp_path/'bad',offline=False))
    with pytest.raises(ValueError):asyncio.run(ab.collect([{'id':'q'},{'id':'q'}],trial,tmp_path/'bad'))
    p=tmp_path/'gap';row={'record_type':'trial','question_id':'q','config':'A','pass':1,'block':1,'recorded_at':10,'harness_version':ab.HARNESS}
    p.write_text(json.dumps(row)+'\n')
    assert asyncio.run(ab.collect([{'id':'q'}],trial,p,clock=lambda:7211))==2
    rows,records=ab.history(p.read_text(),[{'id':'q'}])
    assert rows[1]['reason']=='interruption_over_two_hours' and records[('q','B')]['block']==2


def test_describe_only_complete_precomputed_rows_no_database(monkeypatch):
    from agent import mcp_server
    monkeypatch.setattr(mcp_server,'execute_select',lambda *a:pytest.fail('No SQL execution'))
    qs=[{'id':'q','layer':'window','bounds':['2026-10-15','2026-10-22'],'reference_columns':['value'],'reference_rows':[[2]]}]
    with pytest.raises(ValueError,match='terminal'):ab.describe(qs,{})
    good={'status':'completed','submitted':True,'answer_sql':"SELECT 2 FROM events WHERE created_at >= '2026-10-15' AND created_at < '2026-10-22'",'answer_columns':['value'],'answer_rows':[[2]],'response_models':['fake']}
    records={('q','A'):good,('q','B'):{**good,'submitted':False}}
    text=ab.describe(qs,records)
    assert 'Exploratory, not pre-registered; results MUST NOT be merged into v4 confirmatory conclusions.' in text
    assert '1/1 (100.00%) | 0/1 (0.00%)' in text and 'unparseable' in text


def test_score_complete_writes_only_new_report(tmp_path,monkeypatch):
    qs=[{'id':'q','layer':'control','bounds':None,'reference_columns':['v'],'reference_rows':[[1]]}]
    monkeypatch.setattr(ab,'verify_frozen',lambda root=None:{})
    monkeypatch.setattr(ab,'load_questions',lambda root=None:qs)
    p=tmp_path/'eval/results/runs_v4_ab_exploratory.jsonl';p.parent.mkdir(parents=True)
    rows=[{'record_type':'trial','question_id':'q','config':c,'pass':1,'harness_version':ab.HARNESS,'status':'error','submitted':False} for c in ab.CONFIGS]
    p.write_text(''.join(json.dumps(r)+'\n' for r in rows));before=p.read_bytes()
    report=ab.score_complete(tmp_path)
    assert report==tmp_path/'eval/v4_ab_exploratory.md' and p.read_bytes()==before


def test_main_explicit_modes_substituted_credentials_and_execution(tmp_path,monkeypatch):
    import dotenv
    monkeypatch.setattr(ab,'verify_frozen',lambda:{})
    report=tmp_path/'report';report.write_text('report')
    monkeypatch.setattr(ab,'score_complete',lambda:report)
    assert ab.main(['--score'])==0
    with pytest.raises(SystemExit):ab.main([])
    monkeypatch.setattr(dotenv,'dotenv_values',lambda path:{'DEEPSEEK_API_KEY':'dummy-key'})
    monkeypatch.setattr(ab,'load_questions',lambda:[{'id':'q'}])
    collect=AsyncMock(return_value=2);monkeypatch.setattr(ab,'collect',collect)
    assert ab.main(['--execute'])==0 and collect.call_args.kwargs['offline'] is False
