"""Offline live contracts: temporary databases, injected clocks, no real services."""
import asyncio
from contextlib import asynccontextmanager
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import gzip
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import duckdb
from mcp.types import CallToolResult, ListToolsResult, Tool
import pytest
from streamlit.testing.v1 import AppTest
from agent import context, live_context as lc, live_server as ls, loop, mcp_server, run_mode
from scripts import ingest_live as ingest
from ui import app

NOW = datetime(2026, 11, 1, 12, 30, tzinfo=timezone.utc)
GLOSSARY = (lc.ROOT / 'eval/glossary.md').read_text()

@pytest.fixture(autouse=True)
def offline_only(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Real network, credentials, and model transports are forbidden')
    import dotenv
    monkeypatch.setattr(ingest.requests, 'get', forbidden)
    monkeypatch.setattr(dotenv, 'dotenv_values', forbidden)
    for name in ('AsyncOpenAI', 'stdio_client', 'load_dotenv'):
        monkeypatch.setattr(loop, name, forbidden)
    monkeypatch.delenv('AGENT_MODE', raising=False)
    monkeypatch.setenv('DEEPSEEK_API_KEY', 'offline-fake-key')

@pytest.fixture
def catalog(tmp_path):
    source, repos, target = tmp_path/'catalog.duckdb', tmp_path/'repos.txt', tmp_path/'github_live.duckdb'
    names = [f'owner/repo{i:03}' for i in range(100)]
    repos.write_text('\n'.join(names)+'\n')
    with duckdb.connect(str(source)) as db:
        db.execute('CREATE TABLE repos (repo_id BIGINT PRIMARY KEY, name TEXT, language TEXT, topics TEXT, stars BIGINT, forks BIGINT, open_issues BIGINT, created_at TIMESTAMP, fetched_at TIMESTAMP)')
        db.executemany('INSERT INTO repos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       [(i+1, name, 'Python', '[]', 1, 2, 3, '2020-01-01', '2026-10-22 03:00:00') for i,name in enumerate(names)])
    return source,repos,target

def archive_fetch(events=None, failures=()):
    calls=[]
    def fetch(hour,target):
        calls.append(hour)
        if hour in failures: raise OSError('offline archive unavailable')
        with gzip.open(target,'wt') as output:
            for event in (events or {}).get(hour,[]): output.write(json.dumps(event)+'\n')
    return fetch,calls

def event(id,created):
    return {'id':id,'repo':{'id':1,'name':'owner/repo000'},'type':'WatchEvent',
            'actor':{'login':'actor'},'created_at':created.isoformat(),'payload':{}}

def populate(catalog,*,now=NOW,events=None,failures=()):
    source,repos,target=catalog
    fetch,calls=archive_fetch(events,failures)
    result=ingest.ingest(database=target,catalog=source,repos_file=repos,clock=lambda:now,fetch=fetch)
    return result,calls

@pytest.mark.parametrize('instant,expected',[
 ('2026-11-01T00:01:00+00:00',('2026-10-25','2026-11-01')),
 ('2026-11-01T23:59:00-07:00',('2026-10-26','2026-11-02')),
 ('2027-01-01T00:30:00+08:00',('2026-12-24','2026-12-31'))])
def test_clock_timezone_month_and_year_boundaries(instant,expected):
    assert lc.question_window('Count events for the last 7 days',clock=lambda:datetime.fromisoformat(instant))==expected

@pytest.mark.parametrize('phrase,start,end',[
 ('the last 1 days','2026-10-31','2026-11-01'),
 ('the last 14 days','2026-10-18','2026-11-01'),
 ('last week','2026-10-25','2026-11-01'),
 ('previous week','2026-10-18','2026-10-25'),
 ('October 12 through October 24, 2026','2026-10-12','2026-10-25'),
 ('2026-10-12 through 2026-10-24','2026-10-12','2026-10-25'),
 ('October 30, 2026 through October 31, 2026','2026-10-30','2026-11-01'),
 ('October 31 through October 31, 2026','2026-10-31','2026-11-01')])
def test_authorized_windows_preserve_overlap_without_clamping(phrase,start,end):
    assert lc.question_window('Count events for '+phrase,clock=lambda:NOW)==(start,end)

@pytest.mark.parametrize('now,phrase,message',[
 (NOW,'October 31 through November 1, 2026',"Today's data is incomplete"),
 (datetime(2027,2,1,tzinfo=timezone.utc),'2027-01-31 through 2027-02-02',"Today's data is incomplete"),
 (NOW,'September 30 through October 1, 2026','rolled out of retention'),
 (datetime(2027,2,1,tzinfo=timezone.utc),'December 31, 2026 through January 1, 2027','rolled out of retention'),
 (NOW,'yesterday','Unsupported'),
 (datetime(2027,2,1,tzinfo=timezone.utc),'since January 31, 2027','Unsupported'),
 (NOW,'the last 0 days','N must'),(NOW,'the last 15 days','N must'),
 (NOW,'2026-10-32 through 2026-10-31','Use one window'),
 (NOW,'2026-10-30 through 2026-10-29','reversed'),
 (NOW,'last week and previous week','multiple'),(NOW,'past two weeks','Unsupported')])
def test_rejection_rules_have_actionable_hints(now,phrase,message):
    with pytest.raises(ValueError,match=message):lc.question_window(phrase,clock=lambda:now)
    with pytest.raises(ValueError,match='Use one window'):lc.question_window(phrase,clock=lambda:now)

def test_non_temporal_bad_clock_and_metric_only_source():
    assert lc.question_window('List repository languages',clock=lambda:NOW) is None
    with pytest.raises(ValueError,match='timezone-aware'):lc.utc_now(lambda:datetime(2026,1,1))
    with pytest.raises(ValueError,match='text'):lc.question_window(None)
    for term in ('new_stars','collaboration_events','active_contributors'):
        assert lc.metric_lookup(GLOSSARY,term)==context.lookup_glossary(GLOSSARY,term)
    for term in ('Time conventions','Dataset scope','reference_date'):
        assert '2026-10-22' not in lc.metric_lookup(GLOSSARY,term)
    with pytest.raises(ValueError,match='missing'):lc.metric_lookup('invalid','new_stars')

def test_ingestion_dedup_refresh_gaps_retention_and_catalog_preservation(catalog):
    source,repos,target=catalog;digest=hashlib.sha256(source.read_bytes()).hexdigest()
    hour=NOW.replace(hour=10,minute=0);gap=NOW.replace(hour=0,minute=0)-timedelta(days=5)
    rows={hour:[event('one',hour),event('one',hour),event('expired',NOW-timedelta(days=15))]}
    first,calls=populate(catalog,events=rows,failures=(gap,))
    assert len(calls)==348 and calls[-1]==NOW.replace(hour=11,minute=0)
    assert first['failed']==[{'hour':'2026-10-27-0.json.gz','error':'OSError'}]
    second,calls=populate(catalog,events={hour:[event('one',hour),event('late',hour)]})
    assert len(calls)==25 and gap in calls and len(set(calls))==25 and not second['failed']
    third,calls=populate(catalog,events={hour:[event('late',hour)]});assert len(calls)==24
    with duckdb.connect(str(target),read_only=True) as db:
        assert db.execute('SELECT event_id FROM events ORDER BY event_id').fetchall()==[('late',),('one',)]
        assert db.execute('SELECT COUNT(*), MIN(fetched_at), MAX(fetched_at) FROM repos').fetchone()==(100,datetime(2026,10,22,3),datetime(2026,10,22,3))
    info=lc.coverage(target,clock=lambda:NOW)
    assert info['missing_complete_day_hours']==[] and info['complete_day_hours_ingested']==336
    assert 'unavailable' in info['caveat'] and hashlib.sha256(source.read_bytes()).hexdigest()==digest
    _,calls=populate(catalog,now=NOW+timedelta(days=3));assert len(calls)==72
    with duckdb.connect(str(target),read_only=True) as db:
        assert db.execute('SELECT MIN(substr(source_file,1,10)) FROM ingest_log').fetchone()[0]=='2026-10-21'
    populate(catalog,now=NOW+timedelta(days=15))
    with duckdb.connect(str(target),read_only=True) as db:assert db.execute('SELECT COUNT(*) FROM events').fetchone()[0]==0

def test_corrupt_refresh_rolls_back_entire_hour_and_exposes_gaps(catalog):
    hour=NOW.replace(hour=0,minute=0)-timedelta(days=1)
    populate(catalog,events={hour:[event('original',hour)]})
    fetch,_=archive_fetch()
    def corrupt(h,target):
        if h==hour:
            with gzip.open(target,'wt') as output:
                output.write(''.join(json.dumps(event(f'must-rollback-{i}',h))+'\n' for i in range(1001)))
                output.write('invalid json\n')
        else:fetch(h,target)
    source,repos,target=catalog
    result=ingest.ingest(database=target,catalog=source,repos_file=repos,clock=lambda:NOW.replace(hour=0),fetch=corrupt)
    assert len(result['failed'])==1
    with duckdb.connect(str(target),read_only=True) as db:assert db.execute('SELECT event_id FROM events').fetchall()==[('original',)]
    with duckdb.connect(str(target)) as db:db.execute("DELETE FROM ingest_log WHERE source_file='2026-10-20-0.json.gz'")
    assert lc.coverage(target,clock=lambda:NOW)['missing_complete_day_hours']==['2026-10-20T00:00:00+00:00']

@pytest.mark.parametrize('kind',['direct','symlink','hardlink','wal_symlink','lock_symlink'])
def test_frozen_output_aliases_rejected_before_write(tmp_path,kind):
    frozen=tmp_path/'frozen.duckdb';frozen.write_bytes(b'protected');target=tmp_path/'github_live.duckdb'
    if kind=='direct':target=frozen
    elif kind=='symlink':target.symlink_to(frozen)
    elif kind=='hardlink':target.hardlink_to(frozen)
    else:Path(str(target)+('.wal' if kind=='wal_symlink' else '.ingest.lock')).symlink_to(frozen)
    with pytest.raises(ValueError):ls.live_path(target,frozen)
    assert frozen.read_bytes()==b'protected'

def test_ingest_bad_universe_catalog_and_concurrent_writer(catalog):
    import fcntl
    source,repos,target=catalog
    repos.write_text('owner/repo000\n')
    with pytest.raises(ValueError,match='100-repository'):populate(catalog)
    repos.write_text('\n'.join(f'wrong/repo{i}' for i in range(100)))
    with pytest.raises(ValueError,match='100 names'):populate(catalog)
    repos.write_text('\n'.join(f'owner/repo{i:03}' for i in range(100)))
    with Path(str(target)+'.ingest.lock').open('a') as lock:
        fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        with pytest.raises(BlockingIOError):populate(catalog)

def test_private_mcp_read_only_and_eval_globals_unchanged(catalog,monkeypatch):
    populate(catalog);original=mcp_server.DATABASE_PATH;server=ls.isolated_server(catalog[2])
    assert mcp_server.DATABASE_PATH==original
    assert server.execute_select.__code__.co_code==mcp_server.execute_select.__code__.co_code
    assert server.run_query('SELECT COUNT(*) AS n FROM repos').rows==[[100]]
    assert server.list_tables().tables==['events','ingest_log','repos']
    assert server.describe_table('events').columns[0].name=='event_id'
    for sql in ('DELETE FROM events',"SELECT * FROM read_csv('private.csv')",'SELECT * FROM ingest_log'):
        with pytest.raises(Exception):server.run_query(sql)
    with server.open_connection() as db:
        with pytest.raises(duckdb.Error):db.execute('DELETE FROM events')
    monkeypatch.setattr(ls,'live_path',lambda:catalog[2]);ran=[]
    monkeypatch.setattr(ls,'isolated_server',lambda path:SimpleNamespace(server=SimpleNamespace(run=lambda **kw:ran.append(kw))))
    ls.main();assert ran==[{'transport':'stdio'}]

class Session:
    async def initialize(self):pass
    async def list_tools(self):
        return ListToolsResult(tools=[Tool(name='run_query',input_schema={'type':'object','properties':{}})])
    async def call_tool(self,name,arguments):
        if name=='describe_table':payload={'columns':[{'name':'n','type':'BIGINT'}]}
        elif name=='sample_values':payload={'rows':[[1]]}
        else:payload={'columns':['n'],'rows':[[1]],'truncated':False,'elapsed_ms':0}
        return CallToolResult(content=[],structured_content=payload)
    async def __aenter__(self):return self
    async def __aexit__(self,*args):pass

class Client:
    def __init__(self,error=None):
        self.error=error
        self.requests=[];self.chat=SimpleNamespace(completions=SimpleNamespace(create=self.create))
    async def create(self,**kw):
        self.requests.append(deepcopy(kw))
        if self.error is not None:raise self.error
        calls=None if len(self.requests)>1 else [SimpleNamespace(id='submit',type='function',function=SimpleNamespace(name='submit_answer',arguments='{"sql":"SELECT 1 AS n"}'))]
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='Done',tool_calls=calls))],usage=SimpleNamespace(prompt_tokens=1,completion_tokens=1,total_tokens=2))
    async def __aenter__(self):return self
    async def __aexit__(self,*args):pass

