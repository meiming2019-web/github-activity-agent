"""Independent, conservative DuckDB AST window classification; never execute SQL."""

from datetime import datetime, timedelta

import sqlglot
from sqlglot import exp
from sqlglot.optimizer.scope import Scope, build_scope


class UnknownWindow(ValueError):
    """The supported AST subset cannot establish the effective time interval."""


def _constant(node):
    """Resolve literal UTC dates/timestamps and literal whole-day arithmetic."""
    if isinstance(node, exp.Paren):
        return _constant(node.this)
    if isinstance(node, exp.Date):
        return _constant(node.this).replace(hour=0, minute=0, second=0, microsecond=0)
    if isinstance(node, exp.Cast):
        kind = node.args['to'].sql().upper()
        if kind not in ('DATE', 'TIMESTAMP', 'TIMESTAMPNTZ'):
            raise UnknownWindow('Unsupported temporal constant type')
        value = _constant(node.this)
        return value.replace(hour=0, minute=0, second=0, microsecond=0) if kind == 'DATE' else value
    if isinstance(node, (exp.Add, exp.Sub)) and isinstance(node.expression, exp.Interval):
        interval = node.expression
        if interval.args['unit'].name.upper() != 'DAY' or not isinstance(interval.this, exp.Literal):
            raise UnknownWindow('Only literal whole-day arithmetic is supported')
        days = int(interval.this.this)
        return _constant(node.this) + timedelta(days=days if isinstance(node, exp.Add) else -days)
    if isinstance(node, exp.Literal) and node.is_string:
        if '.' in node.this and len(node.this.split('.', 1)[1]) > 6:
            raise UnknownWindow('Sub-microsecond temporal constants are unsupported')
        value = datetime.fromisoformat(node.this)
        if value.tzinfo is not None:
            raise UnknownWindow('Timezone-bearing constants are outside this rubric')
        return value
    raise UnknownWindow('Dynamic or nonliteral temporal operand')


def _lineage(node, scope):
    """Resolve row-preserving aliases back to one physical events.created_at."""
    if isinstance(node, (exp.Paren, exp.Alias)):
        return _lineage(node.this, scope)
    if isinstance(node, exp.Date):
        origin = _lineage(node.this, scope)
        return (origin[0], 'date') if origin else None
    if isinstance(node, exp.Cast):
        origin = _lineage(node.this, scope)
        if origin is None:
            return None
        kind = node.args['to'].sql().upper()
        if kind == 'DATE':
            return (origin[0], 'date')
        if kind in ('TIMESTAMP', 'TIMESTAMPNTZ') and origin[1] == 'timestamp':
            return origin
        raise UnknownWindow('Unsupported temporal column cast')
    if not isinstance(node, exp.Column):
        if node is not None and any(_lineage(column, scope) for column in node.find_all(exp.Column)):
            raise UnknownWindow('Unsupported transformation of created_at')
        return None
    sources = scope.selected_sources
    if node.table:
        if node.table not in sources:
            raise UnknownWindow('Unresolved column qualifier')
        selected = [sources[node.table][1]]
    else:
        selected = [pair[1] for pair in sources.values()]
    matches = []
    for source in selected:
        if isinstance(source, exp.Table):
            if node.name.lower() == 'created_at':
                if source.name.lower() != 'events' or source.catalog or source.db.lower() not in ('', 'main'):
                    raise UnknownWindow('created_at belongs to an unsupported source')
                matches.append((id(source), 'timestamp'))
        elif isinstance(source, Scope):
            if source.outer_columns:
                raise UnknownWindow('Explicit derived-column name lists are unsupported')
            expressions = source.expression.selects
            projections = [item for item in expressions if item.alias_or_name == node.name]
            stars = [item for item in expressions if isinstance(item, exp.Star) or isinstance(item, exp.Column) and item.is_star]
            if len(projections) > 1:
                raise UnknownWindow('Ambiguous projection alias')
            projection = projections[0] if projections else exp.column(node.name) if stars else None
            if stars and any(star.args.get('except_') or star.args.get('replace') or star.args.get('rename') for star in stars):
                raise UnknownWindow('Modified star projections are unsupported')
            if projection is not None:
                origin = _lineage(projection, source)
                if origin:
                    if any(source.expression.args.get(key) for key in ('group', 'distinct', 'limit', 'offset', 'qualify')) or source.expression.find(exp.Window):
                        raise UnknownWindow('Temporal predicate above a non-row-preserving projection')
                    matches.append(origin)
    if len(matches) > 1 or matches and not node.table and len(selected) > 1:
        raise UnknownWindow('Ambiguous unqualified temporal column')
    if not matches and not node.table:
        aliases = [item for item in scope.expression.selects if isinstance(item, exp.Alias) and item.alias == node.name]
        if aliases and any(column.name.lower() == 'created_at' for item in aliases for column in item.find_all(exp.Column)):
            raise UnknownWindow('Same-select temporal aliases are unsupported')
    return matches[0] if matches else None


