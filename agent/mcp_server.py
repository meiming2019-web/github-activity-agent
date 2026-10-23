"""Four read-only stdio MCP tools for the local GitHub activity database."""

from datetime import date, datetime, time, timedelta
from decimal import Decimal
import math
from pathlib import Path
import threading
from time import perf_counter
from typing import Literal

import duckdb
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel, ConfigDict, Field, JsonValue
import sqlglot
from sqlglot import exp
from sqlglot.optimizer.scope import Scope, traverse_scope


DATABASE_PATH = Path(__file__).resolve().parents[1] / "data/github.duckdb"
QUERY_TIMEOUT_SECONDS = 10.0
MAX_ROWS = 200
TableName = Literal["events", "repos", "ingest_log"]
QUERY_TABLES = frozenset({("", "events"), ("", "repos")})
METADATA_TABLES = QUERY_TABLES | {("", "ingest_log")}
CATALOG_TABLES = frozenset({("information_schema", "tables")})
CATALOG_SQL = """
    SELECT table_name, table_type FROM information_schema.tables
    WHERE table_catalog = CURRENT_DATABASE() AND table_schema = 'main'
      AND table_name IN ('events', 'repos', 'ingest_log')
    ORDER BY table_name LIMIT 3
"""
SAFE_NODES = frozenset("""
    Select From Table TableAlias Identifier Column Star Alias Literal Null Boolean
    Paren Subquery CTE With Join Where Group Having Qualify Order Ordered Limit Offset
    Window WindowSpec Distinct Filter EQ NEQ GT GTE LT LTE And Or Not Is In Between
    Like ILike Add Sub Mul Div IntDiv Mod Neg Tuple DataType DataTypeParam Interval Var Case
""".split())
# Frozen evaluation anchor: agents must use the injected reference date literal, not a live clock.
SAFE_FUNCTIONS = frozenset("""
    COUNT COUNT_IF SUM AVG MIN MAX MEDIAN STDDEV STDDEV_POP STDDEV_SAMP VAR_POP VAR_SAMP
    ABS ROUND CEIL FLOOR COALESCE NULLIF LOWER UPPER LENGTH CHAR_LENGTH CONCAT
    CAST TRY_CAST CASE IF DATE_TRUNC TIMESTAMP_TRUNC EXTRACT
    CURRENT_DATABASE ROW_NUMBER RANK DENSE_RANK LAG LEAD FIRST_VALUE LAST_VALUE
    ARRAY ARRAY_AGG JSON_EXTRACT JSON_EXTRACT_SCALAR GENERATE_SERIES
""".split())


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


class EmptyInput(Model):
    pass


class TableInput(Model):
    table: TableName


class QueryInput(Model):
    sql: str = Field(min_length=1)


class ColumnInfo(Model):
    name: str
    type: str


class TablesOutput(Model):
    tables: list[TableName]


class DescriptionOutput(Model):
    table: TableName
    columns: list[ColumnInfo]


class SampleOutput(DescriptionOutput):
    rows: list[list[JsonValue]] = Field(max_length=3)


class QueryOutput(Model):
    columns: list[str]
    rows: list[list[JsonValue]] = Field(max_length=MAX_ROWS)
    truncated: bool
    elapsed_ms: float = Field(ge=0)


class ExecutionOutput(Model):
    columns: list[ColumnInfo]
    rows: list[list[JsonValue]]
    truncated: bool
    elapsed_ms: float


class QueryPlan(Model):
    logical_sql: str
    execution_sql: str
    physical_tables: set[tuple[str, str]]


def validate_sql(sql, allowed_tables=QUERY_TABLES, row_cap=MAX_ROWS):
    """Validate SELECT scopes and build a bounded, single-execution lookahead plan."""
    try:
        statements = sqlglot.parse(sql, read="duckdb", error_level=sqlglot.ErrorLevel.RAISE)
        if len(statements) != 1 or not isinstance(statements[0], exp.Select):
            raise ValueError("Only one SELECT statement (optionally WITH) is allowed.")
        tree = statements[0]
        for node in tree.walk():
            if type(node).__name__ in SAFE_NODES:
                pass
            elif isinstance(node, exp.Func):
                name = node.name.upper() if isinstance(node, exp.Anonymous) else node.sql_name()
                if name not in SAFE_FUNCTIONS:
                    raise ValueError(f"Function is not allowed: {name}")
            else:
                raise ValueError(f"SQL construct is not allowed: {type(node).__name__}")
            if isinstance(node, exp.With) and node.args.get("recursive"):
                raise ValueError("Recursive CTEs are not allowed.")
            if isinstance(node, exp.Column) and (node.db or node.catalog):
                raise ValueError("Catalog-qualified and schema-qualified columns are not allowed.")
            if isinstance(node, exp.Table):
                if isinstance(node.this, exp.GenerateSeries):
                    if node.this.args.get("is_end_exclusive"):
                        raise ValueError("Only generate_series is allowed; range is not allowed.")
                    def is_constant(argument):
                        if type(argument) is exp.Literal:
                            return True
                        if type(argument) in (exp.Interval, exp.Cast, exp.Paren):
                            return is_constant(argument.this)
                        return False

                    for argument in node.this.iter_expressions():
                        if not is_constant(argument):
                            raise ValueError("generate_series arguments must be constant literals, intervals, casts, or parentheses.")
                elif not isinstance(node.this, exp.Identifier):
                    raise ValueError("Table functions are not allowed.")
                if node.catalog or (node.db and (node.db.lower(), node.name.lower()) not in allowed_tables):
                    raise ValueError("Catalog-qualified and external schema tables are not allowed.")
        physical_tables = set()
        for scope in traverse_scope(tree):
            for source in scope.sources.values():
                if isinstance(source, exp.Table):
                    if isinstance(source.this, exp.GenerateSeries):
                        continue
                    table = (source.db.lower(), source.name.lower())
                    if table not in allowed_tables:
                        raise ValueError(f"Table is not allowed: {source.sql(dialect='duckdb')}")
                    physical_tables.add(table)
                elif not isinstance(source, Scope):
                    raise ValueError("Only named tables and SELECT subqueries are allowed.")
        limit = tree.args.get("limit")
        if limit is None:
            logical = tree.limit(row_cap)
            execution = tree.limit(row_cap + 1)
        else:
            value = limit.expression
            if not isinstance(limit, exp.Limit) or not isinstance(value, exp.Literal) or not value.is_int:
                raise ValueError("LIMIT must be a nonnegative integer literal.")
            count = int(value.this)
            if count < 0 or limit.args.get("limit_options"):
                raise ValueError("LIMIT must be a nonnegative integer literal without options.")
            logical = tree
            execution = tree.limit(row_cap + 1) if count > row_cap else tree
        return QueryPlan(
            logical_sql=logical.sql(dialect="duckdb"),
            execution_sql=execution.sql(dialect="duckdb"), physical_tables=physical_tables,
        )
    except (sqlglot.errors.SqlglotError, ValueError) as error:
        raise ToolError(str(error)) from error