def fake_transport(monkeypatch,client):
    session=Session();parameters=[]
    @asynccontextmanager
    async def stdio(p):
        parameters.append(p);assert 'DEEPSEEK_API_KEY' not in p.env
        yield None,None
    monkeypatch.setattr(loop,'stdio_client',stdio)
    monkeypatch.setattr(loop,'AsyncOpenAI',lambda **kw:client)
    monkeypatch.setattr(loop,'ClientSession',lambda *a,**kw:session)
    return parameters

def test_dynamic_context_has_no_frozen_temporal_instructions(catalog):
    populate(catalog)
    text=asyncio.run(lc.live_date_context_for_question('Count new_stars for October 12 through October 24, 2026',Session(),GLOSSARY,clock=lambda:NOW,database=catalog[2]))
    payload=json.loads(text.split('\n')[1])
    assert payload['reference_date']=='2026-11-01' and text.endswith('Question window: [2026-10-12, 2026-10-25)')
    assert payload['coverage']['retention_start'].startswith('2026-10-18')
    assert 'repo metadata frozen at 2026-10-22' in text
    assert 'Every question treats this date' not in text and 'SHARED STATIC CONTEXT' not in text

def test_live_transport_routes_to_live_and_rejects_before_credentials(catalog,monkeypatch):
    populate(catalog)
    invalid=asyncio.run(run_mode.run_live('Count events yesterday',clock=lambda:NOW,database=catalog[2]))
    assert invalid['trace']['status']=='error' and 'Unsupported' in invalid['trace']['final_answer']
    import dotenv
    monkeypatch.setattr(dotenv,'dotenv_values',lambda p:{'DEEPSEEK_API_KEY':'offline-fake-key'})
    monkeypatch.setattr(run_mode,'LIVE_DATABASE',catalog[2])
    client=Client();parameters=fake_transport(monkeypatch,client)
    result=asyncio.run(run_mode.run_live('Count new_stars for the last 7 days',clock=lambda:NOW,database=catalog[2]))
    assert result['trace']['submitted'] and result['trace']['mode']=='live'
    assert result['trace']['reference_date']=='2026-11-01'
    assert result['trace']['live_coverage']['complete_day_hours_ingested']==336
    assert parameters[0].args==['-B','-m','agent.live_server']
    assert 'Question window: [2026-10-25, 2026-11-01)' in client.requests[0]['messages'][0]['content']
    assert 'offline-fake-key' not in json.dumps(result)

