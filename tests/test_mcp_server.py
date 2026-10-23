"""Security, result-boundary, cancellation, and real stdio MCP protocol tests."""

from datetime import date, datetime, time, timedelta
from decimal import Decimal
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from time import perf_counter

import anyio
import duckdb
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import ValidationError
import pytest
import sqlglot


SERVER_PATH = Path(__file__).resolve().parents[1] / "agent/mcp_server.py"
SPEC = importlib.util.spec_from_file_location("activity_mcp_test_module", SERVER_PATH)
app = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = app
SPEC.loader.exec_module(app)


@pytest.fixture
def database(tmp_path, monkeypatch):
    path = tmp_path / "fixture.duckdb"
    with duckdb.connect(str(path)) as connection:
        connection.execute("""
            CREATE TABLE events (
                event_id TEXT PRIMARY KEY, repo_id BIGINT, repo_name TEXT, type TEXT,
                actor TEXT, created_at TIMESTAMP, payload_json TEXT
            )
        """)
        connection.execute("""
            INSERT INTO events
            SELECT CAST(i AS VARCHAR), i + 1, 'owner/repo', 'PushEvent',
                   CASE WHEN i % 2 = 0 THEN NULL ELSE 'actor' END,
                   TIMESTAMP '2026-10-08 00:00:00', '{}'
            FROM range(300) t(i)
        """)
        connection.execute("""
            CREATE TABLE repos (
                repo_id BIGINT PRIMARY KEY, name TEXT, language TEXT, topics TEXT,
                stars BIGINT, forks BIGINT, open_issues BIGINT,
                created_at TIMESTAMP, fetched_at TIMESTAMP
            )
        """)
        connection.execute("INSERT INTO repos (repo_id, name) VALUES (1, 'owner/one'), (2, 'owner/two')")
        connection.execute("CREATE TABLE ingest_log (source_file TEXT PRIMARY KEY, ingested_at TIMESTAMP, rows_seen BIGINT, rows_kept BIGINT)")
        connection.execute("INSERT INTO ingest_log VALUES ('hour.json.gz', TIMESTAMP '2026-10-22 00:00:00', 50000, 300)")
        connection.execute("CREATE TABLE private_answers (answer TEXT)")
        connection.execute("INSERT INTO private_answers VALUES ('not exposed')")
    monkeypatch.setattr(app, "DATABASE_PATH", path)
    return path


