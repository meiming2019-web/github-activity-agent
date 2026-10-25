"""Independent synthetic checks for offline scoring; no model or database execution."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest
from eval import score_v4 as s


@pytest.fixture
def question():
    return {'id': 'q1', 'layer': 'window', 'bounds': ['2026-10-15', '2026-10-22'],
            'reference_columns': ['value'], 'reference_rows': [[2]], 'targeted': True,
            'template_family_id': 'family', 'paraphrase_id': 'literal', 'distractor_probe': None}


@pytest.fixture
def run():
    return {'status': 'completed', 'submitted': True, 'answer_sql': "SELECT COUNT(*) AS value FROM events WHERE created_at >= '2026-10-15' AND created_at < '2026-10-22'",
            'answer_columns': ['value'], 'answer_rows': [[2]], 'answer_truncated': False,
            'tool_calls': [], 'prompt_tokens': 10, 'completion_tokens': 3, 'tool_call_count': 0,
            'response_models': ['test-model']}


def call(name='run_query', error=False, text='', sql='SELECT 1', **extra):
    return {'name': name, 'is_error': error, 'result_summary': text, 'arguments': {'sql': sql}, **extra}


@pytest.mark.parametrize('b,c,p', [(0, 0, 1), (1, 0, 1), (2, 0, .5), (5, 0, .0625),
                                 (6, 0, .03125), (0, 6, .03125), (4, 1, .375), (5, 5, 1), (20, 0, 2/2**20)])
def test_exact_mcnemar_independent_small_examples(b, c, p):
    assert s.exact_mcnemar(b, c) == p


@pytest.mark.parametrize('b,c', [(-1, 1), (1.0, 2), (True, 1)])
def test_exact_mcnemar_rejects_invalid_counts(b, c):
    with pytest.raises(ValueError): s.exact_mcnemar(b, c)


def test_paired_common_denominator_and_direction():
    result = s.paired_table([(True, True), (True, False), (False, True), (False, True), (False, False), (None, True), (False, None)])
    assert result == {'n': 5, 'both_success': 1, 'left_only': 1, 'right_only': 2,
                      'both_failure': 1, 'excluded': 2, 'p': 1.0, 'right_minus_left': .2}
    assert s.paired_table([(None, False)])['n'] == 0


def test_precomputed_only_and_columns(question, run, monkeypatch):
    from agent import mcp_server
    def forbidden(*args, **kwargs): raise AssertionError('SQL execution forbidden')
    monkeypatch.setattr(mcp_server, 'execute_select', forbidden)
    assert s.grade_rows(question, run) is None
    assert s.grade_rows(question, {**run, 'answer_columns': ['alias']}) is None
    assert s.grade_rows(question, {**run, 'answer_columns': ['other', 'VALUE'], 'answer_rows': [[9, 2]]}) is None
    assert s.grade_rows(question, {**run, 'answer_columns': ['value'], 'answer_rows': [[3]]}) == 'wrong_result_set'


@pytest.mark.parametrize('change,expected', [
    ({'submitted': False}, 'no_submission'), ({'status': 'sql_error_exhausted'}, 'sql_error_exhausted'),
    ({'status': 'error', 'final_answer': 'Agent stopped: Stopped after 3 consecutive SQL errors.'}, 'sql_error_exhausted'),
    ({'status': 'error', 'final_answer': 'Stopped at the limit of 12 tool calls'}, 'breaker'),
    ({'status': 'budget_exceeded'}, 'breaker'), ({'answer_truncated': True}, 'wrong_result_set'),
    ({'answer_rows': None}, 'wrong_result_set'), ({'answer_rows': [[2, 3]]}, 'wrong_result_set'),
    ({'answer_columns': [], 'answer_rows': [[]]}, 'missing_columns'), ({'answer_rows': []}, 'wrong_result_set')])
def test_taxonomy(question, run, change, expected):
    assert s.grade_rows(question, {**run, **change}) == expected


def test_multiset_duplicates_tolerance_and_name_pinning(question, run):
    q = {**question, 'reference_rows': [[2], [2], [3]]}
    assert s.grade_rows(q, {**run, 'answer_rows': [[3], [2], [2]]}) is None
    assert s.grade_rows(q, {**run, 'answer_rows': [[3], [3], [2]]}) == 'wrong_result_set'
    assert s.grade_rows(question, {**run, 'answer_rows': [[2.0000001]]}) is None
    assert s.grade_rows(question, {**run, 'answer_columns': ['value', 'alias'], 'answer_rows': [[99, 2]]}) == 'wrong_result_set'
    q2 = {**question, 'reference_columns': ['a', 'b'], 'reference_rows': [[1, 2]]}
    assert s.grade_rows(q2, {**run, 'answer_columns': ['x', 'y'], 'answer_rows': [[2, 1]]}) is None


@pytest.mark.parametrize('change,present', [({}, True), ({'submitted': False}, False), ({'answer_sql': None}, False), ({'answer_sql': ' '}, False)])
def test_submitted_sql_is_committed(run, change, present):
    assert bool(s.submitted_sql({**run, **change})) is present


def test_whitelist_exact_and_raw_error():
    error = 'Error executing tool run_query: Function is not allowed: EXISTS'
    assert s.whitelist_state(call(error=True, text=error)) == 'rejected'
    assert s.whitelist_state(call(error=True, text='mapped explanation', raw_error=error)) == 'rejected'
    assert s.whitelist_state(call(error=True, text='Something about Function is not allowed: EXISTS')) == 'unknown'
    assert s.whitelist_state(call()) == 'passed'
    assert s.whitelist_state(call(name='describe_table', error=True)) == 'not_dispatched'
    assert s.whitelist_state(call(error=True, text=error, rejected=True)) == 'not_dispatched'


def test_recovery_skips_other_tools_and_submit_answer(run):
    rejected = call(error=True, text='Error executing tool run_query: SQL construct is not allowed: Values')
    trace = {**run, 'tool_calls': [rejected, call(name='lookup_glossary'), call(name='submit_answer'), call()]}
    out = s.recovery(trace)
    assert out['first_index'] == 0 and out['next_index'] == 3 and out['outcome'] is True
    assert s.recovery({**run, 'tool_calls': [rejected, rejected, call()]})['outcome'] is False


def test_recovery_unknowns_and_absence_are_not_success(run):
    rejected = call(error=True, text='Error executing tool run_query: Function is not allowed: EXISTS')
    assert s.recovery(run)['rejection'] is False
    assert s.recovery({**run, 'tool_calls': [rejected]})['reason'] == 'no_next_run_query'
    assert s.recovery({**run, 'tool_calls': [rejected, call(error=True, text='unknown')]})['outcome'] is False
    prior = s.recovery({**run, 'tool_calls': [call(error=True, text='unknown'), rejected, call()]})
    assert prior['first_proven'] is False and prior['outcome'] is False
    assert s.recovery({**run, 'tool_calls': [call(error=True, text='unknown')]})['reason'] == 'unknown_sql_error'


def test_first_submission_and_loop_recovery(question, run):
    good = call(name='submit_answer', sql=run['answer_sql'])
    assert s.first_submission(question, {**run, 'tool_calls': [call(), good]}) is True
    assert s.first_submission(question, {**run, 'tool_calls': [call(name='submit_answer', error=True), good]}) is False
    assert s.first_submission(question, run) is None
    assert s.first_submission(question, {**run, 'tool_calls': [call(name='submit_answer', sql='other')]}) is None


@pytest.mark.parametrize('rows,empty,zero', [([], True, False), ([[0]], False, True), ([['day', 0], ['day2', 0]], False, True), ([[1], [0]], False, False), ([[False]], False, False), ([[None]], False, False)])
def test_empty_zero_definition(run, rows, empty, zero):
    assert s.empty_zero({**run, 'answer_rows': rows}) == {'empty': empty, 'all_numeric_zero': zero}
    assert s.empty_zero({**run, 'submitted': False, 'answer_rows': rows}) == {'empty': False, 'all_numeric_zero': False}


def test_prefix_literal_identity_excludes_call_ids(run):
    a = {**run, 'tool_calls': [call(call_id='a'), call(sql='SELECT 2')]}
    b = {**run, 'tool_calls': [call(call_id='b'), call(sql='select 2')]}
    assert s.action_prefix(a, b) == {'common_length': 1, 'left_length': 2, 'right_length': 2, 'identical': False}
    assert s.action_prefix(a, a)['identical'] is True
    assert s.action_prefix(run, run)['common_length'] == 0


def test_bootstrap_independent_extremes_and_family_weighting():
    assert s.cluster_bootstrap([], ['a'])['ci95'] is None
    with pytest.raises(ValueError): s.cluster_bootstrap([], ['a'], replicates=0)
    assert s.cluster_bootstrap([('a', 1), ('a', 1)], ['a'], replicates=100)['ci95'] == [1, 1]
    sample = [('a', 1)] * 9 + [('b', -1)]
    result = s.cluster_bootstrap(sample, ['a','b'], replicates=1000)
    assert result['estimate'] == .8 and result['families'] == 2 and result['n'] == 10
    assert result['ci95'] == [.8, 1]
    assert s.cluster_bootstrap(sample, ['a','b'], replicates=1000) == result


def test_score_run_keeps_boundary_and_rows_independent(question, run):
    scored = s.score_run(question, run)
    assert scored['category'] is None and scored['boundary_correct'] is True
    wrong_sql = run['answer_sql'].replace('2026-10-15', '2026-10-14')
    scored = s.score_run(question, {**run, 'answer_sql': wrong_sql})
    assert scored['category'] is None and scored['boundary_correct'] is False
    scored = s.score_run(question, {**run, 'submitted': False})
    assert scored['boundary_correct'] is None
    control = s.score_run({**question, 'bounds': None}, run)
    assert control['boundary']['classification'] == 'no_window_predicate'
    assert control['boundary']['observed_time_filter'] is True


def test_percent_and_markdown():
    assert s.percent(1, 2) == '1/2 (50.00%)'
    assert s.percent(0, 0) == '0/0 (not estimable)'
    assert 'a\\|b c' in s.table(['x'], [['a|b\nc']])
    assert '| a\\|b |' in s.table(['a|b'], [[1]])


def test_hash_jsonl_and_torn_record(tmp_path):
    p=tmp_path/'records.jsonl'; p.write_bytes(b'{"a":1}\n')
    assert s.file_hash(p) == hashlib.sha256(p.read_bytes()).hexdigest()
    assert s.read_jsonl(p) == [{'a': 1}]
    p.write_bytes(b'{"a":1}')
    with pytest.raises(ValueError): s.read_jsonl(p)


def test_summarize_fixed_sequence_gate(question, run):
    q = {**question, 'id': 'w'}
    adv = {**question, 'id': 'a', 'layer': 'advanced_sql'}
    ctl = {**question, 'id': 'c', 'layer': 'control', 'bounds': None}
    runs = {1: {(x['id'], cfg): deepcopy(run) for x in (q, adv, ctl) for cfg in s.CONFIGS}, 2: {}}
    result = s.summarize([q, adv, ctl], runs)
    assert result['endpoint1']['p'] == 1 and result['endpoint1']['n'] == 1
    assert result['endpoint2']['gate_open'] is False and result['endpoint2']['p'] is None
    assert result['guard_triggered'] is False


def test_load_inputs_hash_failure_precedes_outcomes(tmp_path, monkeypatch):
    monkeypatch.setattr(s, 'HASHES', {'frozen': 'bad'})
    (tmp_path/'frozen').write_text('original')
    with pytest.raises(ValueError, match='Frozen hash mismatch'): s.load_inputs(tmp_path)


def test_fixed_sequence_open_and_guard_trigger(question, run):
    questions=[]; data={}
    for i in range(6):
        for layer in ('window','advanced_sql','control'):
            q={**question,'id':f'{layer}{i}','layer':layer,'bounds':None if layer=='control' else question['bounds']}
            questions.append(q)
            for c in s.CONFIGS:
                r=deepcopy(run)
                if layer=='window' and c=='C':r['answer_sql']=r['answer_sql'].replace('2026-10-15','2026-10-14')
                if layer=='control' and c!='C':r['answer_rows']=[[3]]
                if layer=='advanced_sql':
                    bad=call(error=True,text='Error executing tool run_query: Function is not allowed: EXISTS')
                    r['tool_calls']=[bad,call() if c=='C3.1' else bad]
                data[(q['id'],c)]=r
    result=s.summarize(questions,{1:data,2:{}})
    assert result['endpoint1']['right_only']==6 and result['endpoint1']['p']==.03125
    assert result['endpoint2']['both_rejected']==6 and result['endpoint2']['p']==.03125
    assert result['endpoint2']['right_only']==6 and result['guard_triggered'] is True


def test_flip_common_evaluable_not_missing_as_stable(question, run):
    q={**question,'id':'w'}
    a={('w',c):deepcopy(run) for c in s.CONFIGS}; b=deepcopy(a)
    b[('w','C')]['answer_rows']=[[3]]
    b[('w','C2.1')].update(submitted=False,answer_sql=None)
    result=s.summarize([q],{1:a,2:b})
    rows=s.descriptive_flips([q],result['scored'])
    boundary=next(r for r in rows if r[:2]==['boundary','C2.1'])
    assert boundary[2:7]==[1,0,0,0,1]
    whole=next(r for r in rows if r[:2]==['whole_question','C'])
    assert whole[3:7]==[1,1,0,0]


def test_report_renders_adjudication_and_no_gate_leak(question, run):
    qs=[{**question,'id':layer,'layer':layer,'bounds':None if layer=='control' else question['bounds']} for layer in ('window','advanced_sql','control')]
    data={(q['id'],c):deepcopy(run) for q in qs for c in s.CONFIGS}
    result=s.summarize(qs,{1:data,2:deepcopy(data)})
    text=s.render_report(result,'External validity statement (final wording, locked): "Scope X."\n\n## 11. Errata\n\n- An erratum.\n')
    assert 'Post-registration adjudications' in text and 'Not tested: gate closed or no eligible pairs' in text
    assert '"Scope X."' in text and '- An erratum.' in text
    assert 'observed_time_filter' in text and 'No model' in text
    assert '## Limitations' in text


@pytest.fixture
def input_tree(tmp_path,monkeypatch):
    def write(name,rows):
        p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(''.join(json.dumps(r)+'\n' for r in rows))
    db=tmp_path/'data/github.duckdb';db.parent.mkdir();db.write_bytes(b'not opened as a database')
    snapshot=s.file_hash(db)
    qs=[{'record_type':'question','id':f'q{i}','snapshot_sha256':snapshot,'reference_rows':[[1]],'reference_columns':['v']} for i in range(300)]
    schedule=[{'record_type':'metadata'}]+[{'question_id':q['id'],'order':list(s.CONFIGS),'pass':p} for p in (1,2) for q in qs[:300 if p==1 else 60]]
    write('eval/v4_questions.jsonl',qs);write('eval/v4_schedule.jsonl',schedule)
    for p,name in ((1,'runs_v4.jsonl'),(2,'runs_v4_pass2.jsonl')):
        write('eval/results/'+name,[{'record_type':'trial','question_id':a['question_id'],'config':c,'pass':p,'harness_version':'c2.1'} for a in schedule[1:] if a['pass']==p for c in s.CONFIGS])
    monkeypatch.setattr(s,'HASHES',{str(p.relative_to(tmp_path)):s.file_hash(p) for p in tmp_path.rglob('*') if p.is_file()})
    return tmp_path


def test_load_inputs_full_synthetic_universe(input_tree):
    qs,runs=s.load_inputs(input_tree)
    assert len(qs)==300 and len(runs[1])==900 and len(runs[2])==180


@pytest.mark.parametrize('fault',['snapshot','reference','duplicate','missing','harness'])
def test_load_inputs_rejects_integrity_faults(input_tree,fault):
    name='eval/v4_questions.jsonl' if fault in ('snapshot','reference') else 'eval/results/runs_v4.jsonl'
    p=input_tree/name;rows=s.read_jsonl(p)
    if fault=='snapshot':rows[0]['snapshot_sha256']='different'
    elif fault=='reference':rows[0]['reference_rows']=[]
    elif fault=='duplicate':rows.append(rows[0])
    elif fault=='missing':rows.pop()
    else:rows[0]['harness_version']='different'
    p.write_text(''.join(json.dumps(r)+'\n' for r in rows));s.HASHES[name]=s.file_hash(p)
    with pytest.raises(ValueError):s.load_inputs(input_tree)


def test_main_uses_only_offline_inputs_and_report(tmp_path,question,run,monkeypatch):
    qs=[question];data={(question['id'],c):deepcopy(run) for c in s.CONFIGS}
    (tmp_path/'eval').mkdir()
    (tmp_path/'eval/v4_preregister.md').write_text('External validity statement: "Scope X."\n## 11. Errata\n\n- Historical caveat.\n')
    monkeypatch.setattr(s,'ROOT',tmp_path)
    monkeypatch.setattr(s,'load_inputs',lambda root:(qs,{1:data,2:{}}))
    s.main()
    assert (tmp_path/'eval/v4_report.md').is_file()


def test_recovery_adjudication_next_recorded_query_and_reasons(run):
    reject=call(error=True,text='Error executing tool run_query: Function is not allowed: EXISTS')
    for next_calls,reason in [([], 'no_next_run_query'),([call(error=True,text='unidentifiable')],'unknown'),([call(rejected=True,error=True)],'not_dispatched')]:
        result=s.recovery({**run,'tool_calls':[reject,call(name='submit_answer')]+next_calls})
        assert result['rejection'] and result['outcome'] is False and result['reason']==reason
    assert s.recovery({**run,'tool_calls':[reject,call(rejected=True,error=True),call()]})['next_index']==1


def test_bootstrap_11_universe_and_zero_denominators():
    families=[f'f{i}' for i in range(11)]
    result=s.cluster_bootstrap([('f0',-1)],families,replicates=1000)
    assert result['families']==11 and result['eligible_families']==1 and result['signed_difference']==-1
    assert result['estimate']==1 and result['ci95']==[1,1]
    assert 0<result['zero_denominator']<1000
    assert result['valid_replicates']+result['zero_denominator']==1000
    assert s.cluster_bootstrap([('f0',-1)],families,replicates=1000)==result
    empty=s.cluster_bootstrap([],families,replicates=100)
    assert empty['zero_denominator']==100 and empty['valid_replicates']==0 and empty['ci95'] is None
    with pytest.raises(ValueError):s.cluster_bootstrap([('other',1)],families)
    with pytest.raises(ValueError):s.cluster_bootstrap([],['a','a'])


def flip_record(boundary=True,rejection=True,outcome=False):
    return {'boundary_correct':boundary,'recovery':{'rejection':rejection,'outcome':outcome}}


def test_flip_combines_two_configs_per_question_not_two_n():
    q=[{'id':'q','layer':'window'}]
    scored={1:{('q',c):flip_record(True) for c in s.CONFIGS},2:{('q',c):flip_record(False) for c in s.CONFIGS}}
    result=s.endpoint_flip(q,scored,'endpoint1',s.paired_table([(False,True)]))
    assert result['eligible_n']==1 and result['combined_flips']==2 and result['rate']==2
    assert result['threshold']==.5 and result['exploratory'] is True


@pytest.mark.parametrize('missing,effect_n,expected', [(False,1,True),(True,1,None),(False,0,None)])
def test_flip_zero_effect_and_unestimable(missing,effect_n,expected):
    q=[{'id':'q','layer':'window'}]
    scored={p:{('q',c):flip_record(None if missing else True) for c in s.CONFIGS} for p in (1,2)}
    result=s.endpoint_flip(q,scored,'endpoint1',s.paired_table([(True,True)]*effect_n))
    assert result['exploratory'] is expected
    if missing:assert result['invalid_ids']==['q'] and result['rate'] is None


def test_flip_endpoint1_common_four_judgments_and_exact_threshold():
    qs=[{'id':str(i),'layer':'window'} for i in range(41)]
    scored={p:{(q['id'],c):flip_record(True) for q in qs for c in s.CONFIGS} for p in (1,2)}
    scored[1][('0','C')]['boundary_correct']=None
    scored[2][('1','C')]['boundary_correct']=False
    pairs=[(False,True)]*9+[(True,True)]*170
    result=s.endpoint_flip(qs,scored,'endpoint1',s.paired_table(pairs))
    assert result['eligible_n']==40 and result['combined_flips']==1
    assert result['rate']==1/40 and result['threshold']==9/358 and result['exploratory'] is False


def test_flip_endpoint2_eligibility_changes_excluded_and_ids_recorded():
    qs=[{'id':name,'layer':'advanced_sql'} for name in ('both','lost','gained','neither')]
    scored={p:{(q['id'],c):flip_record() for q in qs for c in s.CONFIGS} for p in (1,2)}
    for p,names in ((1,['gained','neither']),(2,['lost','neither'])):
        for name in names:scored[p][(name,'C2.1')]['recovery']['rejection']=False
    scored[2][('both','C3.1')]['recovery']['outcome']=True
    result=s.endpoint_flip(qs,scored,'endpoint2',s.paired_table([(False,True),(False,False)]))
    assert result['eligible_ids']==['both'] and result['rate']==1
    assert result['lost_eligibility']==['lost'] and result['gained_eligibility']==['gained'] and result['neither_eligible']==['neither']


def test_prefix_before_rejection_and_no_rejection_full_match(run):
    reject=call(error=True,text='Error executing tool run_query: Function is not allowed: EXISTS')
    a={**run,'tool_calls':[call(sql='same'),reject,call(sql='later-a')]}
    b={**run,'tool_calls':[call(sql='same'),call(sql='different'),call(sql='later-b')]}
    result=s.adjudicated_prefix(a,b)
    assert result['match'] and result['cutoff']==1 and result['first_indices']==[1,None]
    assert not s.adjudicated_prefix(a,{**b,'tool_calls':[call(sql='different-before'),reject]})['match']
    assert not s.adjudicated_prefix(a,{**run,'tool_calls':[]})['match']
    assert s.adjudicated_prefix(run,run)['no_rejection']
    assert not s.adjudicated_prefix(run,b)['match']
    zero=s.adjudicated_prefix({**run,'tool_calls':[reject]},run)
    assert zero['match'] and zero['empty_prefix']


def test_post_adjudication_e2_includes_missing_unknown_symmetrically(question,run):
    reject=call(error=True,text='Error executing tool run_query: Function is not allowed: EXISTS')
    q={**question,'layer':'advanced_sql'}
    data={(q['id'],c):{**run,'tool_calls':[reject]} for c in s.CONFIGS}
    data[(q['id'],'C3.1')]={**run,'tool_calls':[reject,call(error=True,text='unknown')]}
    result=s.summarize([q],{1:data,2:data})
    assert result['endpoint2']['n']==1 and result['endpoint2']['both_failure']==1 and result['endpoint2']['excluded']==0


def test_sensitivity_computed_not_mutating_main_and_bootstrap_all_families(question,run):
    qs=[];data={}
    for i in range(11):
        q={**question,'id':'v4_138' if i==0 else f'q{i}','template_family_id':f'f{i}','layer':'window' if i<9 else 'control'}
        qs.append(q)
        for c in s.CONFIGS:
            r=deepcopy(run)
            if i<9 and c=='C':r['answer_sql']=r['answer_sql'].replace('2026-10-15','2026-10-14')
            data[(q['id'],c)]=r
    result=s.summarize(qs,{1:data,2:deepcopy(data)})
    assert result['endpoint1']['right_only']==9
    adjud=s.adjudicated_statistics(result)
    assert adjud['sensitivity']['right_only']==8 and adjud['sensitivity']['left_only']==0
    assert adjud['sensitivity']['p']==.0078125
    assert result['endpoint1']['right_only']==9
    assert all(b['families']==11 and b['replicates']==10000 for b in adjud['bootstrap'].values())
    assert adjud['bootstrap']['endpoint2']['zero_denominator']==10000