@pytest.mark.parametrize('error',[None,RuntimeError('offline failure offline-fake-key')])
def test_eval_original_entry_byte_equivalence_and_live_file_independence(tmp_path,monkeypatch,error):
    monkeypatch.setattr(loop,'load_dotenv',lambda *a,**kw:None);monkeypatch.setattr(app,'perf_counter',lambda:100.0)
    namespace={};exec(LEGACY_RUN_DEMO,app.__dict__.copy(),namespace);old=namespace['run_demo']
    golden_client=Client(error);fake_transport(monkeypatch,golden_client);golden=asyncio.run(old('Count events'))
    (tmp_path/'github_live.duckdb').write_bytes(b'invalid live DB must never be opened in eval')
    monkeypatch.setattr(ls,'LIVE_DATABASE',tmp_path/'github_live.duckdb')
    for selected in (None,'eval'):
        if selected is None:monkeypatch.delenv('AGENT_MODE',raising=False)
        else:monkeypatch.setenv('AGENT_MODE',selected)
        client=Client(error);params=fake_transport(monkeypatch,client);current=asyncio.run(app.run_demo('Count events'))
        assert json.dumps(current,sort_keys=True)==json.dumps(golden,sort_keys=True)
        assert json.dumps(client.requests,sort_keys=True)==json.dumps(golden_client.requests,sort_keys=True)
        assert params[0].args[-1].endswith('agent/mcp_server.py')

