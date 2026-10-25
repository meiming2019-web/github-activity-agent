"""Offline acceptance checks for additive frozen-date context in config C2."""

import asyncio
from contextlib import asynccontextmanager
from copy import deepcopy
import json

from mcp.types import CallToolResult
import pytest

from agent import context, loop
from eval import run_experiment as experiment
from test_grader_and_experiment import Client, Session, call, database, question, response


KEY = "c2-offline-dummy-key"
FIRST = "2026-10-08T00:02:49"
LAST = "2026-10-21T23:58:01"


@pytest.fixture(autouse=True)
def no_live_services(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("C2 tests must not use real credentials, clients, or subprocesses")
    for name in ("load_dotenv", "AsyncOpenAI", "stdio_client"):
        monkeypatch.setattr(loop, name, forbidden)
    monkeypatch.setenv("DEEPSEEK_API_KEY", KEY)


class BoundsSession(Session):
    def __init__(self):
        super().__init__()
        self.bounds_requests = 0

    async def call_tool(self, name, arguments):
        if name == "run_query" and arguments.get("sql") == context.DATE_BOUNDS_SQL:
            self.bounds_requests += 1
            self.calls.append((name, deepcopy(arguments)))
            return CallToolResult(content=[], structured_content={
                "columns": ["first_event", "last_event"], "rows": [[FIRST, LAST]],
                "truncated": False, "elapsed_ms": 0,
            })
        return await super().call_tool(name, arguments)


def test_c2_adds_only_stable_correct_boundaries_without_spending_loop_budget(database, monkeypatch):
    glossary = experiment.GLOSSARY_PATH.read_text()
    monkeypatch.setenv("AGENT_REF_DATE", "2030-01-01")
    block = context.frozen_date_boundaries(glossary, FIRST, LAST)
    assert block == context.frozen_date_boundaries(glossary, FIRST, LAST)
    windows = json.loads(block.split("\n", 1)[1])["windows"]
    assert windows == {
        "last 7 days": {"start_inclusive": "2026-10-15", "end_exclusive": "2026-10-22"},
        "last week": {"start_inclusive": "2026-10-15", "end_exclusive": "2026-10-22"},
        "previous week": {"start_inclusive": "2026-10-08", "end_exclusive": "2026-10-15"},
        'explicit range "October 8 through October 21, 2026"': {
            "start_inclusive": "2026-10-08", "end_exclusive": "2026-10-22"},
        "full snapshot window": {"start_inclusive": "2026-10-08", "end_exclusive": "2026-10-22"},
    }
    assert "last 14 days" not in block and "past two weeks" not in block
    replies = [response(calls=[call("submit_answer", {"sql": "SELECT 3 AS n"}, "submit")]), response("Done.")]
    clients = [Client(deepcopy(replies)), Client(deepcopy(replies))]
    sessions = [BoundsSession(), BoundsSession()]
    traces = [asyncio.run(experiment.run_config(config, client, session, "Question?", "Schema/sample bytes", glossary, KEY))
              for config, client, session in zip(("C", "C2"), clients, sessions)]
    original, additive = [client.requests[0] for client in clients]
    assert "PRECOMPUTED FROZEN DATE BOUNDARIES" not in original["messages"][0]["content"]
    assert additive["messages"][0]["content"] == original["messages"][0]["content"] + "\n\n" + block
    restored = deepcopy(additive)
    restored["messages"][0]["content"] = original["messages"][0]["content"]
    assert restored == original
    assert [session.bounds_requests for session in sessions] == [0, 1]
    assert all(trace["tool_call_count"] == 1 for trace in traces)
    assert traces[1]["config"] == "C2"


def test_c2_refuses_mismatched_frozen_reference_or_snapshot(monkeypatch):
    glossary = experiment.GLOSSARY_PATH.read_text()
    with pytest.raises(ValueError, match="snapshot UTC dates"):
        context.frozen_date_boundaries(glossary, "2026-10-09T00:00:00", LAST)
    monkeypatch.setattr(context, "REFERENCE_DATE", "2026-10-23")
    with pytest.raises(ValueError, match="reference date"):
        context.frozen_date_boundaries(glossary, FIRST, LAST)


def test_c2_formal_collection_is_blocked_before_credentials_or_history(tmp_path, capsys):
    with pytest.raises(ValueError, match="runs_v3.jsonl"):
        asyncio.run(experiment.run_experiments([question()], ("C2",), None, None, "", tmp_path))
    assert list(tmp_path.iterdir()) == []
    assert asyncio.run(experiment.main(["--config", "C2", "--question-id", "t01"])) == 1
    assert "only one selected d01-d15" in capsys.readouterr().err


def test_c2_cli_runs_one_existing_dev_question_without_scoring_or_files(database, tmp_path, monkeypatch, capsys):
    client = Client([response(calls=[call("submit_answer", {"sql": "SELECT 3 AS n"}, "submit")]), response("Done.")])
    session = BoundsSession()
    monkeypatch.setattr(loop, "load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setattr(loop, "AsyncOpenAI", lambda **kwargs: client)
    monkeypatch.setattr(loop, "ClientSession", lambda *args, **kwargs: session)

    @asynccontextmanager
    async def stdio(parameters):
        yield "reader", "writer"

    def forbidden(*args, **kwargs):
        raise AssertionError("C2 smoke must not grade or write formal results")

    monkeypatch.setattr(loop, "stdio_client", stdio)
    monkeypatch.setattr(experiment, "grade_run", forbidden)
    monkeypatch.setattr(experiment, "run_experiments", forbidden)
    monkeypatch.setattr(experiment, "RESULTS_DIR", tmp_path / "results")
    assert asyncio.run(experiment.main(["--config", "C2", "--questions",
                                       str(experiment.DEVELOPMENT_QUESTIONS_PATH), "--question-id", "d01"])) == 0
    captured = capsys.readouterr().out
    trace = json.loads(captured)
    assert trace["config"] == "C2" and trace["status"] == "completed" and trace["submitted"]
    assert "pass" not in trace and "fail_category" not in trace and KEY not in captured
    assert not (tmp_path / "results").exists()
    assert session.bounds_requests == 1 and trace["tool_call_count"] == 1
