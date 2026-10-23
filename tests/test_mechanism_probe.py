"""Offline checks for the separately declared, observed config C probe."""

import asyncio
from copy import deepcopy
import json

import pytest

from agent import loop
from eval import mechanism_probe as probe, run_experiment as experiment
from test_grader_and_experiment import Client, Session, call, database, question, response, submitted


KEY = "offline-probe-dummy-key"
TRUE_T = {"t04", "t09", "t10", "t15", "t16", "t19", "t24", "t27"}
TRUE_U = {"u02", "u05", "u09", "u10", "u11", "u12", "u14", "u17", "u19", "u20", "u21", "u22", "u23"}


@pytest.fixture(autouse=True)
def no_live_calls(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Offline probe tests must not call real services or read project credentials")
    for name in ("AsyncOpenAI", "stdio_client", "load_dotenv"):
        monkeypatch.setattr(loop, name, forbidden)
    monkeypatch.setenv("DEEPSEEK_API_KEY", KEY)


def questions():
    return [{**question(f"{prefix}{number:02}"), "needs_glossary": f"{prefix}{number:02}" in TRUE_T | TRUE_U}
            for prefix in ("t", "u") for number in range(1, 31)]


def test_selection_is_exactly_twenty_one_plus_five_controls():
    selected = probe.select_questions(questions())
    assert len(selected) == 26
    assert {q["id"] for q in selected} == TRUE_T | TRUE_U | probe.CONTROLS
    assert [q["id"] for q in selected] == sorted(q["id"] for q in selected)


@pytest.mark.parametrize("change", ["missing_true", "true_control", "duplicate"])
def test_selection_mismatch_stops_instead_of_changing_the_probe(change):
    data = questions()
    if change == "missing_true":
        next(q for q in data if q["id"] == "t04")["needs_glossary"] = False
    elif change == "true_control":
        data[0]["needs_glossary"] = True
    else:
        data.append(deepcopy(data[0]))
    with pytest.raises(ValueError):
        probe.select_questions(data)


def test_observation_preserves_exact_config_c_prompt_callback_and_full_lookup(database):
    glossary = "## Time conventions\n" + "Full exact returned content. " * 80
    q = {**question("t04"), "needs_glossary": True}
    replies = [response(calls=[call("lookup_glossary", {"term": "time conventions"}, "lookup"),
                              call("submit_answer", {"sql": "SELECT 3 AS n"}, "submit")]), response("Done.")]
    client = Client(deepcopy(replies)); session = Session()
    record = asyncio.run(probe.probe_question(q, client, session, "Shared bytes", glossary, KEY))
    observed = record["lookup_calls"][0]
    assert observed["arguments"] == {"term": "time conventions"}
    assert observed["returned_text"] == probe.lookup_glossary(glossary, "time conventions") and len(observed["returned_text"]) > 1000
    assert observed["retrieval_hit"] and record["pass"]
    assert record["tool_names"] == ["lookup_glossary", "submit_answer"]
    assert record["tool_call_count"] == 2 and len(session.calls) == 1
    reference_client = Client(deepcopy(replies))
    asyncio.run(experiment.run_config("C", reference_client, Session(), q["question"], "Shared bytes", glossary, KEY))
    assert client.requests[0] == reference_client.requests[0]
    assert observed["returned_text"] == client.requests[1]["messages"][3]["content"]
    assert observed["returned_text"] == reference_client.requests[1]["messages"][3]["content"]


def test_lookup_miss_is_called_but_not_successful_retrieval(database):
    q = {**question("t04"), "needs_glossary": True}
    client = Client([response(calls=[call("lookup_glossary", {"term": "not present"}, "lookup")]), response("No submission.")])
    record = asyncio.run(probe.probe_question(q, client, Session(), "Shared", "## Other\nDefinition", KEY))
    assert record["lookup_calls"] and not record["lookup_calls"][0]["retrieval_hit"]
    assert record["fail_category"] == "no_submission"


def test_standard_runner_logs_actual_tool_order_including_pseudo_tools(database, tmp_path):
    client = Client([response(calls=[call("lookup_glossary", {"term": "metric"}, "lookup"),
                                    call("submit_answer", {"sql": "SELECT 3 AS n"}, "submit")]), response("Done.")])
    records = asyncio.run(experiment.run_experiments([question()], ("C",), client, Session(), "## Metric\nText", tmp_path, KEY))
    assert records[0]["tool_names"] == ["lookup_glossary", "submit_answer"]
    assert records[0]["tool_call_count"] == 2 and len(client.requests) == 2


def test_probe_resume_skips_recorded_failures_and_keeps_independent_file(database, tmp_path):
    output = tmp_path / "mechanism_probe.jsonl"
    old = {**submitted(status="error", submitted=False), "question_id": "t04", "config": "C",
           "needs_glossary": True, "declaration": probe.DECLARATION, "source_hashes": {"frozen": "hash"},
           "lookup_calls": [], "pass": False, "fail_category": "no_submission"}
    output.write_text(json.dumps(old) + "\n")
    prefix = output.read_bytes()
    selected = [{**question("t04"), "needs_glossary": True}, {**question("t01"), "needs_glossary": False}]
    client = Client([response(calls=[call("submit_answer", {"sql": "SELECT 3 AS n"}, "submit")]), response("Done.")])
    records = asyncio.run(probe.run_probes(selected, client, Session(), "Glossary", output, {"frozen": "hash"}, KEY))
    assert len(records) == 2 and output.read_bytes().startswith(prefix)
    assert records[0]["status"] == "error" and records[1]["question_id"] == "t01"
    before = output.read_bytes()
    assert asyncio.run(probe.run_probes(selected, None, None, "Glossary", output, {"frozen": "hash"}, KEY)) == records
    assert output.read_bytes() == before and not (tmp_path / "runs.jsonl").exists()


def test_probe_records_provider_failure_without_retry_and_redacts_key(database, tmp_path):
    client = Client([RuntimeError(KEY)])
    q = {**question("t04"), "needs_glossary": True}
    records = asyncio.run(probe.run_probes([q], client, Session(), "Glossary", tmp_path / "probe.jsonl", {}, KEY))
    assert len(records) == 1 and records[0]["status"] == "error" and len(client.requests) == 1
    assert KEY not in json.dumps(records)


def test_trigger_summary_separates_call_retrieval_and_t_corrected_v2_consistency():
    selected = probe.select_questions(questions())
    records = [{"question_id": q["id"], "config": "C", "needs_glossary": q["needs_glossary"],
                "lookup_calls": [], "pass": True, "fail_category": None} for q in selected]
    records[0]["lookup_calls"] = [{"retrieval_hit": False}]
    next(r for r in records if r["question_id"] == "t04")["lookup_calls"] = [{"retrieval_hit": True}]
    next(r for r in records if r["question_id"] == "u11")["pass"] = False
    corrected = [{"question_id": id, "config": "C", "pass": True} for id in TRUE_T]
    summary = probe.summarize(records, corrected)
    assert summary["matrix"] == {"TP": 1, "FN": 20, "FN_pass": 19, "FN_fail": 1, "FP": 1, "TN": 4,
                                  "glossary_questions": 21, "control_questions": 5,
                                  "glossary_successful_retrieval": 1, "control_successful_retrieval": 0}
    assert summary["t_total"] == summary["t_consistent"] == 8


def test_probe_main_rejects_wrong_selection_before_credentials_or_clients(tmp_path, monkeypatch, capsys):
    for name in ("QUESTIONS_PATH", "GLOSSARY_PATH", "FROZEN_PATH", "CORRECTED_PATH"):
        path = tmp_path / (name + ".json")
        path.write_text("[]" if name == "GLOSSARY_PATH" else "")
        monkeypatch.setattr(probe, name, path)
    assert asyncio.run(probe.main()) == 1
    assert "Probe selection mismatch" in capsys.readouterr().err


def test_remaining_controls_extends_to_sixty_and_preserves_terminal_errors(database, tmp_path):
    data = questions()
    original = probe.select_questions(data)
    records = [{"question_id": q["id"], "config": "C", "status": "error"} for q in original]
    selected = probe.select_remaining_controls(data, records)
    pending = [q for q in selected if q["id"] not in {r["question_id"] for r in records}]
    assert len(selected) == 60 and len(pending) == 34
    assert all(q["needs_glossary"] is False for q in pending)
    records.append({"question_id": pending[0]["id"], "config": "C", "status": "error"})
    assert probe.select_remaining_controls(data, records) == selected
    output = tmp_path / "mechanism_probe.jsonl"
    source = {"frozen": "unchanged"}
    for record in records:
        record.update(declaration=probe.DECLARATION, source_hashes=source)
    output.write_text("".join(json.dumps(r) + "\n" for r in records))
    prefix = output.read_bytes()
    missing = [q for q in data if q["id"] not in {r["question_id"] for r in records}]
    client = Client([item for q in missing for item in [response(calls=[call("submit_answer", {"sql": "SELECT 3 AS n"}, q["id"])]), response("Done.")]])
    actual = asyncio.run(probe.run_probes(selected, client, Session(), "Glossary", output, source, KEY))
    assert len(actual) == 60 and len(client.requests) == 2 * 33
    assert output.read_bytes().startswith(prefix) and actual[:27] == records
    assert all(r["status"] == "error" for r in actual[:27])


@pytest.mark.parametrize("invalid", ["missing_prior", "duplicate", "wrong_universe"])
def test_remaining_controls_rejects_invalid_extension_before_running(invalid):
    data = questions()
    records = [{"question_id": q["id"], "config": "C", "status": "error"} for q in probe.select_questions(data)]
    if invalid == "missing_prior":
        records.pop()
    elif invalid == "duplicate":
        records.append(deepcopy(records[0]))
    else:
        data[-1]["id"] = "x30"
    with pytest.raises(ValueError):
        probe.select_remaining_controls(data, records)