def test_ui_mode_switch_isolation_and_visible_metadata_label(monkeypatch):
    test=AppTest.from_string('from ui.app import main; main()',default_timeout=15).run()
    test.text_area[0].set_value('eval question').run();test.session_state['last_demo']={'bad':'must disappear'}
    test.session_state['demo_runs']=[{'bad':'must disappear'}];monkeypatch.setenv('AGENT_MODE','live');test.run()
    assert not test.exception and 'repo metadata frozen at 2026-10-22' in test.warning[0].value
    assert test.text_area[0].value=='' and test.session_state['demo_runs']==[]
    test.button[0].click().run();assert 'the last 7 days' in test.text_area[0].value
    monkeypatch.setenv('AGENT_MODE','eval');test.run()
    assert test.warning[0].value==app.BANNER and test.text_area[0].value==''
    monkeypatch.setenv('AGENT_MODE','invalid')
    with pytest.raises(ValueError):lc.mode()
    with pytest.raises(ValueError):lc.switch_mode({},'invalid')

def test_mode_dispatch_and_cli_no_shared_trace_write(monkeypatch,capsys):
    calls=[]
    async def fake_live(question,on_update=None):
        calls.append(('live',question));return {'trace':{'status':'completed','reference_date':'2026-11-01'}}
    monkeypatch.setattr(run_mode,'run_live',fake_live);monkeypatch.setenv('AGENT_MODE','live')
    assert asyncio.run(app.run_demo('q'))['trace']['reference_date']=='2026-11-01'
    assert run_mode.main(['q'])==0
    async def fake_eval(question):
        calls.append(('eval',question));return {'trace':{'status':'completed','reference_date':'2026-10-22'}}
    monkeypatch.setattr(app,'run_demo',fake_eval);monkeypatch.setenv('AGENT_MODE','eval')
    assert run_mode.main(['q'])==0 and calls==[('live','q'),('live','q'),('eval','q')]
    assert '2026-10-22' in capsys.readouterr().out
    with pytest.raises(SystemExit):run_mode.main([' '])

