"""Offline v4 scoring from frozen submitted rows; no SQL execution or model calls."""

from collections import Counter, defaultdict
import hashlib
from itertools import combinations, permutations
import json
import math
from pathlib import Path
import random

from agent.error_feedback import whitelist_feedback
from eval.grader import same_multiset
from eval.v4_sql_bounds import analyze_sql

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = ('C', 'C2.1', 'C3.1')
HASHES = {
    'eval/v4_questions.jsonl': '829ec0475c1ba1c090c8b1926221124df092af8b35b81ccc2a0a92e1fa897dc1',
    'eval/results/runs_v4.jsonl': 'b08c2881f8253d8d1e7d65b849f4fcd76499a2b0d467afe0a7f74140e7832240',
    'eval/results/runs_v4_pass2.jsonl': '8ff2597534c7459349107c0a55e8819f9c3b96f7a31700083ddddd59c44156a3',
    'eval/v4_sql_bounds.py': '331fa061ba46bb4cf53c52102eeddd3d0e423a557b3328469e0edbc34f32805f',
    'eval/v4_boundary_rubric.md': '71d2108cdbb2419e1ba5e1676162b27f56b93295bc87401cd01251dd954e411d',
    'eval/v4_preregister.md': '8aeba1dc302b92e9331a3bf0f28c8a451daa415be34ca4dd2aee6c88d5103ab5',
    'eval/v4_schedule.jsonl': '1a9be6c1571f5aceb917fdcc88ff3a66dc5bebcfa9b1540de6ea23620494234e',
    'eval/run_v4.py': '80d0f9f67d427842ef3b9f9e6e220eedcc11279ef63307cfb0a61453f11b7a51',
    'eval/gen_v4_questions.py': '318aee7fb68c6a660b0598ea77710f3ab7ecdcb66b1b8d6ce90a28076fe6b498',
    'data/github.duckdb': '2a063cab4176b97cfd00ea8e92932c64346127ba1da4b120452fb48236c25812',
}
# Fixed before examining v4 effects; implementation details, not preregistered values.
BOOTSTRAP_SEED = 42025
BOOTSTRAP_REPLICATES = 10000


def file_hash(path):
    """Stream bytes without opening DuckDB or changing the source."""
    with Path(path).open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def read_jsonl(path):
    """Reject torn records instead of silently dropping an incomplete tail."""
    raw = Path(path).read_bytes()
    if not raw.endswith(b'\n'):
        raise ValueError(f'Incomplete JSONL: {path}')
    return [json.loads(line) for line in raw.splitlines()]


def load_inputs(root):
    """Validate all frozen inputs and identities before inspecting outcome values."""
    root = Path(root)
    for name, expected in HASHES.items():
        if file_hash(root / name) != expected:
            raise ValueError(f'Frozen hash mismatch: {name}')
    questions = [q for q in read_jsonl(root / 'eval/v4_questions.jsonl') if q.get('record_type') == 'question']
    if len(questions) != 300 or len({q['id'] for q in questions}) != 300:
        raise ValueError('Expected exactly 300 unique questions')
    for q in questions:
        if q['snapshot_sha256'] != HASHES['data/github.duckdb']:
            raise ValueError('Per-question snapshot mismatch')
        if not q['reference_rows'] or any(len(row) != len(q['reference_columns']) for row in q['reference_rows']):
            raise ValueError('Invalid precomputed reference shape')
    schedule = read_jsonl(root / 'eval/v4_schedule.jsonl')[1:]
    runs = {}
    for number, name in ((1, 'runs_v4.jsonl'), (2, 'runs_v4_pass2.jsonl')):
        rows = [r for r in read_jsonl(root / 'eval/results' / name) if r.get('record_type') == 'trial']
        required = {(r['question_id'], c, number) for r in schedule if r['pass'] == number for c in r['order']}
        keys = [(r['question_id'], r['config'], r['pass']) for r in rows]
        if len(keys) != len(set(keys)) or set(keys) != required:
            raise ValueError(f'Pass {number} missing/extra/duplicate identity')
        if any(r.get('harness_version') != 'c2.1' for r in rows):
            raise ValueError('Unexpected harness version')
        runs[number] = {(r['question_id'], r['config']): r for r in rows}
    return questions, runs


def grade_rows(question, run):
    """Reuse frozen value/multiset comparison and its column-mapping algorithm.

    Only the reference-execution prefix of grade_run is replaced by precomputed
    columns/rows. No rejected query results or reference SQL are executed.
    """
    if run.get('status') != 'completed' or run.get('submitted') is not True:
        final = run.get('final_answer', '')
        if run.get('status') == 'budget_exceeded' or 'limit of 12 tool calls' in final or 'Answer already submitted.' in final:
            return 'breaker'
        if run.get('status') == 'sql_error_exhausted' or '3 consecutive SQL errors' in final:
            return 'sql_error_exhausted'
        return 'no_submission'
    if run.get('answer_truncated', False):
        return 'wrong_result_set'
    expected = question['reference_columns']
    gold = question['reference_rows']
    columns = run.get('answer_columns') or []
    rows = run.get('answer_rows')
    if not isinstance(rows, list) or any(not isinstance(row, (list, tuple)) or len(row) != len(columns) for row in rows):
        return 'wrong_result_set'
    if len(columns) < len(expected):
        return 'missing_columns'
    pinned, used = {}, set()
    for i, name in enumerate(expected):
        match = next((j for j, column in enumerate(columns) if j not in used and column.casefold() == name.casefold()), None)
        if match is not None:
            pinned[i] = match; used.add(match)
    remaining = [i for i in range(len(expected)) if i not in pinned]
    unused = sorted(set(range(len(columns))) - used)
    candidates = permutations(unused, len(remaining)) if len(remaining) <= 4 else [tuple(unused[:len(remaining)])]
    for candidate in candidates:
        indexes = {**pinned, **dict(zip(remaining, candidate))}
        actual = [[row[indexes[i]] for i in range(len(expected))] for row in rows]
        if same_multiset(gold, actual):
            return None
    return 'wrong_result_set'


