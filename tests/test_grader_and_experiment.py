"""Offline grading and A/B/C experiments with fake LLMs and temporary databases."""

import asyncio
from contextlib import asynccontextmanager
from copy import deepcopy
from datetime import date, datetime, time
import json
from types import SimpleNamespace

import duckdb
from mcp.types import CallToolResult, ListToolsResult, TextContent, Tool
import pytest

from agent import loop, mcp_server
from eval import grader, regrade as regrade_module, run_experiment as experiment


KEY = "offline-evaluation-dummy-key"
TOOLS = [Tool(name=name, input_schema={"type": "object", "properties": properties}) for name, properties in (
    ("list_tables", {}), ("describe_table", {"table": {"type": "string"}}),
    ("sample_values", {"table": {"type": "string"}}), ("run_query", {"sql": {"type": "string"}}),
)]
GLOSSARY = "## Time conventions\nFrozen UTC days.\n\n## Metric definitions\n### new_stars\nDistinct non-null actors on WatchEvent records.\n\n### active_contributors\nAt least three eligible events.\n"


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Real API, subprocess, and project .env access are forbidden")
    for name in ("AsyncOpenAI", "stdio_client", "load_dotenv"):
        monkeypatch.setattr(loop, name, forbidden)
    monkeypatch.setenv("DEEPSEEK_API_KEY", KEY)


@pytest.fixture
def database(tmp_path, monkeypatch):
    path = tmp_path / "fixture.duckdb"
    with duckdb.connect(str(path)) as connection:
        connection.execute("""
            CREATE TABLE events(event_id TEXT, repo_id BIGINT, repo_name TEXT, type TEXT,
                                actor TEXT, created_at TIMESTAMP, payload_json TEXT);
            CREATE TABLE repos(repo_id BIGINT, name TEXT, language TEXT, topics TEXT,
                               stars BIGINT, forks BIGINT, open_issues BIGINT,
                               created_at TIMESTAMP, fetched_at TIMESTAMP);
            CREATE TABLE ingest_log(source_file TEXT);
        """)
        for index in range(3):
            connection.execute("INSERT INTO events VALUES (?, ?, 'owner/repo', 'PushEvent', ?, TIMESTAMP '2026-10-21', '{}')",
                               [str(index), index + 1, f"actor-{index}"])
            connection.execute("INSERT INTO repos VALUES (?, ?, NULL, '[]', 100, 10, 1, TIMESTAMP '2020-01-01', TIMESTAMP '2026-10-22')",
                               [index + 1, f"owner/repo-{index}"])
    monkeypatch.setattr(mcp_server, "DATABASE_PATH", path)
    return path


def question(id="t01", sql="SELECT 3 AS n", columns=None):
    return {"id": id, "question": f"Question {id}?", "reference_sql": sql, "expected_columns": columns or ["n"]}


def submitted(rows=None, columns=None, **updates):
    trace = loop.new_trace("Question?", experiment.REFERENCE_DATE)
    trace.update(status="completed", submitted=True, answer_sql="SELECT 3 AS n",
                 answer_rows=[[3]] if rows is None else rows, answer_columns=columns or ["n"], answer_truncated=False)
    trace.update(updates)
    return trace


def response(text=None, calls=None):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text, tool_calls=calls))],
                           usage=SimpleNamespace(prompt_tokens=7, completion_tokens=3, total_tokens=10))


def call(name, arguments, id="call-1"):
    return SimpleNamespace(id=id, type="function", function=SimpleNamespace(name=name, arguments=json.dumps(arguments)))


class Client:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))
        self.closed = False

    async def create(self, **kwargs):
        self.requests.append(deepcopy(kwargs))
        result = next(self.responses)
        if isinstance(result, Exception):
            raise result
        return result

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        self.closed = True


class Session:
    def __init__(self):
        self.calls = []
        self.initialized = self.closed = False

    async def list_tools(self):
        return ListToolsResult(tools=TOOLS)

    async def call_tool(self, name, arguments):
        self.calls.append((name, deepcopy(arguments)))
        try:
            payload = getattr(mcp_server, name)(**arguments).model_dump()
            return CallToolResult(content=[], structured_content=payload)
        except Exception as error:
            return CallToolResult(content=[TextContent(type="text", text=str(error))], is_error=True)

    async def initialize(self):
        self.initialized = True

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        self.closed = True


@pytest.mark.parametrize("left,right,equal", [
    (1, 1, True), (1, "1", False), (1, 2, False), (None, None, True), (None, "", False),
    (True, 1, False), (1.0, 1.0000009, True), (1.0, 1.000002, False), (0.0, 1e-20, False),
    (date(2026, 10, 22), "2026-10-22", True),
    (datetime(2026, 10, 22, 1, 2), "2026-10-22T01:02:00", True), (time(1, 2), "01:02:00", True),
])
def test_exact_scalars_iso_values_and_relative_float_tolerance(left, right, equal):
    assert grader.same_value(left, right) is equal