def test_download_and_ingest_command_only_with_fake_io(tmp_path,monkeypatch,capsys):
    class Response:
        status_code=200;headers={'Content-Length':'3'}
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def raise_for_status(self):pass
        def iter_content(self,chunk_size):return iter([b'abc'])
    calls=[]
    def get(url,**kwargs):calls.append((url,kwargs));return Response()
    monkeypatch.setattr(ingest.requests,'get',get);target=tmp_path/'archive.gz';ingest.download_hour(NOW,target)
    assert target.read_bytes()==b'abc' and calls[0][0]=='https://data.gharchive.org/2026-11-01-12.json.gz'
    assert calls[0][1]['allow_redirects'] is False
    Response.headers={'Content-Length':'4'}
    with pytest.raises(ValueError,match='Incomplete'):ingest.download_hour(NOW,target)
    Response.status_code=302
    with pytest.raises(ValueError,match='HTTP 200'):ingest.download_hour(NOW,target)
    monkeypatch.setattr(ingest,'ingest',lambda:{'failed':[]});assert ingest.main([])==0
    monkeypatch.setattr(ingest,'ingest',lambda:{'failed':[{'hour':'x'}]});assert ingest.main([])==1
    def fail():raise ValueError('fixture')
    monkeypatch.setattr(ingest,'ingest',fail);assert ingest.main([])==1
    assert 'Live ingestion stopped' in capsys.readouterr().err


