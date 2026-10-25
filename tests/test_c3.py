"""Offline C3 feedback coverage and unchanged C2/loop-contract checks."""

import asyncio
from copy import deepcopy
import json
import re

from mcp.types import CallToolResult
import pytest

from agent import context, error_feedback, loop
from eval import run_experiment as experiment
from test_agent_loop import FAKE_KEY, FakeClient, FakeSession, response, tool_call, tool_result


PREFIX = "Error executing tool run_query: "
CASES = [
    ("Only one SELECT statement (optionally WITH) is allowed.", 0),
    ("Function is not allowed: DATE_DIFF", 1),
    ("SQL construct is not allowed: Values", 2),
    ("SQL construct is not allowed: Union", 3),
    ("Function is not allowed: EXISTS", 4),
    ("Only generate_series is allowed; range is not allowed.", 5),
    ("Table functions are not allowed.", 6),
    ("generate_series arguments must be constant literals, intervals, casts, or parentheses.", 7),
    ("Table is not allowed: main.events", 8),
    ("Recursive CTEs are not allowed.", 9),
    ("LIMIT must be a nonnegative integer literal.", 10),
    ("Only physical base tables are allowed; views are not allowed.", 11),
    ("SQL construct is not allowed: Pivot", 12),
    ("Catalog-qualified and schema-qualified columns are not allowed.", 8),
    ("Catalog-qualified and external schema tables are not allowed.", 8),
    ("Only named tables and SELECT subqueries are allowed.", 8),
    ("LIMIT must be a nonnegative integer literal without options.", 10),
    ("SQL construct is not allowed: Intersect", 3),
]


