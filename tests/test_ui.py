"""Offline UI, safe chart, unchanged context, and live-progress adapter checks."""

import asyncio
from contextlib import asynccontextmanager
from copy import deepcopy
import json
from types import SimpleNamespace

from mcp.types import CallToolResult, ListToolsResult, Tool
import pytest
from streamlit.testing.v1 import AppTest

from agent import context, loop
from eval import run_experiment as experiment
from ui import app
from ui.charts import infer_chart


KEY = "ui-offline-dummy-key"
TOOLS = [Tool(name=name, input_schema={"type": "object", "properties": {}})
         for name in ("list_tables", "describe_table", "sample_values", "run_query")]


@pytest.fixture(autouse=True)
def no_live_services(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Real model, MCP subprocess, or project .env access is forbidden")
    for name in ("AsyncOpenAI", "stdio_client", "load_dotenv"):
        monkeypatch.setattr(loop, name, forbidden)
    monkeypatch.setenv("DEEPSEEK_API_KEY", KEY)


@pytest.mark.parametrize("columns,rows,kind", [
    (["day", "n"], [["2026-10-08", 1]], "line"),
    (["repo", "n"], [["owner/repo", 3]], "bar"),
    (["repo", "label"], [["owner/repo", "text"]], "table"),
    (["repo", "n"], [], "table"),
    ([], [], "table"),
    (["repo", "n"], [[None, 1]], "table"),
    (["repo", "n"], [[1, 2]], "table"),
    (["day", "n"], [["2026-02-30", 2]], "table"),
    (["day", "n"], [["2026-10-08", 1], ["other", 2]], "table"),
    (["repo", "n"], [["x", True]], "table"),
    (["repo", "n"], [["x", "1"], ["y", 2]], "table"),
    (["repo", "n"], [["x"]], "table"),
])
def test_conservative_chart_type_whitelist(columns, rows, kind):
    assert infer_chart(columns, rows)["type"] == kind


def test_chart_sorts_dates_and_aligns_multiple_numeric_series_without_nonfinite_json():
    result = infer_chart(["day", "first", "second"], [["2026-10-09", 2, float("inf")], ["2026-10-08", 1, 4]])
    assert result == {"type": "line", "x": "day", "x_data": ["2026-10-08", "2026-10-09"],
                      "series": [{"name": "first", "data": [1, 2]}, {"name": "second", "data": [4, None]}]}
    json.dumps(result, allow_nan=False)
    assert infer_chart(["repo", "n"], [["x", None], ["y", float("nan")]]) == {"type": "table"}


def test_chart_html_escapes_untrusted_strings_and_uses_only_local_fixed_bootstrap(tmp_path):
    vendor = tmp_path / "vendor.js"; vendor.write_text("/* developer fixture */ var echarts={};")
    attack = '</script><script src="https://example.invalid/x.js">alert(1)</script>&\u2028'
    spec = infer_chart(["repo", attack], [[attack, 3]])
    html = app.chart_html(spec, vendor)
    data = html.split('<script type="application/json" id="chart-data">', 1)[1].split('</script>', 1)[0]
    assert json.loads(data)["x_data"] == [attack]
    assert '<script src=' not in html and '\\u003c' in data and '\\u2028' in data
    assert "connect-src 'none'" in html and "renderMode:'richText'" in html
    assert "var echarts={};" in html and "series:spec.series.map" in html
    assert app.chart_html({"type": "table"}, vendor) == ""


def test_context_functions_remain_reexported_and_examples_use_dev_text_only():
    assert experiment.lookup_glossary is context.lookup_glossary
    assert experiment.shared_context is context.shared_context
    assert experiment.tool_payload is context.tool_payload
    examples = app.example_questions()
    assert set(examples) == {"d01", "d06", "d09", "d12"}
    assert all(isinstance(value, str) and "reference_sql" not in value for value in examples.values())


def response(calls=None, text=None):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(tool_calls=calls, content=text))],
                           usage=SimpleNamespace(prompt_tokens=10, completion_tokens=2, total_tokens=12))


def call(name, arguments, id):
    return SimpleNamespace(id=id, type="function", function=SimpleNamespace(name=name, arguments=json.dumps(arguments)))


class Client:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.requests = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    async def create(self, **kwargs):
        self.requests.append(deepcopy(kwargs))
        await asyncio.sleep(0.01)
        result = next(self.replies)
        if isinstance(result, Exception):
            raise result
        return result

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


class Session:
    def __init__(self):
        self.calls = []

    async def initialize(self):
        pass

    async def list_tools(self):
        return ListToolsResult(tools=TOOLS)

    async def call_tool(self, name, arguments):
        self.calls.append((name, deepcopy(arguments)))
        if name == "describe_table":
            payload = {"table": arguments["table"], "columns": [{"name": "name", "type": "VARCHAR"}, {"name": "n", "type": "BIGINT"}]}
        elif name == "sample_values":
            payload = {"rows": [["first", 1], ["second", 2], ["third", 3]]}
        else:
            payload = {"columns": ["n"], "rows": [[3]], "truncated": False, "elapsed_ms": 1.0}
        return CallToolResult(content=[], structured_content=payload)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