def test_metadata_is_bounded_to_three_known_tables(database, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assert app.list_tables().tables == ["events", "ingest_log", "repos"]
    description = app.describe_table("events")
    assert [(column.name, column.type) for column in description.columns] == [
        ("event_id", "VARCHAR"), ("repo_id", "BIGINT"), ("repo_name", "VARCHAR"),
        ("type", "VARCHAR"), ("actor", "VARCHAR"), ("created_at", "TIMESTAMP"), ("payload_json", "VARCHAR"),
    ]
    sample = app.sample_values("events")
    assert len(sample.rows) == 3
    assert sample.rows[0][5] == "2026-10-08T00:00:00"
    assert app.describe_table("ingest_log").columns[0].name == "source_file"
    assert len(app.sample_values("ingest_log").rows) == 1
    for table in ["private_answers", "main.events", "events; DROP TABLE events", "../events"]:
        with pytest.raises(ValidationError):
            app.describe_table(table)
        with pytest.raises(ValidationError):
            app.sample_values(table)


def test_read_only_resource_and_external_access_settings(database, monkeypatch, tmp_path):
    real_connect = duckdb.connect
    calls = []

    def connect(*args, **kwargs):
        calls.append((args, kwargs))
        return real_connect(*args, **kwargs)

    monkeypatch.setattr(app.duckdb, "connect", connect)
    with app.open_connection() as connection:
        settings = dict(connection.execute("""
            SELECT name, value FROM duckdb_settings()
            WHERE name IN ('memory_limit', 'threads', 'enable_external_access',
                           'autoinstall_known_extensions', 'autoload_known_extensions')
        """).fetchall())
        assert settings == {"memory_limit": "1.8 GiB", "threads": "2", "enable_external_access": "false",
                            "autoinstall_known_extensions": "false", "autoload_known_extensions": "false"}
        with pytest.raises(duckdb.Error, match="read-only"):
            connection.execute("CREATE TABLE forbidden (value INTEGER)")
        secret = tmp_path / "fixture-secret.txt"
        secret.write_text("fake local secret")
        with pytest.raises(duckdb.Error):
            connection.execute("SELECT * FROM read_text(?)", [str(secret)])
    assert calls[0][0] == (str(database),)
    assert calls[0][1]["read_only"] is True
    assert calls[0][1]["config"]["memory_limit"] == "2GB"
    assert calls[0][1]["config"]["threads"] == 2


@pytest.mark.parametrize("sql", [
    "SELECT 1; SELECT 2",
    "SELECT 1; DROP TABLE events",
    "DELETE FROM events",
    "INSERT INTO events (event_id) VALUES ('bad')",
    "UPDATE events SET actor = 'bad'",
    "CREATE TABLE bad (n INTEGER)",
    "COPY events TO '/tmp/blocked.csv'",
    "ATTACH '/tmp/other.duckdb' AS other",
    "PRAGMA database_list",
    "SELECT * INTO bad FROM events",
    "VALUES (1)",
    "SELECT 1 UNION ALL SELECT 2",
])
def test_only_one_select_is_accepted_before_database_access(monkeypatch, sql):
    def forbidden():
        raise AssertionError("Rejected SQL must not open a database")
    monkeypatch.setattr(app, "open_connection", forbidden)
    with pytest.raises(ToolError):
        app.run_query(sql)


@pytest.mark.parametrize("sql", [
    "SELECT * FROM ingest_log",
    "SELECT * FROM private_answers",
    "SELECT * FROM information_schema.tables",
    "SELECT * FROM main.events",
    "SELECT * FROM other.main.events",
    "SELECT * FROM '/tmp/secret.parquet'",
    "SELECT * FROM read_csv('/tmp/secret.csv')",
    "SELECT * FROM read_json('https://example.invalid/data')",
    "SELECT * FROM parquet_scan('/tmp/secret.parquet')",
    "SELECT * FROM read_parquet('/tmp/secret.parquet')",
    "SELECT * FROM read_blob('/tmp/secret')",
    "SELECT * FROM query('SELECT * FROM ingest_log')",
    "SELECT * FROM query_table('ingest_log')",
    "SELECT * FROM (SELECT * FROM read_csv('/tmp/secret.csv')) AS events",
    "WITH x AS (SELECT * FROM ingest_log) SELECT * FROM x",
    "WITH events AS (SELECT * FROM private_answers) SELECT * FROM events",
    "SELECT (SELECT COUNT(*) FROM ingest_log) FROM events",
    "SELECT getenv('GITHUB_TOKEN')",
    "SELECT * FROM duckdb_tables()",
    "SELECT * FROM events()",
    "SELECT CURRENT_DATE",
    "SELECT CURRENT_TIMESTAMP",
])
def test_physical_table_and_function_allowlists_reject_bypasses(monkeypatch, sql):
    def forbidden():
        raise AssertionError("Unsafe SQL must fail before database access")
    monkeypatch.setattr(app, "open_connection", forbidden)
    with pytest.raises(ToolError):
        app.run_query(sql)


def test_catalog_sql_survives_function_allowlist(database):
    assert app.list_tables().tables == ["events", "ingest_log", "repos"]


def test_ctes_joins_windows_and_literal_sql_text_are_safe(database):
    result = app.run_query("""
        WITH counts AS (SELECT repo_id, COUNT(*) AS n FROM events GROUP BY repo_id)
        SELECT r.name, c.n, ROW_NUMBER() OVER (ORDER BY r.repo_id) AS position
        FROM counts c JOIN repos r ON c.repo_id = r.repo_id ORDER BY r.repo_id
    """)
    assert result.columns == ["name", "n", "position"]
    assert result.rows == [["owner/one", 1, 1], ["owner/two", 1, 2]]
    assert not result.truncated
    assert app.run_query("SELECT 'DROP TABLE events; read_csv(secret)' AS text").rows == [["DROP TABLE events; read_csv(secret)"]]
    assert app.run_query("SELECT COUNT(*) FROM (SELECT * FROM events WHERE repo_id <= 2) t").rows == [[2]]
    assert app.run_query("SELECT SUM(repo_id) OVER (ORDER BY repo_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) FROM events LIMIT 3").rows == [[1], [3], [6]]


@pytest.mark.parametrize("sql,count,truncated,first", [
    ("SELECT repo_id FROM events WHERE repo_id <= 199 ORDER BY repo_id", 199, False, 1),
    ("SELECT repo_id FROM events WHERE repo_id <= 200 ORDER BY repo_id", 200, False, 1),
    ("SELECT repo_id FROM events WHERE repo_id <= 201 ORDER BY repo_id", 200, True, 1),
    ("SELECT repo_id FROM events ORDER BY repo_id", 200, True, 1),
    ("SELECT repo_id FROM events ORDER BY repo_id LIMIT 5", 5, False, 1),
    ("SELECT repo_id FROM events ORDER BY repo_id LIMIT 200", 200, False, 1),
    ("SELECT repo_id FROM events ORDER BY repo_id LIMIT 201", 200, True, 1),
    ("SELECT repo_id FROM events ORDER BY repo_id LIMIT 500", 200, True, 1),
    ("SELECT repo_id FROM events ORDER BY repo_id LIMIT 5 OFFSET 198", 5, False, 199),
    ("SELECT repo_id FROM events ORDER BY repo_id LIMIT 500 OFFSET 150", 150, False, 151),
    ("SELECT repo_id FROM events ORDER BY repo_id OFFSET 100", 200, False, 101),
    ("SELECT * FROM (SELECT repo_id FROM events ORDER BY repo_id LIMIT 2) t", 2, False, 1),
    ("SELECT repo_id FROM events LIMIT 0", 0, False, None),
])
def test_limits_offsets_and_actual_truncation(database, sql, count, truncated, first):
    result = app.run_query(sql)
    assert result.columns == ["repo_id"]
    assert len(result.rows) == count
    assert result.truncated is truncated
    if count:
        assert result.rows == [[value] for value in range(first, first + count)]
    assert result.elapsed_ms >= 0


def test_logical_limit_200_uses_one_bounded_lookahead_execution(database, monkeypatch):
    plan = app.validate_sql("SELECT repo_id FROM events ORDER BY repo_id")
    assert sqlglot.parse_one(plan.logical_sql).args["limit"].expression.this == "200"
    assert sqlglot.parse_one(plan.execution_sql).args["limit"].expression.this == "201"
    real_open = app.open_connection
    statements = []
    sizes = []

    class ConnectionSpy:
        def __init__(self):
            self.connection = real_open()
        def execute(self, sql):
            statements.append(sql)
            self.connection.execute(sql)
            return self
        def fetchmany(self, count):
            sizes.append(count)
            return self.connection.fetchmany(count)
        @property
        def description(self):
            return self.connection.description
        def interrupt(self):
            self.connection.interrupt()
        def close(self):
            self.connection.close()

    monkeypatch.setattr(app, "open_connection", ConnectionSpy)
    assert app.run_query("SELECT repo_id FROM events ORDER BY repo_id").truncated
    assert statements.count(plan.execution_sql) == 1
    assert all(size <= 201 for size in sizes)
    assert sizes == [4, 201]


def test_json_serialization_preserves_order_nulls_and_duplicates(database):
    result = app.run_query("SELECT actor, actor FROM events WHERE repo_id <= 3 ORDER BY repo_id")
    assert result.columns == ["actor", "actor"]
    assert result.rows == [[None, None], ["actor", "actor"], [None, None]]
    numbers = app.run_query("""
        SELECT DATE '2026-10-08' AS day, TIMESTAMP '2026-10-08 12:34:56' AS instant,
               CAST(12.30 AS DECIMAL(6,2)) AS amount,
               CAST('NaN' AS DOUBLE) AS nan_value, CAST('Infinity' AS DOUBLE) AS infinity, NULL AS empty
    """)
    assert numbers.rows == [["2026-10-08", "2026-10-08T12:34:56", "12.30", None, None, None]]
    json.dumps(numbers.model_dump(), allow_nan=False)
    nested = {"values": [Decimal("0.10"), float("-inf"), date(2026, 10, 8), time(1, 2),
                         timedelta(seconds=3), b"ab", Decimal("NaN")]}
    assert app.json_value(nested) == {"values": ["0.10", None, "2026-10-08", "01:02:00", 3.0, "6162", None]}


def test_original_parse_and_duckdb_errors_are_preserved(database):
    invalid = "SELECT * FROM"
    with pytest.raises(sqlglot.errors.ParseError) as original:
        sqlglot.parse(invalid, read="duckdb", error_level=sqlglot.ErrorLevel.RAISE)
    with pytest.raises(ToolError) as returned:
        app.run_query(invalid)
    assert str(returned.value) == str(original.value)
    query = "SELECT missing_column FROM events"
    plan = app.validate_sql(query)
    with app.open_connection() as connection:
        with pytest.raises(duckdb.Error) as original:
            connection.execute(plan.execution_sql)
    with pytest.raises(ToolError) as returned:
        app.run_query(query)
    assert str(returned.value) == str(original.value)


def test_real_running_query_is_interrupted_and_next_query_succeeds(database, monkeypatch):
    real_open = app.open_connection
    interruptions = []
    connections = []

    class ConnectionSpy:
        def __init__(self):
            self.connection = real_open()
            self.running_expensive_query = False
            self.closed = False
            connections.append(self)
        def execute(self, sql):
            if "CROSS JOIN" in sql:
                self.running_expensive_query = True
            return self.connection.execute(sql)
        def interrupt(self):
            interruptions.append(self.running_expensive_query)
            self.connection.interrupt()
        def close(self):
            self.connection.close()
            self.closed = True

    monkeypatch.setattr(app, "open_connection", ConnectionSpy)
    monkeypatch.setattr(app, "QUERY_TIMEOUT_SECONDS", 0.05)
    started = perf_counter()
    with pytest.raises(ToolError, match="timed out"):
        app.run_query("""
            SELECT SUM(a.repo_id + b.repo_id + c.repo_id + d.repo_id + e.repo_id)
            FROM events a CROSS JOIN events b CROSS JOIN events c
            CROSS JOIN events d CROSS JOIN events e
        """)
    assert perf_counter() - started < 3
    assert any(interruptions), "The watchdog must interrupt the actual expensive SQL"
    assert connections[0].closed
    count = len(interruptions)
    monkeypatch.setattr(app, "QUERY_TIMEOUT_SECONDS", 1.0)
    assert app.run_query("SELECT COUNT(*) FROM events").rows == [[300]]
    assert len(interruptions) == count
    assert connections[-1].closed


def test_views_cannot_hide_unauthorized_tables(database):
    with duckdb.connect(str(database)) as connection:
        connection.execute("DROP TABLE repos")
        connection.execute("CREATE VIEW repos AS SELECT * FROM private_answers")
    with pytest.raises(ToolError, match="views are not allowed"):
        app.run_query("SELECT * FROM repos")
    with pytest.raises(ToolError, match="views are not allowed"):
        app.sample_values("repos")
    assert app.list_tables().tables == ["events", "ingest_log"]


def test_pydantic_models_and_exact_four_sdk_tools(database):
    with pytest.raises(ValidationError):
        app.QueryInput(sql=123)
    with pytest.raises(ValidationError):
        app.QueryInput(sql="")
    with pytest.raises(ValidationError):
        app.TableInput(table="private_answers")
    with pytest.raises(ValidationError):
        app.EmptyInput(extra="not allowed")
    with pytest.raises(ValidationError):
        app.ColumnInfo(name=1, type="VARCHAR")
    with pytest.raises(ValidationError):
        app.QueryOutput(columns=[], rows=[], truncated=False, elapsed_ms=float("nan"))

    async def check():
        tools = {tool.name: tool for tool in await app.server.list_tools()}
        assert set(tools) == {"list_tables", "describe_table", "sample_values", "run_query"}
        assert set(tools["list_tables"].input_schema["properties"]) == set()
        assert set(tools["run_query"].input_schema["properties"]) == {"sql"}
        assert tools["run_query"].input_schema["required"] == ["sql"]
        for name in ["describe_table", "sample_values"]:
            assert set(tools[name].input_schema["properties"]) == {"table"}
            assert tools[name].input_schema["properties"]["table"]["enum"] == ["events", "repos", "ingest_log"]
        assert all(tool.output_schema for tool in tools.values())
        with pytest.raises(ToolError):
            await app.server.call_tool("run_query", {"sql": 123})
        result = await app.server.call_tool("run_query", {"sql": "SELECT COUNT(*) AS n FROM events"})
        assert app.QueryOutput.model_validate(result.structured_content).rows == [[300]]
    anyio.run(check)


def test_read_only_tools_leave_database_bytes_unchanged(database):
    before = hashlib.sha256(database.read_bytes()).hexdigest()
    app.list_tables()
    app.describe_table("repos")
    app.sample_values("events")
    app.run_query("SELECT COUNT(*) FROM events")
    assert hashlib.sha256(database.read_bytes()).hexdigest() == before


def test_real_stdio_handshake_list_and_calls(database, tmp_path):
    bootstrap = (
        "import importlib.util,sys; from pathlib import Path; "
        f"spec=importlib.util.spec_from_file_location('stdio_activity_server', {str(SERVER_PATH)!r}); "
        "module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module); "
        f"module.DATABASE_PATH=Path({str(database)!r}); module.server.run(transport='stdio')"
    )
    parameters = StdioServerParameters(command=sys.executable, args=["-B", "-c", bootstrap], cwd=tmp_path)

    async def check():
        with anyio.fail_after(20):
            async with stdio_client(parameters) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream, read_timeout_seconds=5) as session:
                    initialized = await session.initialize()
                    assert initialized.server_info.name == "github-activity"
                    tools = await session.list_tools()
                    assert {tool.name for tool in tools.tools} == {"list_tables", "describe_table", "sample_values", "run_query"}
                    tables = await session.call_tool("list_tables", {})
                    assert tables.structured_content["tables"] == ["events", "ingest_log", "repos"]
                    description = await session.call_tool("describe_table", {"table": "repos"})
                    assert description.structured_content["columns"][0] == {"name": "repo_id", "type": "BIGINT"}
                    sample = await session.call_tool("sample_values", {"table": "events"})
                    assert len(sample.structured_content["rows"]) == 3
                    query = await session.call_tool("run_query", {"sql": "SELECT repo_id FROM events ORDER BY repo_id"})
                    result = app.QueryOutput.model_validate(query.structured_content)
                    assert len(result.rows) == 200 and result.truncated
                    rejected = await session.call_tool("run_query", {"sql": "DELETE FROM events"})
                    assert rejected.is_error
                    assert "Only one SELECT" in rejected.content[0].text
                    error = await session.call_tool("run_query", {"sql": "SELECT missing_column FROM events"})
                    assert error.is_error and "Binder Error" in error.content[0].text
                    recovery = await session.call_tool("run_query", {"sql": "SELECT COUNT(*) FROM events"})
                    assert recovery.structured_content["rows"] == [[300]]
    anyio.run(check)