# Exact original UI entry, captured before implementation for offline replay.
LEGACY_RUN_DEMO = 'async def run_demo(question, on_update=None):\n    trace = loop.new_trace(question, context.REFERENCE_DATE)\n    timings, setup = {}, []\n    api_key = ""\n    started = perf_counter()\n\n    def snapshot():\n        return loop.sanitize({"trace": deepcopy(trace), "tool_timings_ms": dict(timings),\n                              "setup_steps": deepcopy(setup), "elapsed_ms": (perf_counter() - started) * 1000,\n                              "rounds": len(trace["api_responses"])}, api_key)\n\n    def notify():\n        if on_update is not None:\n            on_update(snapshot())\n\n    try:\n        try:\n            loop.load_dotenv(ROOT / ".env", override=False)\n        except Exception:\n            raise RuntimeError("Unable to load the project .env configuration.") from None\n        api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()\n        if not api_key:\n            raise ValueError("DEEPSEEK_API_KEY is missing or empty.")\n        notify()\n        parameters = loop.StdioServerParameters(command=sys.executable, args=["-B", str(ROOT / "agent/mcp_server.py")],\n                                                cwd=str(ROOT), env=loop.get_default_environment())\n        async with loop.AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com", max_retries=0, timeout=60.0) as client:\n            async with loop.stdio_client(parameters) as (reader, writer):\n                async with loop.ClientSession(reader, writer, read_timeout_seconds=20) as session:\n                    await session.initialize()\n                    timed = TimedSession(session, trace, timings, setup, notify)\n                    shared = await context.shared_context(timed)\n                    glossary = (ROOT / "eval/glossary.md").read_text(encoding="utf-8")\n                    system_context = shared + ("\\n\\nUse lookup_glossary for definitions. Available topics include new_stars, "\n                                               "collaboration_events, active_contributors, time conventions, dataset scope, event types.")\n\n                    def lookup(term):\n                        entry = trace["tool_calls"][-1]\n                        lookup_started = perf_counter()\n                        try:\n                            return context.lookup_glossary(glossary, term)\n                        finally:\n                            timings[entry["call_id"]] = (perf_counter() - lookup_started) * 1000\n                            notify()\n\n                    task = asyncio.create_task(loop.run_loop(client, timed, trace, api_key, config="C",\n                                                              system_context=system_context, lookup_glossary=lookup))\n                    try:\n                        while not task.done():\n                            notify()\n                            await asyncio.wait({task}, timeout=0.1)\n                        trace = await task\n                    finally:\n                        if not task.done():\n                            task.cancel()\n                            await asyncio.gather(task, return_exceptions=True)\n    except Exception as error:\n        trace["status"] = "error"\n        trace["final_answer"] = f"Agent stopped: {loop.sanitize(str(error), api_key)}"\n    notify()\n    return snapshot()'

@pytest.mark.parametrize('bad',[
    {'id':'bad','repo':{'id':999,'name':'owner/repo000'},'created_at':'2026-11-01T10:00:00Z'},
    {'id':'','repo':{'id':1,'name':'owner/repo000'},'created_at':'2026-11-01T10:00:00Z'},
    {'id':'bad','repo':{'id':1,'name':'owner/repo000'},'created_at':'2026-11-01T10:00:00'},
    ['not an object'],
])
def test_bad_archive_event_not_marked_complete(catalog,bad):
    hour=NOW.replace(hour=10,minute=0)
    result,_=populate(catalog,events={hour:[bad]})
    assert result['failed']==[{'hour':'2026-11-01-10.json.gz','error':'ValueError'}]
    with duckdb.connect(str(catalog[2]),read_only=True) as db:
        assert db.execute("SELECT COUNT(*) FROM ingest_log WHERE source_file='2026-11-01-10.json.gz'").fetchone()[0]==0
        assert db.execute('SELECT COUNT(*) FROM events').fetchone()[0]==0


def test_live_result_visibly_discloses_coverage(monkeypatch):
    monkeypatch.setenv('AGENT_MODE','live')
    async def fake(question,on_update=None):
        trace=loop.new_trace(question,'2026-11-01')
        trace.update(mode='live',status='completed',submitted=True,final_answer='Offline fixture',
                     live_coverage={'retention_start':'2026-10-18T00:00:00+00:00',
                                    'complete_days_end_exclusive':'2026-11-01T00:00:00+00:00',
                                    'missing_complete_day_hours':['2026-10-20T00:00:00+00:00'],
                                    'last_ingested_at':'2026-11-01T12:30:00'})
        return {'trace':trace,'setup_steps':[],'tool_timings_ms':{},'rounds':0,'elapsed_ms':0}
    monkeypatch.setattr(app,'run_demo',fake)
    test=AppTest.from_string('from ui.app import main; main()',default_timeout=15).run()
    test.text_area[0].set_value('Count events for the last 7 days');test.button[-1].click().run()
    assert not test.exception
    assert any('Missing archive hours: 1' in c.value and 'not verified zero activity' in c.value for c in test.caption)