def _intersect(left, right):
    """Intersect lower/upper endpoints, retaining inclusive/exclusive precision."""
    lowers = [value for value in (left[0], right[0]) if value is not None]
    uppers = [value for value in (left[1], right[1]) if value is not None]
    lower = max(lowers, key=lambda value: (value[0], not value[1])) if lowers else None
    upper = min(uppers, key=lambda value: (value[0], value[1])) if uppers else None
    if lower and upper and (lower[0] > upper[0] or lower[0] == upper[0] and not (lower[1] and upper[1])):
        raise UnknownWindow('Contradictory or empty temporal interval')
    return lower, upper


def _comparison(column, literal, operator, scope):
    """Convert supported DATE comparisons into exact timestamp-set boundaries."""
    origin = _lineage(column, scope)
    if origin is None:
        return None
    value = _constant(literal)
    if origin[1] == 'date':
        if value.time() != datetime.min.time():
            raise UnknownWindow('DATE compared with a non-midnight timestamp')
        if operator == 'gt':
            value += timedelta(days=1)
            operator = 'ge'
        elif operator == 'le':
            value += timedelta(days=1)
            operator = 'lt'
        elif operator == 'eq':
            return ((value, True), (value + timedelta(days=1), False))
    # DuckDB TIMESTAMP is microsecond precision; preserve exact set semantics.
    if operator == 'gt':
        value += timedelta(microseconds=1)
        operator = 'ge'
    elif operator == 'le':
        value += timedelta(microseconds=1)
        operator = 'lt'
    if operator == 'eq':
        return ((value, True), (value + timedelta(microseconds=1), False))
    return ((value, operator == 'ge'), None) if operator in ('gt', 'ge') else (None, (value, operator == 'le'))


def _predicate(node, scope):
    """Conjoin constraints; OR is supported only for identical proven windows."""
    if isinstance(node, exp.Paren):
        return _predicate(node.this, scope)
    if isinstance(node, exp.And):
        return _intersect(_predicate(node.this, scope), _predicate(node.expression, scope))
    if isinstance(node, exp.Or):
        left, right = _predicate(node.this, scope), _predicate(node.expression, scope)
        if left == right and all(left):
            return left
        raise UnknownWindow('OR branches do not prove the same bounded window')
    if isinstance(node, exp.Between):
        if node.args.get('symmetric'):
            raise UnknownWindow('Symmetric BETWEEN is unsupported')
        first = _comparison(node.this, node.args['low'], 'ge', scope)
        last = _comparison(node.this, node.args['high'], 'le', scope)
        if first is not None and last is not None:
            return _intersect(first, last)
        if any(_lineage(column, scope) for column in node.find_all(exp.Column)):
            raise UnknownWindow('Temporal BETWEEN operand is not the tested column')
        return None, None
    operators = {exp.GTE: 'ge', exp.GT: 'gt', exp.LT: 'lt', exp.LTE: 'le', exp.EQ: 'eq'}
    if type(node) in operators:
        operator = operators[type(node)]
        forward = _comparison(node.this, node.expression, operator, scope)
        if forward is not None:
            return forward
        reverse = _comparison(node.expression, node.this, {'ge': 'le', 'gt': 'lt', 'le': 'ge', 'lt': 'gt', 'eq': 'eq'}[operator], scope)
        return reverse or (None, None)
    if any(_lineage(column, scope) for column in node.find_all(exp.Column)):
        raise UnknownWindow('Unsupported predicate on created_at')
    return None, None


