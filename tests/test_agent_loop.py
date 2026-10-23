"""Offline agent-loop tests: fake LLM, fake MCP, and temporary trace/config files."""

import asyncio
from contextlib import asynccontextmanager
from copy import deepcopy
from datetime import datetime, timezone
import json
from types import SimpleNamespace

from dotenv import load_dotenv as real_load_dotenv
from mcp.types import CallToolResult, ListToolsResult, TextContent, Tool
import pytest

from agent import loop, run


FAKE_KEY = "dummy-key-only-for-offline-tests"
TOOLS = [
    Tool(name="list_tables", description="List tables", input_schema={"type": "object", "properties": {}}),
    Tool(name="describe_table", description="Describe", input_schema={"type": "object", "properties": {"table": {"type": "string"}}, "required": ["table"]}),
    Tool(name="sample_values", description="Sample", input_schema={"type": "object", "properties": {"table": {"type": "string"}}, "required": ["table"]}),
    Tool(name="run_query", description="Query", input_schema={"type": "object", "properties": {"sql": {"type": "string"}}, "required": ["sql"]}),
]


@pytest.fixture(autouse=True)
def no_real_services(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Real clients, subprocesses, and project .env access are forbidden in tests")
    monkeypatch.setattr(loop, "AsyncOpenAI", forbidden)
    monkeypatch.setattr(loop, "stdio_client", forbidden)
    monkeypatch.setattr(loop, "load_dotenv", forbidden)
    monkeypatch.setenv("DEEPSEEK_API_KEY", FAKE_KEY)


def tool_call(name="run_query", arguments=None, call_id="call-1"):
    arguments = {"sql": "SELECT COUNT(*) FROM events"} if arguments is None else arguments
    return SimpleNamespace(id=call_id, type="function", function=SimpleNamespace(
        name=name, arguments=arguments if isinstance(arguments, str) else json.dumps(arguments),
    ))


def response(calls=None, text=None, prompt=5, completion=2):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(
            content=text, tool_calls=calls, reasoning_content="private reasoning must not be recorded",
        ))],
        usage=SimpleNamespace(prompt_tokens=prompt, completion_tokens=completion, total_tokens=prompt + completion),
    )


def tool_result(payload=None, error=False):
    if error:
        return CallToolResult(content=[TextContent(type="text", text=payload or "Binder Error")], is_error=True)
    return CallToolResult(content=[], structured_content=payload or {
        "columns": ["count"], "rows": [[42]], "truncated": False, "elapsed_ms": 1.0,
    })


class FakeClient:
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


class FakeSession:
    def __init__(self, results=()):
        self.results = iter(results)
        self.calls = []
        self.listed = False
        self.initialized = False
        self.closed = False

    async def list_tools(self):
        self.listed = True
        return ListToolsResult(tools=TOOLS)

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        result = next(self.results)
        if isinstance(result, Exception):
            raise result
        return result

    async def initialize(self):
        self.initialized = True

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        self.closed = True


def execute(client, session, question="How many events?", ref_date="2026-10-22"):
    return asyncio.run(loop.run_loop(client, session, loop.new_trace(question, ref_date), FAKE_KEY))


def test_schema_conversion_copies_discovered_parameters_without_invention():
    converted = loop.openai_tools(TOOLS)
    for actual, original in zip(converted, TOOLS):
        assert actual == {"type": "function", "function": {
            "name": original.name, "description": original.description, "parameters": original.input_schema,
        }}
        assert actual["function"]["parameters"] is not original.input_schema
    converted[3]["function"]["parameters"]["properties"]["sql"]["type"] = "changed"
    assert TOOLS[-1].input_schema["properties"]["sql"]["type"] == "string"