def test_tolerant_multiset_matching_reassigns_duplicates():
    assert grader.same_multiset([[1.0], [1.0000015]], [[1.00000075], [0.9999995]])
    assert not grader.same_multiset([[1], [1], [2]], [[1], [2], [2]])
    assert not grader.same_multiset([[1]], [[1], [1]])


@pytest.mark.parametrize("rows,passed", [([[2], [1], [1]], True), ([[1], [2], [2]], False)])
def test_grader_compares_unordered_multisets_preserving_counts(database, rows, passed):
    q = question(sql="SELECT 1 AS n FROM events WHERE repo_id <= 2 UNION ALL SELECT 2 AS n")
    # The server permits SELECT roots, so use an equivalent single SELECT reference.
    q["reference_sql"] = "SELECT CASE WHEN repo_id <= 2 THEN 1 ELSE 2 END AS n FROM events"
    assert grader.grade_run(q, submitted(rows))["pass"] is passed


def test_grader_projects_expected_columns_and_ignores_order(database):
    q = question(sql="SELECT actor, repo_id FROM events", columns=["repo_id", "actor"])
    run = submitted([["extra", 3, "actor-2"], ["extra", 1, "actor-0"], ["extra", 2, "actor-1"]],
                    ["unused", "repo_id", "actor"])
    assert grader.grade_run(q, run)["pass"]
    assert grader.grade_run(question(sql="SELECT CAST(1 AS DOUBLE) AS n"), submitted([[1.0000009]]))["pass"]
    assert not grader.grade_run(question(sql="SELECT CAST(0 AS DOUBLE) AS n"), submitted([[1e-20]]))["pass"]


@pytest.mark.parametrize("updates,category", [
    ({"answer_truncated": True}, "truncated_answer"),
    ({"answer_columns": ["other"], "answer_rows": [[4]]}, "wrong_result_set"),
    ({"submitted": False, "status": "no_submission"}, "no_submission"),
    ({"status": "error", "final_answer": "Stopped at the limit of 12 tool calls"}, "budget_exceeded"),
    ({"status": "error", "final_answer": "Stopped after 3 consecutive SQL errors"}, "sql_error_exhausted"),
    ({"status": "error", "final_answer": "Connection error"}, "no_submission"),
    ({"answer_rows": [[3, 4]]}, "wrong_result_set"),
])
def test_ordered_grading_failure_categories(database, updates, category):
    result = grader.grade_run(question(), submitted(**updates))
    assert not result["pass"] and result["fail_category"] == category
    assert result["diagnostic"]
    assert result["matched_by"] is None


@pytest.mark.parametrize("sql,diagnostic", [
    ("SELECT 3 AS n WHERE FALSE", "EMPTY_REFERENCE"),
    ("SELECT repo_id AS n FROM events CROSS JOIN events b", "REFERENCE_ERROR"),
    ("SELECT * FROM generate_series(1, 201)", "TRUNCATED_REFERENCE"),
    ("SELECT 3 AS other", "REFERENCE_COLUMNS_MISSING"),
])
def test_reference_configuration_errors_do_not_score_incomplete_gold(database, sql, diagnostic):
    result = grader.grade_run(question(sql=sql), submitted())
    assert result["fail_category"] == "configuration_error"
    assert diagnostic in result["diagnostic"]


@pytest.mark.parametrize("content,sql", [
    ("SQL follows:\n```sql\nSELECT 3 AS n\n```\nExplanation.", "SELECT 3 AS n"),
    ("SELECT 3 AS n", "SELECT 3 AS n"),
    ("Ignore SELECT 4. ```SQL SELECT 3 AS n```", "SELECT 3 AS n"),
])
def test_baseline_sql_extraction_prefers_sql_fences(content, sql):
    assert loop.parse_sql(content) == sql


def test_glossary_returns_complete_sections_by_case_insensitive_title():
    text = experiment.GLOSSARY_PATH.read_text()
    hit = experiment.lookup_glossary(text, "NEW_STARS")
    assert hit.startswith("### new_stars") and "Count actor values as stored, including bots." in hit
    assert "### collaboration_events" not in hit
    assert "### active_contributors" in experiment.lookup_glossary(text, "metric definitions")
    assert "2026-10-15" in experiment.lookup_glossary(text, "TIME CONVENTIONS")
    assert "filtered subset" in experiment.lookup_glossary(text, "dataset scope")
    assert "WatchEvent" in experiment.lookup_glossary(text, "event types")
    assert "No glossary sections matched" in experiment.lookup_glossary(text, "unknown metric")
    assert "No glossary sections matched" in experiment.lookup_glossary(text, "")