@pytest.fixture(autouse=True)
def no_real_services(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("C3 tests must not access real clients, subprocesses, or credentials")
    for name in ("AsyncOpenAI", "stdio_client", "load_dotenv"):
        monkeypatch.setattr(loop, name, forbidden)
    monkeypatch.setenv("DEEPSEEK_API_KEY", FAKE_KEY)


class BoundsSession(FakeSession):
    async def call_tool(self, name, arguments):
        if name == "run_query" and arguments.get("sql") == context.DATE_BOUNDS_SQL:
            self.calls.append((name, deepcopy(arguments)))
            return CallToolResult(content=[], structured_content={
                "columns": ["first_event", "last_event"],
                "rows": [["2026-10-08T00:02:49", "2026-10-21T23:58:01"]],
                "truncated": False, "elapsed_ms": 0,
            })
        return await super().call_tool(name, arguments)


def execute(config, replies, results):
    client, session = FakeClient(replies), BoundsSession(results)
    trace = asyncio.run(experiment.run_config(
        config, client, session, "Offline C3 question", "Schema/sample bytes",
        experiment.GLOSSARY_PATH.read_text(), FAKE_KEY,
    ))
    return client, session, trace


def test_all_hint_text_is_verbatim_approved_short_and_answer_free():
    approved = (experiment.PROJECT_ROOT / "eval/c3_feasibility.md").read_text()
    approved = approved.split("## Draft generic error mappings — pending approval\n", 1)[1]
    approved = approved.split("\nUncovered/native errors", 1)[0]
    paragraphs = re.findall(r"(?m)^Error category: [^\n]+\nRule: [^\n]+\nGeneric alternative: [^\n]+", approved)
    assert tuple(paragraphs) == error_feedback.MESSAGES
    assert {index for _, index in CASES} == set(range(len(paragraphs)))
    for hint in paragraphs:
        assert len(hint.splitlines()) == 3
        assert not re.search(r"\b[tu]\d{2}\b|\d{4}-\d{2}-\d{2}|huggingface|kubernetes|ollama", hint, re.I)


@pytest.mark.parametrize("reason,index", CASES)
def test_mapping_coverage_and_stable_three_line_feedback(reason, index):
    expected = error_feedback.MESSAGES[index]
    assert error_feedback.whitelist_feedback(PREFIX + reason) == expected
    assert error_feedback.whitelist_feedback(reason) == expected
    assert error_feedback.whitelist_feedback(PREFIX + reason) == expected
    assert len(expected.splitlines()) <= 3


@pytest.mark.parametrize("raw", [
    "Binder Error: Referenced column was not found",
    "Conversion Error: Could not convert string to INT64",
    "Catalog Error: Scalar Function with name missing does not exist",
    "Query timed out after 10 seconds.",
    "Binder Error: Function is not allowed: DATE_DIFF",
    "Unrecognized server rejection\nwith original detail",
    "SQL construct is not allowed: ",
    "  Function is not allowed: DATE_DIFF\r\n",
])
def test_native_and_uncovered_errors_pass_through_byte_for_byte(raw):
    content = PREFIX + raw
    assert error_feedback.whitelist_feedback(content).encode() == content.encode()


def test_same_construct_has_identical_hint_without_echoing_names():
    assert error_feedback.whitelist_feedback(PREFIX + "Function is not allowed: DATE_DIFF") == \
           error_feedback.whitelist_feedback(PREFIX + "Function is not allowed: DAY_OF_WEEK")


def test_c3_loop_only_changes_error_feedback_and_preserves_raw_diagnostic():
    raw = PREFIX + "Function is not allowed: DATE_DIFF"
    replies = [response([tool_call(arguments={"sql": "SELECT DATE_DIFF()"})]),
               response([tool_call("submit_answer", {"sql": "SELECT 42 AS count"}, "submit")]),
               response(text="Done.")]
    runs = [execute(config, deepcopy(replies), [tool_result(raw, error=True), tool_result()])
            for config in ("C2", "C3")]
    old_client, old_session, old_trace = runs[0]
    client, session, trace = runs[1]
    assert json.dumps(client.requests[0]) == json.dumps(old_client.requests[0])
    assert client.requests[1]["messages"][-1]["content"] == error_feedback.MESSAGES[1]
    assert old_client.requests[1]["messages"][-1]["content"] == raw
    restored = deepcopy(client.requests)
    for request in restored:
        for message in request["messages"]:
            if message["role"] == "tool" and message["content"] == error_feedback.MESSAGES[1]:
                message["content"] = raw
    assert json.dumps(restored) == json.dumps(old_client.requests)
    assert session.calls == old_session.calls
    assert trace["tool_calls"][0]["raw_error"] == raw
    assert trace["tool_calls"][0]["result_summary"] == error_feedback.MESSAGES[1]
    assert "raw_error" not in old_trace["tool_calls"][0]
    assert trace["status"] == old_trace["status"] == "completed"
    assert trace["tool_call_count"] == old_trace["tool_call_count"] == 2
    assert trace["answer_sql"] == old_trace["answer_sql"] == "SELECT 42 AS count"
    assert trace["config"] == "C3" and old_trace["config"] == "C2"
    assert "PRECOMPUTED FROZEN DATE BOUNDARIES" in client.requests[0]["messages"][0]["content"]


@pytest.mark.parametrize("config", ["A", "B", "C", "C2"])
def test_other_configs_never_invoke_feedback_and_keep_raw_errors(config, monkeypatch):
    def forbidden(*args):
        raise AssertionError("Feedback must be C3-only")
    monkeypatch.setattr(loop, "whitelist_feedback", forbidden)
    raw = PREFIX + "Function is not allowed: DATE_DIFF"
    replies = [response(text="SELECT DATE_DIFF()")] if config == "A" else [
        response([tool_call()]), response(text="Stopped.")]
    client, session, trace = execute(config, replies, [tool_result(raw, error=True)])
    if config == "A":
        assert trace["final_answer"] == "Baseline stopped: " + raw
    else:
        assert client.requests[1]["messages"][-1]["content"].encode() == raw.encode()
        assert trace["tool_calls"][0]["result_summary"] == raw
        assert "raw_error" not in trace["tool_calls"][0]


@pytest.mark.parametrize("name", ["submit_answer", "list_tables"])
def test_c3_does_not_rewrite_other_tool_errors(name, monkeypatch):
    def forbidden(*args):
        raise AssertionError("Only run_query refusals may be rewritten")
    monkeypatch.setattr(loop, "whitelist_feedback", forbidden)
    arguments = {"sql": "SELECT 1"} if name == "submit_answer" else {}
    raw = PREFIX + "Function is not allowed: EXISTS"
    client, session, trace = execute("C3", [response([tool_call(name, arguments)]), response(text="Done.")],
                                     [tool_result(raw, error=True)])
    assert client.requests[1]["messages"][-1]["content"] == raw
    assert "raw_error" not in trace["tool_calls"][0]
    assert trace["submitted"] is False


def test_c3_native_tool_error_integration_keeps_the_original_text():
    raw = PREFIX + "Binder Error: Referenced column missing was not found"
    client, session, trace = execute("C3", [response([tool_call()]), response(text="Done.")],
                                     [tool_result(raw, error=True)])
    assert client.requests[1]["messages"][-1]["content"] == raw
    assert trace["tool_calls"][0]["result_summary"] == raw
    assert "raw_error" not in trace["tool_calls"][0]
    assert trace["tool_call_count"] == 1


def test_c3_success_and_transport_exceptions_do_not_enter_feedback(monkeypatch):
    def forbidden(*args):
        raise AssertionError("No recognized tool-error result was received")
    monkeypatch.setattr(loop, "whitelist_feedback", forbidden)
    payload = {"columns": ["text"], "rows": [["Function is not allowed: EXISTS"]], "truncated": False}
    client, session, trace = execute("C3", [response([tool_call()]), response(text="Done.")], [tool_result(payload)])
    assert client.requests[1]["messages"][-1]["content"] == json.dumps(payload, ensure_ascii=False)
    client, session, trace = execute("C3", [response([tool_call()])], [RuntimeError("transport failed")])
    assert trace["final_answer"] == "Agent stopped: Tool request failed: transport failed"
    assert trace["tool_call_count"] == 1


@pytest.mark.parametrize("config", ["C2", "C3"])
def test_third_sql_error_still_stops_without_retry_or_fourth_dispatch(config):
    raw = PREFIX + "Function is not allowed: DATE_DIFF"
    replies = [response([tool_call(call_id=str(i)) for i in range(4)])]
    client, session, trace = execute(config, replies, [tool_result(raw, error=True) for _ in range(4)])
    assert trace["tool_call_count"] == 3
    assert len(session.calls) == 4  # One context-bound read plus three deliberative calls.
    assert len(client.requests) == 1
    assert trace["final_answer"] == "Agent stopped: Stopped after 3 consecutive SQL errors."
    assert trace["answer_sql"] is None and trace["submitted"] is False
    assert len({entry["result_summary"] for entry in trace["tool_calls"]}) == 1


@pytest.mark.parametrize("config", ["C2", "C3"])
def test_twelve_call_budget_and_submission_slot_are_unchanged(config):
    metadata = [tool_call("list_tables", {}, str(i)) for i in range(11)]
    replies = [response(metadata + [tool_call("submit_answer", {"sql": "SELECT 42 AS count"}, "submit")]),
               response(text="Done.")]
    client, session, trace = execute(config, replies,
        [tool_result({"tables": ["events"]}) for _ in range(11)] + [tool_result()])
    assert trace["status"] == "completed" and trace["submitted"]
    assert trace["tool_call_count"] == 12 and len(session.calls) == 13
    client, session, trace = execute(config,
        [response([tool_call("list_tables", {}, str(i)) for i in range(13)])],
        [tool_result({"tables": ["events"]}) for _ in range(13)])
    assert trace["tool_call_count"] == 12 and len(session.calls) == 13
    assert "limit of 12 tool calls" in trace["final_answer"]


def test_c3_failed_submissions_remain_raw_and_count_toward_sql_streak():
    raw = PREFIX + "Function is not allowed: EXISTS"
    client, session, trace = execute("C3",
        [response([tool_call("submit_answer", {"sql": "SELECT 1"}, str(i)) for i in range(3)])],
        [tool_result(raw, error=True) for _ in range(3)])
    assert trace["tool_call_count"] == 3 and not trace["submitted"]
    assert all(t["result_summary"] == raw and "raw_error" not in t for t in trace["tool_calls"])
    assert "3 consecutive SQL errors" in trace["final_answer"]


def test_c3_raw_error_and_feedback_trace_redact_the_key():
    raw = PREFIX + "Table is not allowed: " + FAKE_KEY
    client, session, trace = execute("C3", [response([tool_call()]), response(text="Done.")],
                                     [tool_result(raw, error=True)])
    assert trace["tool_calls"][0]["raw_error"] == PREFIX + "Table is not allowed: [REDACTED]"
    assert FAKE_KEY not in json.dumps(trace) + json.dumps(client.requests)


def test_c3_formal_collection_is_blocked_before_credentials_or_history(tmp_path, capsys):
    with pytest.raises(ValueError, match="C3 formal experiments are disabled in Phase B"):
        asyncio.run(experiment.run_experiments([], ("C3",), None, None, "", tmp_path))
    assert list(tmp_path.iterdir()) == []
    assert asyncio.run(experiment.main(["--config", "C3", "--question-id", "t01"])) == 1
    assert "Phase B C3 permits only one selected" in capsys.readouterr().err