def test_history_call_ids_usage_and_submitted_query():
    query = "SELECT type, COUNT(*) FROM events GROUP BY type"
    client = FakeClient([
        response([tool_call("list_tables", {}, "tables"), tool_call("submit_answer", arguments={"sql": query}, call_id="query")], prompt=11, completion=4),
        response(text="There were 42 push events.", prompt=13, completion=3),
    ])
    session = FakeSession([
        tool_result({"tables": ["events", "repos", "ingest_log"]}),
        tool_result({"columns": ["type", "count"], "rows": [["PushEvent", 42]], "truncated": False, "elapsed_ms": 1.0}),
    ])
    trace = execute(client, session)
    assert session.listed
    assert trace["status"] == "completed"
    assert trace["answer_sql"] == query
    assert trace["answer_columns"] == ["type", "count"]
    assert trace["answer_rows"] == [["PushEvent", 42]]
    assert trace["answer_truncated"] is False
    assert trace["tool_call_count"] == 2
    assert (trace["prompt_tokens"], trace["completion_tokens"]) == (24, 7)
    assert trace["api_responses"] == [
        {"prompt_tokens": 11, "completion_tokens": 4, "total_tokens": 15},
        {"prompt_tokens": 13, "completion_tokens": 3, "total_tokens": 16},
    ]
    history = client.requests[1]["messages"]
    assert [item["role"] for item in history] == ["system", "user", "assistant", "tool", "tool"]
    assert [item["id"] for item in history[2]["tool_calls"]] == ["tables", "query"]
    assert [item["tool_call_id"] for item in history[3:]] == ["tables", "query"]
    assert json.loads(history[-1]["content"])["rows"] == [["PushEvent", 42]]
    assert all(request["model"] == "deepseek-chat" and request["temperature"] == 0 for request in client.requests)
    assert "private reasoning" not in json.dumps(trace)


def test_third_sql_error_stops_and_metadata_does_not_reset_streak():
    calls = [tool_call(call_id="bad1"), tool_call("describe_table", {"table": "events"}, "metadata"),
             tool_call(call_id="bad2"), tool_call(call_id="bad3"), tool_call(call_id="never")]
    client = FakeClient([response(calls)])
    session = FakeSession([tool_result(error=True), tool_result({"columns": []}),
                           tool_result(error=True), tool_result(error=True), tool_result()])
    trace = execute(client, session)
    assert trace["status"] == "error"
    assert "3 consecutive SQL errors" in trace["final_answer"]
    assert trace["tool_call_count"] == len(session.calls) == 4
    assert len(client.requests) == 1
    assert trace["answer_sql"] is None


def test_success_resets_sql_streak_and_later_failure_leaves_unsubmitted_answer_empty():
    queries = [f"SELECT {index} FROM events" for index in range(6)]
    client = FakeClient([response([tool_call(arguments={"sql": sql}, call_id=str(index)) for index, sql in enumerate(queries)])])
    session = FakeSession([tool_result(error=True), tool_result(error=True), tool_result(),
                           tool_result(error=True), tool_result(error=True), tool_result(error=True)])
    trace = execute(client, session)
    assert trace["tool_call_count"] == 6
    assert trace["status"] == "error"
    assert trace["answer_sql"] is None
    assert trace["answer_rows"] is None
    assert trace["submitted"] is False


@pytest.mark.parametrize("ending", ["batch_overflow", "later_tool", "final_text"])
def test_twelve_actual_calls_are_a_hard_limit_but_final_text_is_allowed(ending):
    count = 13 if ending == "batch_overflow" else 12
    responses = [response([tool_call("list_tables", {}, str(index)) for index in range(count)])]
    if ending == "later_tool":
        responses.append(response([tool_call("list_tables", {}, "thirteenth")]))
    elif ending == "final_text":
        responses.append(response(text="Finished after twelve calls."))
    client = FakeClient(responses)
    session = FakeSession([tool_result({"tables": ["events"]}) for _ in range(13)])
    trace = execute(client, session)
    assert trace["tool_call_count"] == len(session.calls) == 12
    assert len(trace["tool_calls"]) == 12
    assert trace["status"] == ("no_submission" if ending == "final_text" else "error")
    if ending != "final_text":
        assert "limit of 12 tool calls" in trace["final_answer"]


def test_reference_date_is_injected_and_default_uses_utc(monkeypatch):
    monkeypatch.setenv("AGENT_REF_DATE", "2026-10-15")
    client = FakeClient([response(text="Done.")])
    trace = execute(client, FakeSession(), ref_date=loop.reference_date())
    prompt = client.requests[0]["messages"][0]["content"]
    assert "Today's date is 2026-10-15 (UTC)." in prompt
    assert "Never use CURRENT_DATE or CURRENT_TIMESTAMP" in prompt
    assert "SQL date literal" in prompt
    assert trace["reference_date"] == "2026-10-15"

    class UTCClock(datetime):
        @classmethod
        def now(cls, tz=None):
            assert tz is timezone.utc
            return datetime(2026, 10, 22, 0, 5, tzinfo=timezone.utc)

    monkeypatch.delenv("AGENT_REF_DATE")
    monkeypatch.setattr(loop, "datetime", UTCClock)
    assert loop.reference_date() == "2026-10-22"
    monkeypatch.setenv("AGENT_REF_DATE", "20261022")
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        loop.reference_date()