@pytest.mark.parametrize("config", ["A", "B", "C"])
def test_configs_include_identical_full_static_context_and_fetch_once(database, config):
    session = Session()
    sql = "SELECT 3 AS n"
    replies = [response("```sql\n" + sql + "\n```")] * 2 if config == "A" else [
        response(calls=[call("submit_answer", {"sql": sql})]), response("Done.")
    ] * 2
    client = Client(replies)

    async def execute():
        shared = await experiment.shared_context(session)
        for _ in range(2):
            trace = await experiment.run_config(config, client, session, "How many?", shared, GLOSSARY, KEY)
            assert trace["status"] == "completed" and trace["reference_date"] == "2026-10-22"
            assert trace["tool_call_count"] == 1
            assert len(trace["api_responses"]) == (1 if config == "A" else 2)
        return shared

    shared = asyncio.run(execute())
    for name in ("describe_table", "sample_values"):
        for table in ("events", "repos"):
            assert session.calls.count((name, {"table": table})) == 1
    prompts = [request["messages"][0]["content"] for request in client.requests]
    for prompt in prompts:
        assert shared in prompt
        assert '"event_id", "type": "VARCHAR"' in prompt
        assert '"fetched_at", "type": "TIMESTAMP"' in prompt
        for value in ("actor-0", "actor-1", "actor-2", "owner/repo-0", "owner/repo-1", "owner/repo-2"):
            assert value in prompt
        assert "half-open" in prompt and "2026-10-22" in prompt
        assert "reference_sql" not in prompt
        assert (GLOSSARY in prompt) is (config != "C")
    first = client.requests[0]
    assert first["model"] == "deepseek-chat" and first["temperature"] == 0
    if config == "A":
        assert len(client.requests) == 2 and all("tools" not in request for request in client.requests)
    else:
        names = {tool["function"]["name"] for tool in first["tools"]}
        assert names == {tool.name for tool in TOOLS} | {"submit_answer"} | ({"lookup_glossary"} if config == "C" else set())
        if config == "C":
            assert all(term in prompts[0] for term in ("new_stars", "collaboration_events", "active_contributors", "time conventions", "dataset scope", "event types"))


def test_baseline_executes_once_without_retry_and_sanitizes_errors(database):
    client = Client([response("SELECT missing FROM events")])
    session = Session()
    trace = asyncio.run(loop.run_loop(client, session, loop.new_trace("Question?", "2026-10-22"), KEY, config="A", system_context="Context"))
    assert trace["status"] == "error" and not trace["submitted"]
    assert len(client.requests) == len(session.calls) == trace["tool_call_count"] == 1
    assert "Binder Error" in trace["final_answer"]
    client = Client([RuntimeError(KEY)])
    trace = asyncio.run(loop.run_loop(client, Session(), loop.new_trace(KEY, "2026-10-22"), KEY, config="A", system_context="Context"))
    assert KEY not in json.dumps(trace) and KEY not in json.dumps(client.requests)


def test_local_lookup_counts_toward_budget_and_does_not_reach_mcp(database):
    client = Client([response(calls=[call("lookup_glossary", {"term": "new_stars"}, str(i)) for i in range(12)] +
                             [call("submit_answer", {"sql": "SELECT 3 AS n"}, "thirteenth")])])
    session = Session()
    trace = asyncio.run(loop.run_loop(client, session, loop.new_trace("Q?", "2026-10-22"), KEY,
                                     config="C", system_context="Context", lookup_glossary=lambda term: experiment.lookup_glossary(GLOSSARY, term)))
    assert trace["tool_call_count"] == 12 and not session.calls
    assert trace["status"] == "error" and "limit of 12" in trace["final_answer"]
    assert grader.grade_run(question(), trace)["fail_category"] == "budget_exceeded"


def test_lookup_returns_full_section_without_resetting_sql_error_streak(database):
    calls = [call("run_query", {"sql": "SELECT missing FROM events"}, "one"),
             call("lookup_glossary", {"term": "new_stars"}, "lookup"),
             call("run_query", {"sql": "SELECT missing FROM events"}, "two"),
             call("run_query", {"sql": "SELECT missing FROM events"}, "three")]
    client = Client([response(calls=calls)])
    trace = asyncio.run(experiment.run_config("C", client, Session(), "Q?", "Shared", GLOSSARY, KEY))
    assert trace["tool_call_count"] == 4 and "3 consecutive SQL errors" in trace["final_answer"]
    assert "Distinct non-null actors" in trace["tool_calls"][1]["result_summary"]