def submitted_sql(run):
    """A final committed SQL is distinct from an attempted/rejected submission."""
    sql = run.get('answer_sql')
    return sql if run.get('submitted') is True and isinstance(sql, str) and sql.strip() else None


def exact_mcnemar(b, c):
    """Two-sided exact conditional binomial test, including zero discordances."""
    if type(b) is not int or type(c) is not int or min(b, c) < 0:
        raise ValueError('Discordances must be nonnegative integers')
    n = b + c
    return min(1.0, 2 * sum(math.comb(n, k) for k in range(min(b, c) + 1)) / 2**n) if n else 1.0


def paired_table(pairs):
    """Use common evaluable pairs only; b favors left, c favors right."""
    counts = Counter((left, right) for left, right in pairs if left is not None and right is not None)
    a, b, c, d = (counts[(True, True)], counts[(True, False)], counts[(False, True)], counts[(False, False)])
    n = a + b + c + d
    return {'n': n, 'both_success': a, 'left_only': b, 'right_only': c, 'both_failure': d,
            'excluded': len(pairs) - n, 'p': exact_mcnemar(b, c),
            'right_minus_left': (c - b) / n if n else None}


def cluster_bootstrap(observations, families, seed=BOOTSTRAP_SEED, replicates=BOOTSTRAP_REPLICATES):
    """Draw the complete family universe, then project onto endpoint-eligible rows.

    Post-registration estimand is absolute net discordance |b-c|/n. Draw all
    eleven families for formal analyses, including families without this endpoint.
    Such families add no eligible rows, not failures. Zero-denominator replicates
    remain counted but cannot supply a numerical statistic; percentile bounds use
    the explicitly reported valid replicates only. Rows within families are equal.
    """
    if replicates < 1 or not families or len(set(families)) != len(families):
        raise ValueError('Positive replicates and a unique nonempty family universe are required')
    groups = {family: [] for family in sorted(families)}
    for family, difference in observations:
        if family not in groups:
            raise ValueError('Observation outside the family universe')
        groups[family].append(difference)
    totals = [(sum(values), len(values)) for values in groups.values()]
    rng, estimates = random.Random(seed), []
    empty = 0
    for _ in range(replicates):
        drawn = [totals[rng.randrange(len(totals))] for _ in totals]
        denominator = sum(t[1] for t in drawn)
        if denominator == 0:
            empty += 1
        else:
            estimates.append(abs(sum(t[0] for t in drawn)) / denominator)
    estimates.sort()
    valid = len(estimates)
    limits = [estimates[max(0, math.ceil(valid * quantile) - 1)] for quantile in (.025, .975)] if valid else None
    n = sum(t[1] for t in totals)
    signed = sum(t[0] for t in totals) / n if n else None
    return {'families': len(groups), 'eligible_families': sum(bool(v) for v in groups.values()),
            'n': n, 'signed_difference': signed, 'estimate': abs(signed) if signed is not None else None,
            'ci95': limits, 'replicates': replicates, 'zero_denominator': empty, 'valid_replicates': valid,
            'seed': seed}


def whitelist_state(call):
    """Use exact frozen validator diagnostics, never vague SQL-error keywords."""
    if call.get('name') not in ('run_query', 'submit_answer') or call.get('rejected'):
        return 'not_dispatched'
    if call.get('is_error') is False:
        return 'passed'
    content = call.get('raw_error', call.get('result_summary', ''))
    if call.get('is_error') is True and isinstance(content, str) and whitelist_feedback(content) != content:
        return 'rejected'
    return 'unknown'


def recovery(run):
    """First documented whitelist rejection, followed by the next recorded run_query.

    Do not substitute another tool or submit_answer. Unknown earlier SQL errors
    prevent proving that the documented rejection was the first rejection.
    Post-registration: missing/unknown next outcomes are failures, with separate reasons.
    """
    calls = run.get('tool_calls', [])
    uncertain_prior = False
    for index, call in enumerate(calls):
        state = whitelist_state(call)
        if state == 'unknown':
            uncertain_prior = True
        if state != 'rejected':
            continue
        result = {'rejection': True, 'first_proven': not uncertain_prior, 'first_index': index,
                  'next_index': None, 'outcome': False, 'reason': 'no_next_run_query'}
        for later in range(index + 1, len(calls)):
            nxt = calls[later]
            if nxt.get('name') == 'run_query':
                next_state = whitelist_state(nxt)
                result.update(next_index=later, reason=next_state,
                              outcome=next_state == 'passed')
                break
        if uncertain_prior:
            result.update(outcome=False, reason='first_rejection_not_proven')
        return result
    return {'rejection': False, 'first_proven': not uncertain_prior, 'first_index': None,
            'next_index': None, 'outcome': None, 'reason': 'unknown_sql_error' if uncertain_prior else 'no_rejection'}


def first_submission(question, run):
    """Score first dispatched submission only when its recorded rows are available."""
    calls = [c for c in run.get('tool_calls', []) if c.get('name') == 'submit_answer' and not c.get('rejected')]
    if not calls:
        return None
    first = calls[0]
    if first.get('is_error') is True:
        return False
    if first.get('is_error') is False and first.get('arguments', {}).get('sql') == submitted_sql(run):
        return grade_rows(question, {**run, 'status': 'completed'}) is None
    return None


def empty_zero(run):
    """Observe submitted empty rows or all numeric cells zero; not an SQL inference."""
    rows = run.get('answer_rows')
    if not run.get('submitted') or not isinstance(rows, list):
        return {'empty': False, 'all_numeric_zero': False}
    numeric = [cell for row in rows for cell in row if type(cell) in (int, float)]
    return {'empty': rows == [], 'all_numeric_zero': bool(numeric) and all(cell == 0 for cell in numeric)}