def test_case_when_select_returns_correct_results(database):
    result = app.run_query("""
        SELECT repo_id, CASE WHEN repo_id = 1 THEN 'first' ELSE 'other' END AS category
        FROM events WHERE repo_id <= 2 ORDER BY repo_id
    """)
    assert result.columns == ["repo_id", "category"]
    assert result.rows == [[1, "first"], [2, "other"]]
    assert result.truncated is False


def test_generate_series_calendar_left_join_includes_zero_event_days(database):
    result = app.run_query("""
        WITH calendar AS (
            SELECT DATE '2026-10-08' + CAST(day_offset AS INTEGER) AS day
            FROM generate_series(0, 2) AS days(day_offset)
        )
        SELECT c.day, COUNT(e.event_id) AS event_count
        FROM calendar c LEFT JOIN events e ON CAST(e.created_at AS DATE) = c.day
        GROUP BY c.day ORDER BY c.day
    """)
    assert result.columns == ["day", "event_count"]
    assert result.rows == [["2026-10-08", 300], ["2026-10-09", 0], ["2026-10-10", 0]]
    assert len(result.rows) == 3 and result.truncated is False


@pytest.mark.parametrize("sql", [
    "SELECT * FROM generate_series(1, repo_id)",
    "SELECT * FROM generate_series(1, (SELECT MAX(repo_id) FROM events))",
    "SELECT * FROM generate_series(1, ABS(3))",
    "SELECT * FROM generate_series(1, 3, INTERVAL (repo_id) DAY)",
    "SELECT * FROM generate_series(1, CAST(repo_id AS BIGINT))",
    "SELECT * FROM generate_series(1, (SELECT 1))",
    "SELECT * FROM generate_series(1, ABS(2))",
    "SELECT * FROM range(1, 3)",
])
def test_generate_series_rejects_nonliteral_arguments_and_other_table_functions(monkeypatch, sql):
    def forbidden():
        raise AssertionError("Rejected series arguments must not open a database")
    monkeypatch.setattr(app, "open_connection", forbidden)
    with pytest.raises(ToolError):
        app.run_query(sql)


def test_generate_series_accepts_constant_casts_and_parentheses(database):
    result = app.run_query("""
        SELECT day FROM generate_series(
            TIMESTAMP '2026-10-08 00:00:00', TIMESTAMP '2026-10-10 00:00:00', INTERVAL '1 day'
        ) AS g(day) ORDER BY day
    """)
    assert result.columns == ["day"]
    assert result.rows == [["2026-10-08T00:00:00"], ["2026-10-09T00:00:00"], ["2026-10-10T00:00:00"]]
    assert result.truncated is False
    assert app.run_query("SELECT * FROM generate_series((1), CAST((2) AS BIGINT))").rows == [[1], [2]]