def runtime(monkeypatch, tmp_path, client):
    (tmp_path / "eval").mkdir()
    (tmp_path / "eval/glossary.md").write_text("## Time conventions\nUTC and frozen dates.")
    monkeypatch.setattr(app, "ROOT", tmp_path)
    monkeypatch.setattr(loop, "load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setattr(loop, "AsyncOpenAI", lambda **kwargs: client)
    session = Session()

    @asynccontextmanager
    async def stdio(parameters):
        assert "DEEPSEEK_API_KEY" not in parameters.env
        yield "reader", "writer"

    monkeypatch.setattr(loop, "stdio_client", stdio)
    monkeypatch.setattr(loop, "ClientSession", lambda *args, **kwargs: session)
    return session


def test_demo_progress_instruments_tools_and_matches_experiment_config_c(monkeypatch, tmp_path):
    replies = [response([call("lookup_glossary", {"term": "time conventions"}, "lookup")]),
               response([call("run_query", {"sql": "SELECT 3 AS n"}, "explore")]),
               response([call("submit_answer", {"sql": "SELECT 3 AS n"}, "submit")]), response(text="Answer: 3")]
    client = Client(replies)
    session = runtime(monkeypatch, tmp_path, client)
    updates = []
    result = asyncio.run(app.run_demo("Question?", on_update=lambda value: updates.append(deepcopy(value))))
    trace = result["trace"]
    assert trace["submitted"] and trace["status"] == "completed"
    assert result["rounds"] == len(trace["api_responses"]) == 4
    assert trace["tool_call_count"] == 3 and len(result["setup_steps"]) == 4
    assert set(result["tool_timings_ms"]) == {"lookup", "explore", "submit"}
    assert all(value >= 0 for value in result["tool_timings_ms"].values())
    assert any(update["trace"]["tool_call_count"] and update["trace"]["status"] != "completed" for update in updates)
    assert len(session.calls) == 6
    assert trace["reference_date"] == "2026-10-22"
    assert KEY not in json.dumps(result)
    reference = Client([response(text="Done.")])

    async def check():
        shared = await context.shared_context(Session())
        await experiment.run_config("C", reference, Session(), "Question?", shared,
                                    (tmp_path / "eval/glossary.md").read_text(), KEY)

    asyncio.run(check())
    assert reference.requests[0]["messages"] == client.requests[0]["messages"]
    assert reference.requests[0]["tools"] == client.requests[0]["tools"]


def test_demo_redacts_provider_errors_without_retry(monkeypatch, tmp_path):
    client = Client([RuntimeError(f"Provider error {KEY}")])
    runtime(monkeypatch, tmp_path, client)
    updates = []
    result = asyncio.run(app.run_demo(f"Question {KEY}", on_update=updates.append))
    assert result["trace"]["status"] == "error" and len(client.requests) == 1
    assert KEY not in json.dumps(result) and KEY not in json.dumps(updates)
    assert "[REDACTED]" in result["trace"]["final_answer"]


def test_demo_missing_key_stops_before_starting_services(monkeypatch):
    monkeypatch.setattr(loop, "load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.delenv("DEEPSEEK_API_KEY")
    result = asyncio.run(app.run_demo("Question?"))
    assert result["trace"]["status"] == "error" and result["rounds"] == 0
    assert "missing or empty" in result["trace"]["final_answer"]


@pytest.mark.parametrize("status,submitted,message,category", [
    ("completed", True, "Done", None),
    ("no_submission", False, "Done", "no_submission"),
    ("error", False, "Stopped at the limit of 12 tool calls", "budget_exceeded"),
    ("error", False, "Stopped after 3 consecutive SQL errors", "sql_error_exhausted"),
])
def test_ui_displays_existing_failure_categories(status, submitted, message, category):
    assert app.failure_category({"status": status, "submitted": submitted, "final_answer": message}) == category


def test_streamlit_initial_layout_and_example_button_do_not_start_runs():
    test = AppTest.from_string("from ui.app import main; main()", default_timeout=15).run()
    assert not test.exception
    assert test.title[0].value == "GitHub Activity Explorer" and test.warning[0].value == app.BANNER
    assert [item.value for item in test.subheader] == ["Answer", "SQL", "Stats"]
    assert test.expander[0].label == "Agent trace"
    assert len(test.button) == 5
    test.button[0].click().run()
    assert test.text_area[0].value == app.example_questions()["d01"]
    assert test.session_state["demo_runs"] == []


def test_streamlit_keeps_error_run_in_session_without_automatic_retry(monkeypatch):
    calls = []

    async def fake_run(question, on_update=None):
        calls.append(question)
        trace = loop.new_trace(question, context.REFERENCE_DATE)
        trace["final_answer"] = "Agent stopped: offline fixture failure"
        result = {"trace": trace, "rounds": 0, "elapsed_ms": 12.0, "setup_steps": [], "tool_timings_ms": {}}
        on_update(result)
        return result

    monkeypatch.setattr(app, "run_demo", fake_run)
    test = AppTest.from_string("from ui.app import main; main()", default_timeout=15).run()
    test.text_area[0].set_value("Question?")
    test.button[-1].click().run()
    assert not test.exception and len(test.session_state["demo_runs"]) == 1
    assert "no_submission" in test.error[0].value
    test.run()
    assert calls == ["Question?"] and len(test.session_state["demo_runs"]) == 1