def analyze_sql(sql, authorized_bounds):
    """Return six-way primary classification and independent guardrail/scaffold flags."""
    control = authorized_bounds is None
    result = {'classification': 'no_window_predicate' if control else 'unparseable',
              'observed_time_filter': None, 'observed_bounds': None, 'reason': None,
              'generate_series_end': 'not_present', 'secondary_parse_status': 'unparseable'}
    try:
        expected = None if control else tuple(datetime.fromisoformat(value) for value in authorized_bounds)
        if expected is not None and (len(expected) != 2 or expected[0] >= expected[1] or any(v.tzinfo for v in expected)):
            raise UnknownWindow('Invalid authorized boundaries')
        if not isinstance(sql, str) or not sql.strip():
            raise UnknownWindow('No SQL text')
        statements = sqlglot.parse(sql, read='duckdb', error_level=sqlglot.ErrorLevel.RAISE)
        if len(statements) != 1 or not isinstance(statements[0], exp.Select):
            raise UnknownWindow('Exactly one SELECT is required')
        tree = statements[0]
        root = build_scope(tree)
        reachable, pending, seen = [], [root], set()
        while pending:
            scope = pending.pop()
            if id(scope) in seen:
                raise UnknownWindow('Reused source scope requires branch-sensitive lineage')
            seen.add(id(scope)); reachable.append(scope)
            if scope.subquery_scopes or not isinstance(scope.expression, exp.Select):
                raise UnknownWindow('Scalar/correlated subqueries or set operations are unsupported')
            pending.extend(source for _, source in scope.selected_sources.values() if isinstance(source, Scope))
        for scope in reachable:
            for conditional in scope.expression.find_all(exp.Filter, exp.Case, exp.If):
                if conditional.find_ancestor(exp.Select) is scope.expression and any(
                        _lineage(column, scope) for column in conditional.find_all(exp.Column)):
                    result['observed_time_filter'] = True
                    raise UnknownWindow('Temporal aggregate FILTER or conditional expression is unsupported')
        sources = [source for scope in reachable for _, source in scope.selected_sources.values()
                   if isinstance(source, exp.Table) and source.name.lower() == 'events']
        predicates = []
        for scope in reachable:
            for key in ('where', 'having', 'qualify'):
                if scope.expression.args.get(key):
                    predicates.append((scope, scope.expression.args[key].this))
            for join in scope.expression.args.get('joins', []):
                if join.args.get('on'):
                    if join.args.get('side') and any(_lineage(column, scope) for column in join.args['on'].find_all(exp.Column)):
                        raise UnknownWindow('Outer-join temporal ON is not a row restriction')
                    predicates.append((scope, join.args['on']))
        result['observed_time_filter'] = any(column.name.lower() == 'created_at' for _, p in predicates for column in p.find_all(exp.Column))
        interval = (None, None)
        for scope, predicate in predicates:
            constraint = _predicate(predicate, scope)
            if any(constraint):
                result['observed_time_filter'] = True
            interval = _intersect(interval, constraint)
        if len(sources) > 1:
            raise UnknownWindow('Multiple physical events sources require independent windows')
        if not sources and any(interval):
            raise UnknownWindow('No supported physical events source')
        series_status = []
        for scope in reachable:
            for node in scope.expression.find_all(exp.GenerateSeries):
                try:
                    end = _constant(node.args['end'])
                    series_status.append('not_applicable' if control else 'correct' if not node.args.get('is_end_exclusive') and end == expected[1] - timedelta(days=1) else 'wrong')
                except (ValueError, KeyError, TypeError):
                    series_status.append('unparseable')
        if series_status:
            result['generate_series_end'] = 'unparseable' if 'unparseable' in series_status else 'wrong' if 'wrong' in series_status else series_status[0]
        result['secondary_parse_status'] = 'parsed'
        result['observed_bounds'] = [None if endpoint is None else {'value': endpoint[0].isoformat(), 'inclusive': endpoint[1]} for endpoint in interval]
        if control:
            return result
        if not any(interval):
            result['classification'] = 'no_window_predicate'
        else:
            wrong_start = interval[0] != (expected[0], True)
            wrong_end = interval[1] != (expected[1], False)
            result['classification'] = 'both_wrong' if wrong_start and wrong_end else 'start_wrong' if wrong_start else 'end_wrong' if wrong_end else 'correct'
    except (ValueError, TypeError, KeyError, AttributeError, sqlglot.errors.SqlglotError) as error:
        result['reason'] = str(error)
        if not control:
            result['classification'] = 'unparseable'
    return result