@pytest.mark.parametrize("failure", ["api", "tool", "echo"])
def test_key_is_redacted_from_exceptions_results_arguments_and_traces(failure):
    if failure == "api":
        client = FakeClient([RuntimeError(f"Authorization: Bearer {FAKE_KEY}")])
        session = FakeSession()
    elif failure == "tool":
        client = FakeClient([response([tool_call()])])
        session = FakeSession([RuntimeError(f"Tool failure with {FAKE_KEY}")])
    else:
        client = FakeClient([response([tool_call("submit_answer", arguments={"sql": f"SELECT '{FAKE_KEY}'"})]),
                             response(text=f"Answer: {FAKE_KEY}")])
        session = FakeSession([tool_result({"columns": ["value"], "rows": [[FAKE_KEY]], "truncated": False})])
    trace = execute(client, session, question=f"Question with {FAKE_KEY}")
    assert FAKE_KEY not in json.dumps(trace)
    assert FAKE_KEY not in json.dumps(client.requests)
    assert FAKE_KEY not in json.dumps(session.calls)
    assert "[REDACTED]" in json.dumps(trace)
    assert trace["status"] == ("completed" if failure == "echo" else "error")


@pytest.mark.parametrize("call", [tool_call(arguments="{"), tool_call(name="unknown_tool")])
def test_invalid_tool_requests_stop_without_dispatch(call):
    client = FakeClient([response([call])])
    session = FakeSession()
    trace = execute(client, session)
    assert trace["status"] == "error"
    assert trace["tool_call_count"] == 0
    assert not session.calls
    assert len(client.requests) == 1