def json_value(value):
    """Dates use ISO text, decimals use exact text, and non-finite numbers become null."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, Decimal):
        return str(value) if value.is_finite() else None
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, timedelta):
        return value.total_seconds()
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, (list, tuple)):
        return [json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): json_value(item) for key, item in value.items()}
    return str(value)


def open_connection():
    return duckdb.connect(
        str(DATABASE_PATH), read_only=True,
        config={"memory_limit": "2GB", "threads": 2, "enable_external_access": False,
                "autoinstall_known_extensions": False, "autoload_known_extensions": False},
    )


def execute_select(sql, allowed_tables=QUERY_TABLES, row_cap=MAX_ROWS):
    plan = validate_sql(sql, allowed_tables, row_cap)
    started = perf_counter()
    connection = None
    watchdog = None
    finished = threading.Event()
    expired = threading.Event()

    def interrupt_after_deadline():
        if not finished.wait(QUERY_TIMEOUT_SECONDS):
            expired.set()
            # Repeat until the owner finishes, including gaps between execute/fetch calls.
            while not finished.is_set():
                connection.interrupt()
                finished.wait(0.01)

    try:
        connection = open_connection()
        watchdog = threading.Thread(target=interrupt_after_deadline, daemon=True)
        watchdog.start()
        if plan.physical_tables & METADATA_TABLES:
            catalog_plan = validate_sql(CATALOG_SQL, CATALOG_TABLES, 3)
            catalog = connection.execute(catalog_plan.execution_sql).fetchmany(4)
            views = {name for name, kind in catalog if kind != "BASE TABLE"}
            if any(name in views for _, name in plan.physical_tables):
                raise ToolError("Only physical base tables are allowed; views are not allowed.")
        if expired.is_set():
            raise ToolError(f"Query timed out after {QUERY_TIMEOUT_SECONDS:g} seconds.")
        cursor = connection.execute(plan.execution_sql)
        columns = [ColumnInfo(name=column[0], type=str(column[1])) for column in cursor.description]
        fetched = cursor.fetchmany(row_cap + 1)
        rows = [[json_value(value) for value in row] for row in fetched[:row_cap]]
    except duckdb.Error as error:
        if expired.is_set():
            raise ToolError(f"Query timed out after {QUERY_TIMEOUT_SECONDS:g} seconds: {error}") from error
        raise ToolError(str(error)) from error
    finally:
        finished.set()
        if watchdog is not None:
            watchdog.join()
        if connection is not None:
            connection.close()
    if expired.is_set():
        raise ToolError(f"Query timed out after {QUERY_TIMEOUT_SECONDS:g} seconds.")
    return ExecutionOutput(
        columns=columns, rows=rows, truncated=len(fetched) > row_cap,
        elapsed_ms=(perf_counter() - started) * 1000,
    )


server = MCPServer("github-activity", log_level="WARNING")


@server.tool(structured_output=True)
def list_tables() -> TablesOutput:
    """List existing base tables among events, repos, and ingest_log."""
    EmptyInput()
    result = execute_select(CATALOG_SQL, CATALOG_TABLES, 3)
    return TablesOutput(tables=[name for name, kind in result.rows if kind == "BASE TABLE"])


@server.tool(structured_output=True)
def describe_table(table: TableName) -> DescriptionOutput:
    """Describe the columns of one known table, in database order."""
    request = TableInput(table=table)
    result = execute_select(f'SELECT * FROM "{request.table}" LIMIT 0', METADATA_TABLES)
    return DescriptionOutput(table=request.table, columns=result.columns)


@server.tool(structured_output=True)
def sample_values(table: TableName) -> SampleOutput:
    """Return up to three sample rows from one known table."""
    request = TableInput(table=table)
    result = execute_select(f'SELECT * FROM "{request.table}" LIMIT 3', METADATA_TABLES, 3)
    return SampleOutput(table=request.table, columns=result.columns, rows=result.rows)


@server.tool(structured_output=True)
def run_query(sql: str) -> QueryOutput:
    """Run one SELECT over events/repos, returning at most 200 rows with omission detection."""
    request = QueryInput(sql=sql)
    result = execute_select(request.sql)
    return QueryOutput(
        columns=[column.name for column in result.columns], rows=result.rows,
        truncated=result.truncated, elapsed_ms=result.elapsed_ms,
    )


if __name__ == "__main__":
    server.run(transport="stdio")