def action_prefix(left, right):
    """Literal tool name plus parsed argument identity; exclude random call IDs."""
    sequences = [[(c.get('name'), c.get('arguments')) for c in r.get('tool_calls', [])] for r in (left, right)]
    common = 0
    for a, b in zip(*sequences):
        if a != b:
            break
        common += 1
    return {'common_length': common, 'left_length': len(sequences[0]), 'right_length': len(sequences[1]),
            'identical': sequences[0] == sequences[1]}


def score_run(question, run):
    """Combine independent recorded-row grading and the immutable boundary parser."""
    sql = submitted_sql(run)
    boundary = analyze_sql(sql, question['bounds'])
    return {'category': grade_rows(question, run), 'sql_present': sql is not None,
            'boundary': boundary, 'boundary_correct': boundary['classification'] == 'correct' if sql else None,
            'recovery': recovery(run), 'first_submission_correct': first_submission(question, run),
            'empty_zero': empty_zero(run)}


def percent(success, total):
    """Render the denominator explicitly, including empty eligible sets."""
    return f'{success}/{total} ({100 * success / total:.2f}%)' if total else '0/0 (not estimable)'


def table(headers, rows):
    """Render safe Markdown cells without mutating evidence."""
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    return '\n'.join(['| ' + ' | '.join(cell(header) for header in headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |'] +
                     ['| ' + ' | '.join(cell(v) for v in row) + ' |' for row in rows])


def summarize(questions, runs):
    """Compute locked endpoints and explicitly post-registration adjudicated auxiliaries."""
    qs = {q['id']: q for q in questions}
    scored = {p: {key: score_run(qs[key[0]], run) for key, run in data.items()} for p, data in runs.items()}
    windows = [q for q in questions if q['layer'] == 'window']
    advanced = [q for q in questions if q['layer'] == 'advanced_sql']
    controls = [q for q in questions if q['layer'] == 'control']
    ep1 = paired_table([(scored[1][(q['id'], 'C')]['boundary_correct'], scored[1][(q['id'], 'C2.1')]['boundary_correct']) for q in windows])
    both_rejected = [q for q in advanced if all(scored[1][(q['id'], c)]['recovery']['rejection'] for c in CONFIGS[1:])]
    ep2 = paired_table([(scored[1][(q['id'], 'C2.1')]['recovery']['outcome'], scored[1][(q['id'], 'C3.1')]['recovery']['outcome']) for q in both_rejected])
    ep2['both_rejected'] = len(both_rejected)
    # Never expose an Endpoint-2 inferential p-value when fixed-sequence gate fails.
    ep2['gate_open'] = ep1['p'] < .05
    if not ep2['gate_open'] or ep2['excluded'] or not ep2['n']:
        ep2['p'] = None
    guards = {f'{a} vs {b}': paired_table([(scored[1][(q['id'], a)]['category'] is None, scored[1][(q['id'], b)]['category'] is None) for q in controls]) for a, b in combinations(CONFIGS, 2)}
    return {'questions': questions, 'runs': runs, 'scored': scored, 'endpoint1': ep1, 'endpoint2': ep2,
            'guards': guards, 'guard_triggered': any(v['p'] < .05 for v in guards.values())}


def descriptive_flips(questions, scored):
    """Return descriptive per-configuration transition tables, separate from combined flips."""
    rows = []
    for endpoint in ('whole_question', 'boundary', 'recovery'):
        for config in CONFIGS:
            pairs = []
            for q in questions:
                key = (q['id'], config)
                if key not in scored[2]:
                    continue
                if endpoint == 'boundary' and q['layer'] != 'window':
                    continue
                if endpoint == 'recovery' and q['layer'] != 'advanced_sql':
                    continue
                values = []
                for number in (1, 2):
                    result = scored[number][key]
                    values.append(result['category'] is None if endpoint == 'whole_question' else
                                  result['boundary_correct'] if endpoint == 'boundary' else result['recovery']['outcome'])
                pairs.append(tuple(values))
            paired = paired_table(pairs)
            rows.append([endpoint, config, len(pairs), paired['n'], paired['left_only'], paired['right_only'],
                         paired['excluded'], percent(paired['left_only'] + paired['right_only'], paired['n'])])
    return rows


def endpoint_flip(questions, scored, endpoint, paired):
    """Apply the adjudicated combined-flips/question denominator, range zero to two."""
    configs = CONFIGS[:2] if endpoint == 'endpoint1' else CONFIGS[1:]
    layer = 'window' if endpoint == 'endpoint1' else 'advanced_sql'
    selected = [q for q in questions if q['layer'] == layer and all((q['id'], c) in scored[2] for c in configs)]
    eligible, lost, gained, neither, invalid = [], [], [], [], []
    flips = Counter({c: 0 for c in configs})
    for q in selected:
        states = [[scored[p][(q['id'], c)] for c in configs] for p in (1, 2)]
        if endpoint == 'endpoint2':
            qualifies = [all(r['recovery']['rejection'] for r in pair) for pair in states]
            if not all(qualifies):
                (lost if qualifies[0] else gained if qualifies[1] else neither).append(q['id'])
                continue
            values = [[r['recovery']['outcome'] for r in pair] for pair in states]
        else:
            values = [[r['boundary_correct'] for r in pair] for pair in states]
        if any(v is None for pair in values for v in pair):
            invalid.append(q['id']); continue
        eligible.append(q['id'])
        for index, config in enumerate(configs):
            flips[config] += values[0][index] != values[1][index]
    n = len(eligible)
    numerator = sum(flips.values())
    rate = numerator / n if n else None
    effect = abs(paired['left_only'] - paired['right_only']) / paired['n'] if paired['n'] else None
    threshold = effect / 2 if effect is not None else None
    # Compare exact integer fractions, including the explicitly specified 0 >= 0.
    downgrade = (2 * numerator * paired['n'] >= abs(paired['left_only'] - paired['right_only']) * n) if n and paired['n'] else None
    return {'sample_stratum_n': len(selected), 'eligible_n': n, 'eligible_ids': eligible,
            'flips_by_config': dict(flips), 'combined_flips': numerator, 'rate': rate,
            'pass1_paired_n': paired['n'], 'net_effect': effect, 'threshold': threshold,
            'exploratory': downgrade, 'lost_eligibility': lost, 'gained_eligibility': gained,
            'neither_eligible': neither, 'invalid_ids': invalid}


def adjudicated_prefix(left, right):
    """Compare literal actions strictly before the earliest observed rejection.

    Align by trace position. The rejection call itself is excluded by 'before'.
    The cutoff is the smaller first-rejection index when both reject, or the
    observed index when only one rejects. Both traces must reach that cutoff;
    unequal earlier actions fail. With no rejection require full equality.
    Empty pre-rejection prefixes are counted explicitly, not hidden.
    """
    sequences = [[(c.get('name'), c.get('arguments')) for c in r.get('tool_calls', [])] for r in (left, right)]
    first = [next((i for i, c in enumerate(r.get('tool_calls', [])) if whitelist_state(c) == 'rejected'), None) for r in (left, right)]
    observed = [i for i in first if i is not None]
    if not observed:
        return {'match': sequences[0] == sequences[1], 'cutoff': None, 'no_rejection': True,
                'empty_prefix': False, 'first_indices': first}
    cutoff = min(observed)
    match = all(len(seq) >= cutoff for seq in sequences) and sequences[0][:cutoff] == sequences[1][:cutoff]
    return {'match': match, 'cutoff': cutoff, 'no_rejection': False,
            'empty_prefix': cutoff == 0, 'first_indices': first}


def adjudicated_statistics(result):
    """Compute only authorized endpoint/whole-question CIs and one sensitivity."""
    questions, scored, runs = (result[k] for k in ('questions', 'scored', 'runs'))
    families = sorted({q['template_family_id'] for q in questions})
    bootstrap = {}
    for endpoint, layer, configs in [('endpoint1', 'window', CONFIGS[:2]), ('endpoint2', 'advanced_sql', CONFIGS[1:])]:
        observations = []
        for q in questions:
            if q['layer'] != layer: continue
            pair = [scored[1][(q['id'], c)] for c in configs]
            if endpoint == 'endpoint2' and not all(r['recovery']['rejection'] for r in pair): continue
            values = [r['boundary_correct'] if endpoint == 'endpoint1' else r['recovery']['outcome'] for r in pair]
            if any(v is None for v in values): continue
            observations.append((q['template_family_id'], int(values[1]) - int(values[0])))
        bootstrap[endpoint] = cluster_bootstrap(observations, families)
    for left, right in combinations(CONFIGS, 2):
        observations = [(q['template_family_id'], int(scored[1][(q['id'], right)]['category'] is None) - int(scored[1][(q['id'], left)]['category'] is None)) for q in questions]
        bootstrap[f'whole_question: {left} vs {right}'] = cluster_bootstrap(observations, families)
    flips = {name: endpoint_flip(questions, scored, name, result[name]) for name in ('endpoint1', 'endpoint2')}
    prefixes = {q['id']: adjudicated_prefix(runs[1][(q['id'], 'C2.1')], runs[1][(q['id'], 'C3.1')]) for q in questions
                if all((q['id'], c) in runs[1] for c in CONFIGS[1:])}
    sensitivity = None
    if any(q['id'] == 'v4_138' for q in questions):
        # Explicit human adjudication only; do not mutate scored or frozen parser.
        sensitivity = paired_table([(True if q['id'] == 'v4_138' else scored[1][(q['id'], 'C')]['boundary_correct'],
                                     scored[1][(q['id'], 'C2.1')]['boundary_correct']) for q in questions if q['layer'] == 'window'])
    return {'bootstrap': bootstrap, 'flips': flips, 'prefixes': prefixes, 'sensitivity': sensitivity}


def render_report(result, preregistration):
    """Report auditable denominators and post-registration decisions without changing inputs."""
    questions, runs, scored = (result[k] for k in ('questions', 'runs', 'scored'))
    ep1, ep2 = result['endpoint1'], result['endpoint2']
    adjudicated = adjudicated_statistics(result)
    lines = ['# v4 Phase D analysis report', '',
             'Status: offline scoring completed under the frozen primary rules plus the explicitly labeled post-registration adjudications below. No model, API, SQL execution, re-run, or frozen-file modification is part of this analysis.', '',
             '## Frozen inputs and scoring integrity', '',
             table(['Input', 'Verified SHA-256'], sorted(HASHES.items())), '',
             'All 300 per-question snapshot hashes match the actual database bytes. Both frozen result universes are complete (900 pass-1, 180 pass-2 unique identities). No reference SQL is executed: gold rows come only from the question file. No rejected/tool result is promoted to a gold or final answer.', '',
             'The frozen grader.same_multiset/same_value functions are reused. Its case-insensitive name pinning, unused-column permutation (at most four unpinned columns), extra-column treatment and duplicate-aware tolerant matching are retained. Only its reference-execution prefix is replaced with precomputed reference_columns/reference_rows. The legacy grade_run function itself is never called. A truncated answer is counted under wrong_result_set; its truncation count is separately reported. The grader budget_exceeded branch is labeled breaker; three-consecutive-SQL-error termination retains sql_error_exhausted. No rejected submission is treated as a final SQL.', '',
             '## Analysis definitions recorded before effects', '',
             'Exact two-sided McNemar uses the conditional binomial distribution with p=1 for zero discordances. In all tables, left-only favors the first-named configuration and right-only favors the second. Endpoint 1 excludes a pair if either configuration lacks committed SQL; separate marginal missing counts do not create separate paired denominators. Unknown parser classifications are not correct and are disclosed separately. The frozen parser is not repaired or reinterpreted.', '',
             'Bootstrap implementation choices were recorded before effects: seed 42025; 10000 family-resampling replicates; empirical percentile endpoints ceil(0.025B), ceil(0.975B). These are implementation details, not preregistered values. The later human adjudication selects the estimand/weighting below; those choices were not specified by the original preregistration.', '',
             'The pre-effect audit identified missing operational definitions; descriptive results were then reported without selecting them. The user subsequently supplied the following decisions after viewing that initial report. They are post-registration adjudications, not retroactive preregistration content.', '',
             '## Post-registration adjudications (2026-10-25)', '',
             'E2: the first recorded run_query after the first documented whitelist rejection determines recovery; no following run_query or unidentifiable outcome is failure symmetrically. Counts and IDs below distinguish these conservative failures from observed whitelist rejections. Other tools, including submit_answer, cannot replace that next run_query.', '',
             'Flip downgrade: use each endpoint binary; sum flips over the two compared configurations and divide by common eligible questions, NOT twice that count. This quantity has range [0,2] (0% to 200%). Compare it with half the pass-1 absolute net discordance |b-c|/n. E1 requires both configs evaluable in both passes; E2 additionally requires both configs to have rejection eligibility in both passes. Eligibility changes are descriptive only. Zero effect implies zero threshold, so an observed zero flip rate still meets the literal >= rule; an empty denominator is not estimable and does not license validation.', '',
             'Family bootstrap: draw 11 family labels with replacement per replicate from the full 11-family universe, 10000 times. Include all eligible questions from each selected family, with equal question weights and family multiplicity. Project each draw onto the relevant endpoint or full-set paired population; no eligible rows means an undefined replicate, counted and omitted from numerical percentiles. Use |b-c|/n consistently with the adjudicated absolute net effect; signed differences remain visible separately. Percentile order statistics use the number of valid replicates. No family without endpoint exposure is treated as a negative observation.', '',
             'Prefix-match denominator: all 300 paired C2.1/C3.1 traces. Compare exact tool names and argument objects in trace order, ignoring random call IDs, outputs and timing; do not normalize SQL or reconstruct contexts. Align positions and take the earliest first-whitelist-rejection index across the pair as the boundary, excluding that rejection call itself (strictly before). Both traces must reach the cutoff and all preceding actions must match. If neither rejects, require full-sequence equality. Empty prefixes are explicitly disclosed.', '',
             'v4_138: retain the frozen main classification. A separately labeled, human-authorized sensitivity sets its C boundary judgment to correct, without changing the parser, files or main analysis. Message-level token cost and runtime actual injection text remain unavailable.', '',
             '## Endpoint 1: window stratum, C versus C2.1', '',
             table(['Paired n', 'Both correct', 'C only', 'C2.1 only', 'Neither correct', 'Joint exclusions', 'Exact two-sided p', 'C2.1 minus C'],
                   [[ep1['n'], ep1['both_success'], ep1['left_only'], ep1['right_only'], ep1['both_failure'], ep1['excluded'], f"{ep1['p']:.12g}", ep1['right_minus_left']]]), '']
    window_rows, family_rows, parser_reasons = [], [], Counter()
    for config in CONFIGS:
        selected = [scored[1][(q['id'], config)] for q in questions if q['layer'] == 'window']
        present = [r for r in selected if r['sql_present']]
        categories = Counter(r['boundary']['classification'] for r in present)
        window_rows.append([config, len(selected), len(selected)-len(present), percent(categories['correct'],len(present)), json.dumps(dict(sorted(categories.items())))])
    for family in sorted({q['template_family_id'] for q in questions if q['layer']=='window'}):
        selected = [q for q in questions if q['template_family_id']==family]
        counts = paired_table([(scored[1][(q['id'],'C')]['boundary_correct'],scored[1][(q['id'],'C2.1')]['boundary_correct']) for q in selected])
        family_rows.append([family, counts['n'], counts['left_only'], counts['right_only'], counts['excluded']])
    lines += [table(['Config','Window questions','No committed SQL','Correct / submitted','Parser categories'], window_rows), '',
              table(['Family','Paired n','C only','C2.1 only','Joint exclusions'], family_rows), '',
              'Non-significance is not evidence against the mechanism. The preregistered power statement anticipates low power if the true baseline error rate is at most 5%; the observed small error count is not a proof that the true rate meets that condition. Discordant counts are retained regardless of significance. Family clustering and only three window families limit independent information; missing SQL is not a correct window.', '',
              ('Visible frozen-parser limitation: v4_138/C is unparseable because the non-events py CTE is reused. Its sole events source has literal predicates >= 2026-10-08 and < 2026-10-15, matching its authorized interval. The locked binary still counts this as not classified correct. The nine Endpoint-1 discordances comprise eight both_wrong classifications and one unparseable classification; they must not be described as nine independently established semantic boundary errors. No repaired verdict is substituted into the main analysis; the explicitly authorized sensitivity appears separately below.' if any(q['id'] == 'v4_138' for q in questions) else 'Frozen parser limitations remain unmodified.'), '',
              '## Endpoint 2: advanced stratum, C2.1 versus C3.1', '',
              f"Fixed-sequence gate open: {ep2['gate_open']}. Both configurations have a documented whitelist rejection on {ep2['both_rejected']} questions; paired binary outcomes under adjudication: {ep2['n']}; remaining invalid pair exclusions: {ep2['excluded']}.", '',
              table(['Both recover','C2.1 only','C3.1 only','Neither recover','Exact p (gate-eligible only)'],
                    [[ep2['both_success'],ep2['left_only'],ep2['right_only'],ep2['both_failure'],ep2['p'] if ep2['p'] is not None else 'Not tested: gate closed or no eligible pairs']]), '']
    recovery_rows=[]
    for config in CONFIGS:
        records=[scored[1][(q['id'],config)]['recovery'] for q in questions if q['layer']=='advanced_sql']
        rejected=[r for r in records if r['rejection']]
        recovery_rows.append([config,len(rejected),sum(r['outcome'] is True for r in rejected),sum(r['outcome'] is False for r in rejected),sum(r['outcome'] is None for r in rejected),percent(sum(r['outcome'] is True for r in rejected),len(rejected)),json.dumps(dict(Counter(r['reason'] for r in records)))])
    lines += [table(['Config','Documented rejection set','Observed next-query pass','Conservative failures','Unclassified outcomes','Recovery / full rejection set','Reasons (all advanced)'],recovery_rows), '',
              'Rejections require exact frozen whitelist diagnostics (including original raw_error for feedback runs). A generic SQL/transport error does not prove rejection or whitelist passage. The next recorded run_query is used, skipping metadata/glossary tools and submit_answer. Undispatched or unidentified next-call results are conservative failures, not proven whitelist rejections. An unknown earlier SQL error leaves first-rejection identity unproven and is conservatively failed. No-next and unknown-next reason counts and IDs are retained below. No Endpoint-2 confirmatory p is reported when Endpoint 1 fails its gate.', '',
              '## Control guardrail', '',
              table(['Pair','n','Left only','Right only','Exact p'],[[pair,r['n'],r['left_only'],r['right_only'],f"{r['p']:.12g}"] for pair,r in result['guards'].items()]), '',
              f"Guardrail triggered: {result['guard_triggered']}. " + ('All mechanism conclusions are paused for investigation.' if result['guard_triggered'] else 'No pairwise control comparison reaches p<0.05; this does not prove absence of side effects.'), '']
    control_rows=[]
    for c in CONFIGS:
        records=[scored[1][(q['id'],c)] for q in questions if q['layer']=='control']
        control_rows.append([c,len(records),sum(not r['sql_present'] for r in records),sum(r['sql_present'] and r['boundary']['observed_time_filter'] is True for r in records),sum(r['sql_present'] and r['boundary']['observed_time_filter'] is False for r in records),sum(r['sql_present'] and r['boundary']['observed_time_filter'] is None for r in records)])
    lines += [table(['Config','Controls','No SQL','Extra time filter true','False','Unknown'],control_rows), '',
              'Control primary classification no_window_predicate is not evidence of no added time filter; the separate observed_time_filter field is used. Unknown detection and absent SQL are reported separately.', '',
              '## Whole-question accuracy and error taxonomy', '']
    accuracy, taxonomy, costs, process=[] ,[],[],[]
    groups=[('window',lambda q:q['layer']=='window'),('advanced targeted',lambda q:q['layer']=='advanced_sql' and q['targeted']),('advanced non-targeted',lambda q:q['layer']=='advanced_sql' and not q['targeted']),('control',lambda q:q['layer']=='control'),('all',lambda q:True)]
    for label,selector in groups:
        subset=[q for q in questions if selector(q)]
        accuracy.append([label,len(subset)]+[percent(sum(scored[1][(q['id'],c)]['category'] is None for q in subset),len(subset)) for c in CONFIGS])
        for c in CONFIGS:
            vals=[scored[1][(q['id'],c)] for q in subset]; traces=[runs[1][(q['id'],c)] for q in subset]
            cats=Counter(v['category'] for v in vals if v['category'] is not None)
            taxonomy.append([label,c]+[cats[k] for k in ('wrong_result_set','sql_error_exhausted','no_submission','missing_columns','breaker')]+[sum(bool(r.get('answer_truncated')) for r in traces)])
            sums=[sum(r.get(k,0) for r in traces) for k in ('prompt_tokens','completion_tokens','tool_call_count')]
            costs.append([label,c,len(subset)]+sums+[round(x/len(subset),3) if subset else None for x in sums])
            wrong=[v for v in vals if v['category'] is not None]
            first_known=sum(v['first_submission_correct'] is not None for v in vals)
            first_success=sum(v['first_submission_correct'] is True for v in vals)
            recovered=sum(v['category'] is None and v['first_submission_correct'] is False for v in vals)
            process.append([label,c,percent(first_success,first_known),len(vals)-first_known,recovered,len(wrong),percent(sum(v['empty_zero']['empty'] for v in wrong),len(wrong)),percent(sum(v['empty_zero']['all_numeric_zero'] for v in wrong),len(wrong))])
    family_accuracy = []
    for family in sorted({q['template_family_id'] for q in questions}):
        subset = [q for q in questions if q['template_family_id'] == family]
        family_accuracy.append([family, len(subset)] + [percent(sum(scored[1][(q['id'], c)]['category'] is None for q in subset), len(subset)) for c in CONFIGS])
    lines += [table(['Stratum','n']+list(CONFIGS),accuracy),'', table(['Family','n']+list(CONFIGS),family_accuracy), '',table(['Stratum','Config','wrong_result_set','sql_error_exhausted','no_submission','missing_columns','breaker','Truncated (overlap)'],taxonomy),'',
              'Whole-question differences are descriptive; no total-score superiority claim is licensed. Taxonomy is mutually exclusive; truncation is an overlapping diagnostic. SQL-error exhaustion and tool-budget breakers remain separate rather than being silently merged.', '',
              '## First submission, empty/zero outputs, and trajectory prefixes','',
              table(['Stratum','Config','First submitted SQL correct / known','No attempt or unavailable','Correct after failed first submit','Wrong answers','Empty / wrong','All numeric zero / wrong'],process),'',
              'First-attempt means the first dispatched submit_answer, as stated in Section 7, not the first exploratory run_query. Its success is measurable from stored final rows only when it is the committed successful submission; a failed submission is not a row-set success. Rejected earlier SQL is never executed offline. Empty means []; zero means at least one numeric cell and every numeric cell zero (categorical/date cells ignored). These are observable output flags, not inferred intent or silent semantic correctness.', '']
    prefixes=list(adjudicated['prefixes'].values())
    no_rejection=[p for p in prefixes if p['no_rejection']]
    rejection=[p for p in prefixes if not p['no_rejection']]
    lines += [f"Adjudicated prefix-match: {percent(sum(p['match'] for p in prefixes),len(prefixes))}; paired trace denominator {len(prefixes)} (required formal universe: 300). No rejection in either trace: {sum(p['match'] for p in no_rejection)}/{len(no_rejection)} fully identical. At least one rejection: {sum(p['match'] for p in rejection)}/{len(rejection)} pre-rejection prefixes identical. Empty pre-rejection prefixes: {sum(p['empty_prefix'] for p in prefixes)}.", '',
              '## Distractor probes and parser observability','']
    probe_rows=[]
    for layer in ('window','advanced_sql','control'):
        selected=[q for q in questions if q['layer']==layer and q['paraphrase_id']=='distractor']
        mismatches=[]
        for q in selected:
            probe=q['distractor_probe']
            expected_line=None if q['bounds'] is None else f"Question window: [{q['bounds'][0]}, {q['bounds'][1]})"
            if probe.get('triggered') != (expected_line is not None) or probe.get('appended_line') != expected_line:
                mismatches.append(q['id'])
        probe_rows.append([layer,len(selected),len(mismatches),','.join(mismatches) or 'None'])
    lines += [table(['Stratum','Frozen distractor probes','Mis-append','IDs'],probe_rows),'',
              'These probes were captured offline during generation. Runtime traces do not retain the actual injected context; runtime mis-append count is not separately estimable. No post-run reconstruction is substituted for that evidence. Controls have no operative window despite decorative dates.','']
    parser_rows=[]
    for c in CONFIGS:
        for layer in ('window','advanced_sql','control'):
            rs=[scored[1][(q['id'],c)] for q in questions if q['layer']==layer and scored[1][(q['id'],c)]['sql_present']]
            parser_rows.append([c,layer,json.dumps(dict(Counter(r['boundary']['classification'] for r in rs))),json.dumps(dict(Counter(r['boundary']['generate_series_end'] for r in rs)))])
            for r in rs:
                if r['boundary']['reason']:parser_reasons[r['boundary']['reason']]+=1
    lines += [table(['Config','Stratum','Primary parser classes (submitted only)','Scaffold end flags'],parser_rows),'',
              table(['Frozen parser reason (no correction applied)','Count'],sorted(parser_reasons.items())),'',
              'Unparseable does not prove a semantically wrong window, and scaffold flags cannot override the primary classification. The parser intentionally rejects some valid query forms; this report preserves that limitation. Additional visible parser defects, if found, must be disclosed without score repair.','',
              '## Cost and model fingerprints','',table(['Stratum','Config','n','Prompt tokens','Completion tokens','Tool calls','Mean prompt','Mean completion','Mean tools'],costs),'',
              'Token counts are observed aggregate usage, not money estimates. Tokens of the injected line and feedback messages are not separately recorded; repeated prompt accumulation, variable responses and tokenizer identity prevent exact isolation. No causal cost attribution is inferred from total differences.','']
    for number in (1,2):
        models=Counter(model for r in runs[number].values() for model in r.get('response_models',[]))
        lines.append(f"Pass {number} response_models: `{dict(models)}`.")
    lines += ['', '## Pass-2 transitions and downgrade status','',
              table(['Binary','Config','Sample eligible by stratum','Jointly evaluable','Pass1 success to failure','Pass1 failure to success','Unavailable pairs','Observed flips / evaluable'],descriptive_flips(questions,scored)),'',
              'Whole-question flips remain descriptive. Endpoint-specific combined flips and exact eligible denominators determine the adjudicated downgrade below.', '']
    flip_rows=[]
    for endpoint,f in adjudicated['flips'].items():
        flip_rows.append([endpoint,f['sample_stratum_n'],f['eligible_n'],json.dumps(f['flips_by_config']),f['combined_flips'],
                          f['rate'],f['net_effect'],f['threshold'],f['exploratory'] if f['exploratory'] is not None else 'Not estimable'])
    lines += [table(['Endpoint','Pass2 stratum n','Common eligible n','Flips by config','Combined flips','Flips/n','Pass1 |b-c|/n','50% threshold','Exploratory'],flip_rows),'']
    for endpoint,f in adjudicated['flips'].items():
        lines.append(f"{endpoint} eligibility: lost={f['lost_eligibility']}; gained={f['gained_eligibility']}; neither pass eligible={f['neither_eligible']}; missing/invalid judgment={f['invalid_ids']}. Common eligible IDs: {f['eligible_ids']}.")
    failure_rows=[]
    for number in (1,2):
        for config in CONFIGS:
            for reason in ('no_next_run_query','unknown','not_dispatched','first_rejection_not_proven'):
                ids=[q['id'] for q in questions if q['layer']=='advanced_sql' and (q['id'],config) in scored[number]
                     and scored[number][(q['id'],config)]['recovery']['rejection'] and scored[number][(q['id'],config)]['recovery']['reason']==reason]
                paired_ids=[qid for qid in ids if all((qid,c) in scored[number] and scored[number][(qid,c)]['recovery']['rejection'] for c in CONFIGS[1:])]
                failure_rows.append([number,config,reason,len(ids),', '.join(ids) or 'None',len(paired_ids),', '.join(paired_ids) or 'None'])
    lines += ['', '## Conservative E2 failures: counts and identities', '',
              table(['Pass','Config','Reason','Full rejection-set count','IDs','In E2 dual-rejection subset','Subset IDs'],failure_rows),'',
              'No-next and unknown-result failures are adjudicated binary zeros, not observations of a tool refusing SQL. They are retained symmetrically in E2 and in eligible cross-pass flips. In particular v4_219/C3.1 has a recorded native Binder Error after the next run_query; absent a structured whitelist-validation field, the conservative unknown-result rule is retained, not silently recoded as recovery.', '',
              '## Family clustering', '',
              table(['Statistic','Families sampled','Families with eligible rows','Eligible n','Signed difference','Absolute net effect','95% percentile CI','Zero denominator / 10000','Valid replicates'],
                    [[name,b['families'],b['eligible_families'],b['n'],b['signed_difference'],b['estimate'],b['ci95'],b['zero_denominator'],b['valid_replicates']] for name,b in adjudicated['bootstrap'].items()]), '',
              'All formal rows above sample the same 11-family universe. Seed=42025, B=10000. Zero-denominator draws are counted and excluded from percentile calculation, not set to zero and not redrawn. Intervals conditional on a nonempty eligible draw can be unstable with few contributing families. Whole-question pairwise CIs are secondary descriptive intervals, not additional primary tests or evidence of general superiority.', '',
              '## Sensitivity analysis: human-adjudicated v4_138', '']
    sensitivity=adjudicated['sensitivity']
    if sensitivity is not None:
        lines += [f"Main classification remains unchanged. In the separate sensitivity only, C is classified correct on v4_138: paired n={sensitivity['n']}; C2.1-only correct={sensitivity['right_only']}; C-only correct={sensitivity['left_only']}; exact two-sided McNemar p={sensitivity['p']:.12g}. This value is computed by exact_mcnemar, not copied from the instruction. Direction and nominal significance are unchanged. No sensitivity result replaces the main flip gate or primary p-value.", '']
    lines += ['## Claim scope and locked external validity statement','']
    for endpoint,ep in [('endpoint1',ep1),('endpoint2',ep2)]:
        flip=adjudicated['flips'][endpoint]
        significant=ep['p'] is not None and ep['p'] < .05 and ep['right_only'] > ep['left_only']
        if result['guard_triggered']:
            lines.append(f'{endpoint}: guardrail triggered; mechanism conclusions paused.')
        elif significant and flip['exploratory'] is False:
            lines.append(('On the v4 targeted distribution, per-question window-boundary injection (C2.1) reduced window-boundary errors relative to C (McNemar exact p = '+f"{ep['p']:.12g}"+').' if endpoint=='endpoint1' else 'Actionable whitelist feedback (C3.1) improved immediate step recovery after whitelist rejections relative to C2.1.') + ' This statement uses the frozen operational endpoint; its post-registration stability adjudication and parser limitations are disclosed above.')
        elif significant and flip['exploratory'] is True:
            lines.append(f'{endpoint}: nominal significance in the expected direction, but the adjudicated flip rule downgrades the claim to exploratory, not validated.')
        elif flip['exploratory'] is None:
            lines.append(f'{endpoint}: stability is not estimable; no validated claim is issued.')
        else:
            lines.append(f'{endpoint}: no significant improvement in the expected direction; no mechanism-improvement claim. The small paired recovery subset has insufficient power; non-significance does not establish equivalence or evidence against the mechanism.' if endpoint=='endpoint2' else f'{endpoint}: no significant improvement; the preregistered low-power caveat applies without proving a particular true error rate.')
    lines += ['', 'No total-score superiority claim is made. Whole-question accuracy and its CIs are descriptive. C3.1 versus C2.1 accuracy differences are separated into targeted and non-targeted families; no transfer beyond the template distribution is asserted. All conclusions remain scoped to English questions, this snapshot and the declared templates. Post-registration decisions are not retroactively confirmatory procedure.', '']
    external=next(line for line in preregistration.splitlines() if line.startswith('External validity statement'))
    lines.append(external)
    lines += ['', 'The X placeholder above is retained in this verbatim locked quotation; any numerical claim must use the declared paired denominator and the adjudicated inferential status.', '', '## Frozen errata', '']
    lines.extend(preregistration.split('## 11. Errata',1)[1].splitlines()[2:])
    lines += ['', '## Limitations', '',
              'Message-level token costs for injection and feedback, and actual runtime injected context text, were not recorded. They cannot be reconstructed exactly; no replacement observations or model estimates were created. The offline generator distractor probe is not runtime proof. Conservative E2 failures caused by absent/unknown follow-up are not actual observed whitelist rejections. E2 is underpowered and its flip comparison has only three common eligible questions. E1 has three contributing window families; its no-downgrade decision is very close to the specified threshold. Neither point identifies behavior on natural, multilingual or new-snapshot distributions.', '',
              'Operational flip, recovery, bootstrap and prefix decisions were supplied after the initial results were seen and are explicitly post-registration. The locked main parser classification for v4_138 remains unchanged; its sensitivity is separate. Full-set absolute-effect CIs are descriptive and do not establish direction or superiority.', '']
    lines += ['', '## Reproducibility and delivery', '',
              'Run `python -B -m eval.score_v4` offline. The only analysis output is this report. No raw result, schedule, reference, parser, glossary, preregistration or historical artifact is modified. Synthetic tests and the full offline suite are reported separately at delivery; no model requests are made by the scorer.', '']
    return '\n'.join(lines)


def main():
    """Explicit offline report generation; importing the scorer has no I/O."""
    questions,runs=load_inputs(ROOT)
    report=render_report(summarize(questions,runs),(ROOT/'eval/v4_preregister.md').read_text())
    path=ROOT/'eval/v4_report.md'
    path.write_text(report,encoding='utf-8')
    print(f'Offline report: {path}; SHA-256 {file_hash(path)}')


if __name__ == '__main__':
    main()