def test_runtime_loads_only_temp_dotenv_keeps_env_override_and_closes_sessions(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("DEEPSEEK_API_KEY=another-dummy-value\nAGENT_REF_DATE=2020-01-01\n")
    monkeypatch.setattr(loop, "PROJECT_ROOT", tmp_path)
    monkeypatch.setenv("AGENT_REF_DATE", "2026-10-22")
    monkeypatch.setenv("GITHUB_TOKEN", "dummy-github-token")
    client = FakeClient([response(text="Ready.")])
    session = FakeSession()
    loaded = []
    options = []
    processes = []
    cleanup = []

    def load(path, override):
        assert path == tmp_path / ".env"
        loaded.append((path, override))
        return real_load_dotenv(path, override=override)

    def create_client(**kwargs):
        options.append(kwargs)
        return client

    @asynccontextmanager
    async def stdio(parameters):
        processes.append(parameters)
        try:
            yield "reader", "writer"
        finally:
            cleanup.append(True)

    def create_session(reader, writer, read_timeout_seconds):
        assert (reader, writer, read_timeout_seconds) == ("reader", "writer", 20)
        return session

    monkeypatch.setattr(loop, "load_dotenv", load)
    monkeypatch.setattr(loop, "AsyncOpenAI", create_client)
    monkeypatch.setattr(loop, "stdio_client", stdio)
    monkeypatch.setattr(loop, "ClientSession", create_session)
    trace = asyncio.run(loop.answer_question("Question"))
    assert trace["status"] == "no_submission"
    assert loaded == [(tmp_path / ".env", False)]
    assert options == [{"api_key": FAKE_KEY, "base_url": "https://api.deepseek.com", "max_retries": 0, "timeout": 60.0}]
    assert processes[0].command == loop.sys.executable
    assert processes[0].args == ["-B", str(tmp_path / "agent/mcp_server.py")]
    assert processes[0].cwd == str(tmp_path)
    assert "DEEPSEEK_API_KEY" not in processes[0].env
    assert "GITHUB_TOKEN" not in processes[0].env
    assert session.initialized and session.closed and client.closed and cleanup == [True]
    assert trace["reference_date"] == "2026-10-22"


def test_missing_key_fails_before_starting_clients(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY")
    monkeypatch.setattr(loop, "load_dotenv", lambda *args, **kwargs: False)
    trace = asyncio.run(loop.answer_question("Question"))
    assert trace["status"] == "error"
    assert "DEEPSEEK_API_KEY is missing or empty" in trace["final_answer"]
    assert trace["tool_call_count"] == 0


def test_cli_appends_one_trace_per_question_and_prints_sanitized_answer(tmp_path, monkeypatch, capsys):
    destination = tmp_path / "eval/traces.jsonl"
    destination.parent.mkdir()
    destination.write_text('{"existing":true}\n')
    monkeypatch.setattr(run, "TRACE_PATH", destination)

    async def answer(question):
        trace = loop.new_trace(question, "2026-10-22")
        trace.update(final_answer="A sanitized answer.", status="completed" if question == "first" else "error", submitted=question == "first")
        return trace

    monkeypatch.setattr(run, "answer_question", answer)
    assert run.main(["first"]) == 0
    assert run.main(["second"]) == 1
    records = [json.loads(line) for line in destination.read_text().splitlines()]
    assert records[0] == {"existing": True}
    assert [record["question"] for record in records[1:]] == ["first", "second"]
    required = {"question", "final_answer", "answer_sql", "answer_rows", "tool_call_count", "prompt_tokens", "completion_tokens", "status", "submitted"}
    assert all(required <= record.keys() for record in records[1:])
    assert capsys.readouterr().out == "A sanitized answer.\nA sanitized answer.\n"


def test_submit_answer_schema_is_local_and_requires_exact_sql():
    converted = loop.openai_tools(TOOLS)
    assert len(TOOLS) == 4 and len(converted) == 5
    assert [tool["function"]["name"] for tool in converted] == [tool.name for tool in TOOLS] + ["submit_answer"]
    assert converted[-1]["function"]["parameters"] == {
        "type": "object", "properties": {"sql": {"type": "string"}},
        "required": ["sql"], "additionalProperties": False,
    }


def test_scoring_answer_comes_from_submission_not_the_last_exploratory_query():
    answer_sql = "SELECT type, COUNT(*) FROM events GROUP BY type"
    coverage_sql = "SELECT MIN(created_at), MAX(created_at) FROM events"
    client = FakeClient([
        response([tool_call(arguments={"sql": answer_sql}, call_id="candidate"),
                  tool_call(arguments={"sql": coverage_sql}, call_id="coverage"),
                  tool_call("submit_answer", {"sql": answer_sql}, "submission")]),
        response(text="The submitted answer is 43 push events."),
    ])
    session = FakeSession([
        tool_result({"columns": ["type", "count"], "rows": [["PushEvent", 42]], "truncated": False}),
        tool_result({"columns": ["min", "max"], "rows": [["2026-10-08", "2026-10-21"]], "truncated": False}),
        tool_result({"columns": ["type", "count"], "rows": [["PushEvent", 43]], "truncated": False}),
    ])
    trace = execute(client, session)
    assert trace["status"] == "completed" and trace["submitted"] is True
    assert trace["answer_sql"] == answer_sql
    assert trace["answer_columns"] == ["type", "count"]
    assert trace["answer_rows"] == [["PushEvent", 43]]
    assert trace["answer_truncated"] is False
    assert session.calls == [("run_query", {"sql": answer_sql}), ("run_query", {"sql": coverage_sql}),
                             ("run_query", {"sql": answer_sql})]
    assert trace["tool_call_count"] == 3
    assert trace["tool_calls"][-1]["name"] == "submit_answer"
    prompt = client.requests[0]["messages"][0]["content"]
    assert "When you are confident a query's result IS the final answer, you MUST call submit_answer with that exact SQL." in prompt
    assert "After submitting, make no further tool calls; write your final summary as text." in prompt
    assert "Every question requires exactly one submission." in prompt


@pytest.mark.parametrize("explore", [False, True])
def test_plain_text_without_submission_has_no_scoring_answer(explore):
    responses = [response([tool_call()])] if explore else []
    responses.append(response(text="An unsubmitted answer."))
    trace = execute(FakeClient(responses), FakeSession([tool_result()] if explore else []))
    assert trace["status"] == "no_submission" and trace["submitted"] is False
    assert all(trace[field] is None for field in ["answer_sql", "answer_columns", "answer_rows", "answer_truncated"])


@pytest.mark.parametrize("same_batch", [True, False])
def test_post_submission_tools_are_rejected_without_mcp_execution(same_batch):
    sql = "SELECT COUNT(*) FROM events"
    submission = tool_call("submit_answer", {"sql": sql}, "submit")
    trailing = [tool_call(arguments={"sql": "SELECT 999"}, call_id="coverage"),
                tool_call("list_tables", {}, "tables"), tool_call("submit_answer", {"sql": "SELECT 0"}, "duplicate")]
    responses = [response([submission] + trailing)] if same_batch else [response([submission]), response(trailing)]
    responses.append(response(text="The submitted answer remains 42."))
    client = FakeClient(responses)
    session = FakeSession([tool_result()])
    trace = execute(client, session)
    assert trace["submitted"] is True and trace["status"] == "completed"
    assert trace["answer_sql"] == sql and trace["answer_rows"] == [[42]]
    assert session.calls == [("run_query", {"sql": sql})]
    assert trace["tool_call_count"] == 4
    assert all(entry["rejected"] and entry["is_error"] and entry["result_summary"] == "Answer already submitted."
               for entry in trace["tool_calls"][1:])
    replies = [message for message in client.requests[-1]["messages"] if message["role"] == "tool"][-3:]
    assert replies == [{"role": "tool", "tool_call_id": call_id, "content": "Answer already submitted."}
                       for call_id in ["coverage", "tables", "duplicate"]]


@pytest.mark.parametrize("submission_slot", [12, 13])
def test_submission_counts_once_and_only_fits_within_twelve_slots(submission_slot):
    calls = [tool_call("list_tables", {}, str(index)) for index in range(submission_slot - 1)]
    calls.append(tool_call("submit_answer", {"sql": "SELECT COUNT(*) FROM events"}, "submit"))
    client = FakeClient([response(calls), response(text="Final summary.")])
    session = FakeSession([tool_result({"tables": ["events"]}) for _ in range(submission_slot - 1)] + [tool_result()])
    trace = execute(client, session)
    assert trace["tool_call_count"] == len(session.calls) == 12
    assert trace["submitted"] is (submission_slot == 12)
    assert trace["status"] == ("completed" if submission_slot == 12 else "error")
    if submission_slot == 12:
        assert session.calls[-1][0] == "run_query"
        assert trace["answer_rows"] == [[42]]
        assert len(client.requests) == 2
    else:
        assert all(name == "list_tables" for name, _ in session.calls)
        assert trace["answer_sql"] is None
        assert len(client.requests) == 1


@pytest.mark.parametrize("failures", [1, 3])
def test_failed_submission_never_commits_and_uses_sql_error_streak(failures):
    calls = [tool_call("submit_answer", {"sql": "SELECT bad FROM events"}, str(index)) for index in range(failures)]
    client = FakeClient([response(calls), response(text="No valid submission.")])
    session = FakeSession([tool_result(error=True) for _ in range(failures)])
    trace = execute(client, session)
    assert trace["submitted"] is False
    assert all(trace[field] is None for field in ["answer_sql", "answer_columns", "answer_rows", "answer_truncated"])
    assert trace["tool_call_count"] == failures
    assert trace["status"] == ("error" if failures == 3 else "no_submission")
    assert all(name == "run_query" for name, _ in session.calls)
    if failures == 3:
        assert "3 consecutive SQL errors" in trace["final_answer"]
        assert len(client.requests) == 1


def test_failed_submission_can_be_corrected_before_successful_commit():
    client = FakeClient([response([tool_call("submit_answer", {"sql": "SELECT bad"}, "bad")]),
                         response([tool_call("submit_answer", {"sql": "SELECT COUNT(*) FROM events"}, "good")]),
                         response(text="42 events.")])
    session = FakeSession([tool_result(error=True), tool_result()])
    trace = execute(client, session)
    assert trace["submitted"] is True and trace["status"] == "completed"
    assert trace["tool_call_count"] == 2
    assert trace["answer_sql"] == "SELECT COUNT(*) FROM events"
    assert trace["tool_calls"][0]["is_error"] and not trace["tool_calls"][1]["is_error"]


def test_submission_arguments_are_validated_before_dispatch():
    session = FakeSession()
    trace = execute(FakeClient([response([tool_call("submit_answer", {"sql": 42})])]), session)
    assert trace["status"] == "error" and trace["submitted"] is False
    assert trace["tool_call_count"] == 0 and session.calls == []


def test_repeated_post_submission_requests_stop_at_existing_budget():
    client = FakeClient([response([tool_call("submit_answer")])] +
                        [response([tool_call("list_tables", {}, str(index))]) for index in range(12)])
    session = FakeSession([tool_result()])
    trace = execute(client, session)
    assert trace["submitted"] is True and trace["status"] == "error"
    assert trace["tool_call_count"] == 12
    assert trace["answer_rows"] == [[42]]
    assert len(session.calls) == 1 and len(client.requests) == 13
    assert all(entry["result_summary"] == "Answer already submitted." for entry in trace["tool_calls"][1:])