def test_runner_interleaves_grades_immediately_and_resumes_normal_wrong_answers(database, tmp_path, monkeypatch):
    questions = [question("t01"), question("t02")]
    directory = tmp_path / "results"; directory.mkdir()
    wrong = {"question_id": "t01", "config": "B", "status": "completed", "pass": False,
             "fail_category": "wrong_result_set", "prompt_tokens": 2, "completion_tokens": 1}
    old_error = dict(wrong, question_id="t02", config="A", status="error", fail_category="no_submission")
    (directory / "runs.jsonl").write_text(json.dumps(wrong) + "\n" + json.dumps(old_error) + "\n")
    events = []

    async def run_config(config, client, session, text, shared, glossary, key):
        events.append(("run", text, config))
        assert "reference_sql" not in shared and "SELECT 3 AS n" not in text
        return submitted(prompt_tokens=7, completion_tokens=3)

    def grade(q, trace):
        events.append(("grade", q["question"]))
        return {"pass": True, "fail_category": None, "diagnostic": "match"}

    monkeypatch.setattr(experiment, "run_config", run_config)
    monkeypatch.setattr(experiment, "grade_run", grade)
    records = asyncio.run(experiment.run_experiments(questions, ("A", "B", "C"), None, Session(), GLOSSARY, directory))
    assert [(row["question_id"], row["config"]) for row in records] == [("t01", "A"), ("t01", "C"), ("t02", "B"), ("t02", "C")]
    assert [event[0] for event in events] == ["run", "grade"] * 4
    assert all(row["latency_ms"] >= 0 for row in records)
    before = (directory / "runs.jsonl").read_bytes()
    session = Session()
    assert asyncio.run(experiment.run_experiments(questions, ("A", "B", "C"), None, session, GLOSSARY, directory)) == []
    assert not session.calls and (directory / "runs.jsonl").read_bytes() == before
    summary = (directory / "summary.md").read_text()
    assert "| A | 1/2 |" in summary and "| B | 1/2 |" in summary
    assert "| t01 | PASS | FAIL (wrong_result_set) | PASS |" in summary
    assert "2/3" not in summary


def test_selector_runs_three_items_and_retains_thirty_question_universe(database, tmp_path, monkeypatch):
    questions = [question(f"t{i:02}") for i in range(1, 31)]
    client = Client([response("SELECT 3 AS n"), response(calls=[call("submit_answer", {"sql": "SELECT 3 AS n"})]),
                     response("Done."), response(calls=[call("submit_answer", {"sql": "SELECT 3 AS n"})]), response("Done.")])
    session = Session()
    records = asyncio.run(experiment.run_experiments(questions, ("A", "B", "C"), client, session, GLOSSARY, tmp_path, KEY, "t01"))
    assert [(row["question_id"], row["config"]) for row in records] == [("t01", "A"), ("t01", "B"), ("t01", "C")]
    assert all(row["pass"] for row in records)
    assert len([item for item in session.calls if item[0] in ("describe_table", "sample_values")]) == 4
    assert len(client.requests) == 5
    summary = (tmp_path / "summary.md").read_text()
    assert summary.count("1/30") == 3 and "| t30 | NOT RUN | NOT RUN | NOT RUN |" in summary
    assert not (tmp_path / "traces.jsonl").exists()


def test_cli_initializes_official_resources_and_only_runs_selected_question(database, tmp_path, monkeypatch):
    qpath = tmp_path / "questions.jsonl"; qpath.write_text(json.dumps(question()) + "\n" + json.dumps(question("t02")))
    gpath = tmp_path / "glossary.md"; gpath.write_text(GLOSSARY)
    monkeypatch.setattr(experiment, "QUESTIONS_PATH", qpath)
    monkeypatch.setattr(experiment, "GLOSSARY_PATH", gpath)
    monkeypatch.setattr(experiment, "RESULTS_DIR", tmp_path / "results")
    loaded = []; options = []; processes = []
    client = Client([response("SELECT 3 AS n")]); session = Session()
    monkeypatch.setattr(loop, "load_dotenv", lambda path, override: loaded.append((path, override)))

    def create_client(**kwargs):
        options.append(kwargs); return client

    @asynccontextmanager
    async def stdio(parameters):
        processes.append(parameters); yield "reader", "writer"

    monkeypatch.setattr(loop, "AsyncOpenAI", create_client)
    monkeypatch.setattr(loop, "stdio_client", stdio)
    monkeypatch.setattr(loop, "ClientSession", lambda *args, **kwargs: session)
    assert asyncio.run(experiment.main(["--config", "A", "--question-id", "t01"])) == 0
    assert loaded == [(experiment.PROJECT_ROOT / ".env", False)]
    assert options == [{"api_key": KEY, "base_url": "https://api.deepseek.com", "max_retries": 0, "timeout": 60.0}]
    assert processes[0].args == ["-B", str(experiment.PROJECT_ROOT / "agent/mcp_server.py")]
    assert session.initialized and session.closed and client.closed
    assert len((tmp_path / "results/runs.jsonl").read_text().splitlines()) == 1


def test_cli_missing_key_stops_before_clients_or_result_files(tmp_path, monkeypatch, capsys):
    qpath = tmp_path / "questions.jsonl"; qpath.write_text(json.dumps(question()))
    gpath = tmp_path / "glossary.md"; gpath.write_text(GLOSSARY)
    monkeypatch.setattr(experiment, "QUESTIONS_PATH", qpath)
    monkeypatch.setattr(experiment, "GLOSSARY_PATH", gpath)
    monkeypatch.setattr(experiment, "RESULTS_DIR", tmp_path / "results")
    monkeypatch.setattr(loop, "load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.delenv("DEEPSEEK_API_KEY")
    assert asyncio.run(experiment.main(["--config", "all", "--question-id", "t01"])) == 1
    assert "missing or empty" in capsys.readouterr().err
    assert not (tmp_path / "results").exists()


def test_shared_block_is_byte_identical_across_all_three_loop_configs(database):
    session = Session()
    blocks = []
    glossary_blocks = []

    async def execute():
        shared = await experiment.shared_context(session)
        for config in ("A", "B", "C"):
            replies = [response("SELECT 3 AS n")] if config == "A" else [
                response(calls=[call("submit_answer", {"sql": "SELECT 3 AS n"})]), response("Done.")]
            client = Client(replies)
            trace = await experiment.run_config(config, client, session, "Q?", shared, GLOSSARY, KEY)
            assert trace["submitted"] and trace["tool_call_count"] == 1
            prompt = client.requests[0]["messages"][0]["content"]
            start = prompt.index("SHARED STATIC CONTEXT\n")
            suffix = "\n\nUse lookup_glossary" if config == "C" else "\n\nFULL GLOSSARY\n"
            end = prompt.index(suffix, start)
            blocks.append(prompt[start:end].encode("utf-8"))
            if config in ("A", "B"):
                glossary_blocks.append(prompt[end:].encode("utf-8"))
        assert len([item for item in session.calls if item[0] in ("describe_table", "sample_values")]) == 4

    asyncio.run(execute())
    assert blocks[0] == blocks[1] == blocks[2]
    assert glossary_blocks[0] == glossary_blocks[1]


def test_reference_sql_and_gold_rows_never_enter_model_requests(database, tmp_path):
    q = question(sql="SELECT CAST(424242 AS BIGINT) AS n /* GOLD_ONLY_SENTINEL */")
    client = Client([response("SELECT 3 AS n"), response(calls=[call("submit_answer", {"sql": "SELECT 3 AS n"})]),
                     response("Done."), response(calls=[call("submit_answer", {"sql": "SELECT 3 AS n"})]), response("Done.")])
    records = asyncio.run(experiment.run_experiments([q], ("A", "B", "C"), client, Session(), GLOSSARY, tmp_path, KEY))
    assert len(records) == 3 and all(record["fail_category"] == "wrong_result_set" for record in records)
    requests = json.dumps(client.requests)
    assert "GOLD_ONLY_SENTINEL" not in requests and "424242" not in requests and "reference_sql" not in requests


@pytest.mark.parametrize("config,message", [("unknown", "config must be A, B, or C"), ("C", "requires lookup_glossary")])
def test_loop_config_validation_stops_before_model_requests(config, message):
    client = Client([])
    trace = asyncio.run(loop.run_loop(client, Session(), loop.new_trace("Q?", "2026-10-22"), KEY, config=config))
    assert trace["status"] == "error" and message in trace["final_answer"]
    assert not client.requests


@pytest.mark.parametrize("status", ["no_submission", "error"])
def test_resume_skips_every_recorded_terminal_outcome(tmp_path, monkeypatch, status):
    record = {"question_id": "t01", "config": "A", "status": status, "pass": False,
              "fail_category": "no_submission", "prompt_tokens": 7, "completion_tokens": 3}
    path = tmp_path / "runs.jsonl"
    path.write_text(json.dumps(record) + "\n")
    before = path.read_bytes()

    async def forbidden(*args, **kwargs):
        raise AssertionError("Recorded outcomes must not fetch context, run, or call a model again")

    monkeypatch.setattr(experiment, "shared_context", forbidden)
    monkeypatch.setattr(experiment, "run_config", forbidden)
    assert asyncio.run(experiment.run_experiments([question()], ("A",), None, None, GLOSSARY, tmp_path)) == []
    assert path.read_bytes() == before
    assert "| t01 | FAIL (no_submission) |" in (tmp_path / "summary.md").read_text()


@pytest.mark.parametrize("first_status", ["no_submission", "error", "completed"])
def test_summary_first_failed_outcome_wins_over_later_completed_success(tmp_path, first_status):
    first = {"question_id": "t01", "config": "A", "status": first_status, "pass": False,
             "fail_category": "wrong_result_set", "prompt_tokens": 7, "completion_tokens": 3}
    later = dict(first, status="completed", **{"pass": True, "fail_category": None})
    path = tmp_path / "summary.md"
    experiment.write_summary([question()], ("A",), [first, later], path)
    summary = path.read_text()
    assert summary.splitlines()[2] == "Each (question, config) pair was attempted exactly once; recorded outcomes are final."
    assert "| A | 0/1 |" in summary
    assert "| t01 | FAIL (wrong_result_set) |" in summary
    assert "| t01 | PASS |" not in summary


@pytest.mark.parametrize("columns,rows,matched_by", [
    (["push_events"], [[3]], "column_values"),
    (["n"], [[3]], "column_names"),
    (["push_events", "extra"], [[3, "ignored"]], "column_values"),
])
def test_grader_reports_name_or_position_matching(database, columns, rows, matched_by):
    result = grader.grade_run(question(), submitted(rows, columns))
    assert result["pass"] and result["fail_category"] is None
    assert result["matched_by"] == matched_by


def test_value_mapping_unequal_values_is_wrong_result_set(database):
    result = grader.grade_run(question(), submitted([[4]], ["push_events"]))
    assert not result["pass"] and result["fail_category"] == "wrong_result_set"
    assert result["matched_by"] is None
    assert "Pinned 0/1" in result["diagnostic"] and "injective value mappings" in result["diagnostic"]


def test_position_fallback_requires_enough_answer_columns(database):
    q = question(sql="SELECT 3 AS first, 4 AS second", columns=["first", "second"])
    result = grader.grade_run(q, submitted([[3]], ["alias"]))
    assert not result["pass"] and result["fail_category"] == "missing_columns"
    assert result["matched_by"] is None
    assert "Expected 2 columns; answer has 1" in result["diagnostic"]


def test_position_does_not_rescue_wrong_values_when_names_match(database):
    result = grader.grade_run(question(), submitted([[3, 4]], ["other", "n"]))
    assert not result["pass"] and result["fail_category"] == "wrong_result_set"
    assert result["matched_by"] is None


@pytest.mark.parametrize("rows,passed", [([[2], [1], [1]], True), ([[1], [2], [2]], False)])
def test_position_fallback_preserves_duplicate_counts(database, rows, passed):
    q = question(sql="SELECT CASE WHEN repo_id <= 2 THEN 1 ELSE 2 END AS n FROM events")
    result = grader.grade_run(q, submitted(rows, ["alias"]))
    assert result["pass"] is passed
    assert result["matched_by"] == ("column_values" if passed else None)


def test_position_fallback_preserves_relative_only_float_tolerance(database):
    near = grader.grade_run(question(sql="SELECT CAST(1 AS DOUBLE) AS n"), submitted([[1.0000009]], ["alias"]))
    tiny = grader.grade_run(question(sql="SELECT CAST(0 AS DOUBLE) AS n"), submitted([[1e-20]], ["alias"]))
    assert near["pass"] and near["matched_by"] == "column_values"
    assert not tiny["pass"] and tiny["matched_by"] is None


def test_position_fallback_cannot_bypass_row_shape_validation(database):
    result = grader.grade_run(question(), submitted([[3, 4]], ["alias"]))
    assert not result["pass"] and result["fail_category"] == "wrong_result_set"
    assert result["matched_by"] is None


@pytest.mark.parametrize("columns,rows,matched_by", [
    (["beta", "alias"], [[2, 1]], "name_plus_values"),
    (["x", "y"], [[2, 1]], "column_values"),
    (["unused", "ALPHA", "alias"], [[99, 1, 2]], "name_plus_values"),
    (["BETA", "Alpha"], [[2, 1]], "column_names"),
])
def test_v2_pins_partial_names_and_searches_unused_columns(database, columns, rows, matched_by):
    q = question(sql="SELECT 1 AS alpha, 2 AS beta", columns=["alpha", "beta"])
    result = grader.grade_run(q, submitted(rows, columns))
    assert result["pass"] and result["matched_by"] == matched_by
    assert all(grader.grade_run(q, submitted(rows, columns)) == result for _ in range(3))


@pytest.mark.parametrize("columns,rows", [
    (["beta", "alpha"], [[1, 2]]),
    (["alpha", "alias"], [[2, 1]]),
    (["ALPHA", "alpha", "beta"], [[9, 1, 2]]),
])
def test_v2_never_reassigns_pinned_names_even_with_case_collisions(database, columns, rows):
    q = question(sql="SELECT 1 AS alpha, 2 AS beta", columns=["alpha", "beta"])
    results = [grader.grade_run(q, submitted(rows, columns)) for _ in range(3)]
    assert all(result == results[0] for result in results)
    assert results[0]["fail_category"] == "wrong_result_set" and results[0]["matched_by"] is None


def test_v2_more_than_four_unmatched_columns_use_remaining_positions(database):
    columns = [f"c{i}" for i in range(5)]
    q = question(sql="SELECT 1 AS c0, 2 AS c1, 3 AS c2, 4 AS c3, 5 AS c4", columns=columns)
    aliases = [f"alias{i}" for i in range(5)]
    assert grader.grade_run(q, submitted([[1, 2, 3, 4, 5]], aliases))["matched_by"] == "column_values"
    assert grader.grade_run(q, submitted([[5, 4, 3, 2, 1]], aliases))["fail_category"] == "wrong_result_set"


def regrade_inputs(tmp_path):
    qpath = tmp_path / "questions.jsonl"
    runs = tmp_path / "runs.jsonl"
    summary = tmp_path / "summary.md"
    output = tmp_path / "runs_v2.jsonl"
    qpath.write_text(json.dumps(question()) + "\n")
    records = []
    for config in ("A", "B", "C"):
        records.append({**submitted([[3]], ["alias"]), "question_id": "t01", "config": config,
                        "pass": False, "fail_category": "missing_columns", "matched_by": None,
                        "diagnostic": "Old name/position grading failed.", "latency_ms": 1.25})
    runs.write_text("".join(json.dumps(record) + "\n" for record in records))
    summary.write_bytes(b"# Frozen v1 summary\nOriginal result bytes.\n")
    return {"questions_path": qpath, "runs_path": runs, "output_path": output, "summary_path": summary}


def test_offline_regrade_is_deterministic_and_preserves_frozen_provenance(database, tmp_path):
    paths = regrade_inputs(tmp_path)
    frozen = paths["runs_path"].read_bytes()
    prefix = paths["summary_path"].read_bytes()
    first = regrade_module.regrade(**paths)
    output = paths["output_path"].read_bytes()
    summary = paths["summary_path"].read_bytes()
    second = regrade_module.regrade(**paths)
    assert first == second
    assert paths["output_path"].read_bytes() == output
    assert paths["summary_path"].read_bytes() == summary and summary.startswith(prefix)
    assert summary.count(regrade_module.HEADING.encode()) == 1
    assert paths["runs_path"].read_bytes() == frozen
    records = [json.loads(line) for line in output.splitlines()]
    assert len(records) == 3 and all(record["pass"] and record["matched_by"] == "column_values" for record in records)
    assert all(record["v1_pass"] is False and record["latency_ms"] == 1.25 for record in records)
    assert records[0]["source_record_line"] == 1 and records[0]["answer_rows"] == [[3]]
    assert first["scores"]["A"] == {"v1": 0, "v2": 1, "delta": 1, "questions": 1}


def test_offline_regrade_missing_answer_data_blocks_without_writes(database, tmp_path):
    paths = regrade_inputs(tmp_path)
    records = [json.loads(line) for line in paths["runs_path"].read_text().splitlines()]
    del records[0]["answer_rows"]
    paths["runs_path"].write_text("".join(json.dumps(record) + "\n" for record in records))
    summary = paths["summary_path"].read_bytes()
    with pytest.raises(ValueError, match="Stored answer data missing"):
        regrade_module.regrade(**paths)
    assert not paths["output_path"].exists() and paths["summary_path"].read_bytes() == summary


def test_offline_regrade_explicit_null_failure_data_uses_recorded_error(database, tmp_path):
    paths = regrade_inputs(tmp_path)
    records = [json.loads(line) for line in paths["runs_path"].read_text().splitlines()]
    records[0].update(status="error", submitted=False, answer_rows=None, answer_columns=None,
                      answer_sql=None, answer_truncated=None, final_answer="Stopped after 3 consecutive SQL errors.")
    paths["runs_path"].write_text("".join(json.dumps(record) + "\n" for record in records))
    regrade_module.regrade(**paths)
    first = json.loads(paths["output_path"].read_text().splitlines()[0])
    assert first["fail_category"] == "sql_error_exhausted" and first["answer_rows"] is None


def test_offline_regrade_duplicate_records_keep_first_write(database, tmp_path):
    paths = regrade_inputs(tmp_path)
    records = [json.loads(line) for line in paths["runs_path"].read_text().splitlines()]
    duplicate = dict(records[0], answer_rows=[[999]], **{"pass": True})
    with paths["runs_path"].open("a") as stream:
        stream.write(json.dumps(duplicate) + "\n")
    result = regrade_module.regrade(**paths)
    outputs = [json.loads(line) for line in paths["output_path"].read_text().splitlines()]
    assert result["records"] == 3 and outputs[0]["source_record_line"] == 1 and outputs[0]["answer_rows"] == [[3]]


def test_t07_audit_reports_missing_evidence_instead_of_asserting_claim(database):
    records = [{"question_id": "t07", "config": "A", "diagnostic": "Function is not allowed: TIME_TO_STR"},
               {"question_id": "t07", "config": "B", "fail_category": "sql_error_exhausted", "diagnostic": "Stopped after 3 consecutive SQL errors."},
               {"question_id": "t07", "config": "C", "fail_category": "sql_error_exhausted", "diagnostic": "Stopped after 3 consecutive SQL errors."}]
    evidence = regrade_module.t07_evidence(records)
    assert "t07 evidence discrepancy" in evidence and "Monday=1, Sunday=7" in evidence
    assert "cannot be verified" in evidence and evidence != regrade_module.T07_CLAIM


def test_regrade_main_reports_blocker_without_agent_calls(monkeypatch, capsys):
    def blocked(**kwargs):
        raise ValueError("Stored answer data missing")
    monkeypatch.setattr(regrade_module, "regrade", blocked)
    assert regrade_module.main([]) == 1
    assert "Offline re-scoring blocked: Stored answer data missing" in capsys.readouterr().err


def test_dry_run_lists_new_batch_without_credentials_services_network_or_writes(tmp_path, monkeypatch, capsys):
    import socket
    questions = [question(f"{prefix}{number:02}") for prefix in ("t", "u") for number in range(1, 31)]
    path = tmp_path / "combined.jsonl"
    path.write_text("".join(json.dumps(q) + "\n" for q in questions))
    results = tmp_path / "results"; results.mkdir()
    statuses = ("completed", "no_submission", "error")
    history = [{"question_id": f"t{number:02}", "config": config, "status": statuses[index]}
               for number in range(1, 31) for index, config in enumerate(("A", "B", "C"))]
    (results / "runs.jsonl").write_text("".join(json.dumps(row) + "\n" for row in history))
    (results / "summary.md").write_bytes(b"Frozen summary bytes.\n")
    before = {p.name: p.read_bytes() for p in results.iterdir()}
    monkeypatch.setattr(experiment, "RESULTS_DIR", results)
    monkeypatch.setattr(experiment, "GLOSSARY_PATH", tmp_path / "must-not-read.md")
    monkeypatch.setattr(experiment, "QUESTIONS_PATH", tmp_path / "unselected-default.jsonl")

    def forbidden(*args, **kwargs):
        raise AssertionError("Dry-run must not load credentials, start services, grade, or call the network")

    for name in ("load_dotenv", "AsyncOpenAI", "stdio_client", "ClientSession"):
        monkeypatch.setattr(loop, name, forbidden)
    for name in ("shared_context", "run_config", "grade_run"):
        monkeypatch.setattr(experiment, name, forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(asyncio.BaseEventLoop, "create_connection", forbidden)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    assert asyncio.run(experiment.main(["--config", "all", "--questions", str(path), "--dry-run"])) == 0
    lines = capsys.readouterr().out.splitlines()
    assert json.loads(lines[0]) == {"questions": 60, "skipped": 90, "pending": 90}
    assert lines[1:] == [f"u{number:02}-{config}" for number in range(1, 31) for config in ("A", "B", "C")]
    assert {p.name: p.read_bytes() for p in results.iterdir()} == before


@pytest.mark.parametrize("selector,skipped,pending", [(None, 3, ["u01-A", "u01-B", "u01-C"]), ("t01", 3, [])])
def test_dry_run_default_question_path_and_existing_selector(tmp_path, monkeypatch, capsys, selector, skipped, pending):
    path = tmp_path / "default.jsonl"
    path.write_text(json.dumps(question("t01")) + "\n" + json.dumps(question("u01")))
    results = tmp_path / "results"; results.mkdir()
    (results / "runs.jsonl").write_text("".join(json.dumps({"question_id": "t01", "config": config, "status": "error"}) + "\n" for config in ("A", "B", "C")))
    monkeypatch.setattr(experiment, "QUESTIONS_PATH", path)
    monkeypatch.setattr(experiment, "RESULTS_DIR", results)
    args = ["--config", "all", "--dry-run"] + (["--question-id", selector] if selector else [])
    assert asyncio.run(experiment.main(args)) == 0
    lines = capsys.readouterr().out.splitlines()
    assert json.loads(lines[0]) == {"questions": 2, "skipped": skipped, "pending": len(pending)}
    assert lines[1:] == pending
    assert not (results / "summary.md").exists()


def test_selected_question_file_reaches_execution_grading_and_sixty_question_summary(database, tmp_path, monkeypatch):
    path = tmp_path / "sixty.jsonl"
    path.write_text("".join(json.dumps(question(f"{prefix}{number:02}")) + "\n" for prefix in ("t", "u") for number in range(1, 31)))
    glossary = tmp_path / "glossary.md"; glossary.write_text(GLOSSARY)
    monkeypatch.setattr(experiment, "QUESTIONS_PATH", tmp_path / "unselected.jsonl")
    monkeypatch.setattr(experiment, "GLOSSARY_PATH", glossary)
    monkeypatch.setattr(experiment, "RESULTS_DIR", tmp_path / "results")
    client = Client([response("SELECT 3 AS n")]); session = Session()
    monkeypatch.setattr(loop, "load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setattr(loop, "AsyncOpenAI", lambda **kwargs: client)

    @asynccontextmanager
    async def stdio(parameters):
        yield "reader", "writer"

    monkeypatch.setattr(loop, "stdio_client", stdio)
    monkeypatch.setattr(loop, "ClientSession", lambda *args, **kwargs: session)
    assert asyncio.run(experiment.main(["--config", "A", "--questions", str(path), "--question-id", "u01"])) == 0
    assert client.requests[0]["messages"][1]["content"] == "Question u01?"
    record = json.loads((tmp_path / "results/runs.jsonl").read_text())
    assert record["question_id"] == "u01" and record["pass"]
    summary = (tmp_path / "results/summary.md").read_text()
    assert "| A | 1/60 |" in summary and "| u30 | NOT RUN |" in summary


@pytest.mark.parametrize("use_selected_path", [False, True])
def test_regrade_cli_forwards_selected_question_lookup_without_regrading(tmp_path, monkeypatch, capsys, use_selected_path):
    selected = tmp_path / "selected.jsonl"
    calls = []

    def fake_regrade(**kwargs):
        calls.append(kwargs)
        return {"selected": str(kwargs["questions_path"])}

    monkeypatch.setattr(regrade_module, "regrade", fake_regrade)
    args = ["--questions", str(selected)] if use_selected_path else []
    assert regrade_module.main(args) == 0
    expected = selected if use_selected_path else regrade_module.ROOT / "eval/github_test_questions.jsonl"
    assert calls == [{"questions_path": expected}]
    assert json.loads(capsys.readouterr().out) == {"selected": str(expected)}
