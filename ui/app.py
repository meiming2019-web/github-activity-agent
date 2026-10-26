"""Local Streamlit presentation of the unchanged config C agent."""

import asyncio
from copy import deepcopy
import json
import os
from pathlib import Path
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import streamlit.components.v1 as components

from agent import context, loop
from agent import live_context
from ui.charts import infer_chart


BANNER = "Frozen snapshot: GitHub top-100 repos, 2026-10-08 to 2026-10-21 (reference date 2026-10-22, UTC)"
ASSET = ROOT / "ui/assets/echarts.min.js"
EXAMPLES = (("d01", "Event mix"), ("d06", "Daily collaboration"), ("d09", "Repository comparison"), ("d12", "Activity trend"))


def example_questions():
    return {q["id"]: q["question"] for q in
            (json.loads(line) for line in (ROOT / "eval/github_dev_questions.jsonl").read_text().splitlines() if line.strip())
            if q["id"] in {id for id, _ in EXAMPLES}}


def chart_html(spec, asset_path=ASSET):
    if spec.get("type") not in ("line", "bar"):
        return ""
    data = json.dumps(spec, ensure_ascii=False, allow_nan=False)
    for character, escaped in (("<", "\\u003c"), (">", "\\u003e"), ("&", "\\u0026"), ("\u2028", "\\u2028"), ("\u2029", "\\u2029")):
        data = data.replace(character, escaped)
    vendor = Path(asset_path).read_text(encoding="utf-8").replace("</script", "<\\/script")
    return """<!doctype html><html><head><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'none'; img-src data:; font-src data:">
<style>body{margin:0;background:#fff;font-family:system-ui}#chart{height:340px;width:100%}</style></head><body>
<div id="chart"></div><script>""" + vendor + """</script><script type="application/json" id="chart-data">""" + data + """</script><script>
const spec=JSON.parse(document.getElementById('chart-data').textContent);
const chart=echarts.init(document.getElementById('chart'));
chart.setOption({animation:false,color:['#2563eb','#0d9488','#e69f00','#8b5cf6'],
 tooltip:{trigger:'axis',renderMode:'richText',confine:true},legend:{type:'scroll',top:4},
 grid:{left:60,right:24,top:45,bottom:85},
 xAxis:{type:'category',data:spec.x_data,axisLabel:{rotate:25,hideOverlap:true}},yAxis:{type:'value'},
 series:spec.series.map(s=>({name:s.name,type:spec.type,data:s.data,connectNulls:false}))});
window.addEventListener('resize',()=>chart.resize());
</script></body></html>"""


def failure_category(trace):
    if trace.get("status") == "completed" and trace.get("submitted") is True:
        return None
    message = trace.get("final_answer", "")
    if trace.get("status") == "budget_exceeded" or "limit of 12 tool calls" in message or "Answer already submitted." in message:
        return "budget_exceeded"
    if trace.get("status") == "sql_error_exhausted" or "3 consecutive SQL errors" in message:
        return "sql_error_exhausted"
    return "no_submission"


class TimedSession:
    """Measure UI-side wall time without changing MCP arguments or responses."""
    def __init__(self, session, trace, timings, setup, notify):
        self.session, self.trace, self.timings, self.setup, self.notify = session, trace, timings, setup, notify

    async def list_tools(self):
        return await self.session.list_tools()

    async def call_tool(self, name, arguments):
        entry = self.trace["tool_calls"][-1] if self.trace["tool_calls"] else None
        started = perf_counter()
        try:
            return await self.session.call_tool(name, arguments=arguments)
        finally:
            elapsed = (perf_counter() - started) * 1000
            if entry is not None:
                self.timings[entry["call_id"]] = elapsed
            else:
                self.setup.append({"name": name, "arguments": arguments, "elapsed_ms": elapsed})
            self.notify()


async def run_demo(question, on_update=None):
    if live_context.mode() == "live":
        from agent.run_mode import run_live
        return await run_live(question, on_update=on_update)
    trace = loop.new_trace(question, context.REFERENCE_DATE)
    timings, setup = {}, []
    api_key = ""
    started = perf_counter()

    def snapshot():
        return loop.sanitize({"trace": deepcopy(trace), "tool_timings_ms": dict(timings),
                              "setup_steps": deepcopy(setup), "elapsed_ms": (perf_counter() - started) * 1000,
                              "rounds": len(trace["api_responses"])}, api_key)

    def notify():
        if on_update is not None:
            on_update(snapshot())

    try:
        try:
            loop.load_dotenv(ROOT / ".env", override=False)
        except Exception:
            raise RuntimeError("Unable to load the project .env configuration.") from None
        api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY is missing or empty.")
        notify()
        parameters = loop.StdioServerParameters(command=sys.executable, args=["-B", str(ROOT / "agent/mcp_server.py")],
                                                cwd=str(ROOT), env=loop.get_default_environment())
        async with loop.AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com", max_retries=0, timeout=60.0) as client:
            async with loop.stdio_client(parameters) as (reader, writer):
                async with loop.ClientSession(reader, writer, read_timeout_seconds=20) as session:
                    await session.initialize()
                    timed = TimedSession(session, trace, timings, setup, notify)
                    shared = await context.shared_context(timed)
                    glossary = (ROOT / "eval/glossary.md").read_text(encoding="utf-8")
                    system_context = shared + ("\n\nUse lookup_glossary for definitions. Available topics include new_stars, "
                                               "collaboration_events, active_contributors, time conventions, dataset scope, event types.")

                    def lookup(term):
                        entry = trace["tool_calls"][-1]
                        lookup_started = perf_counter()
                        try:
                            return context.lookup_glossary(glossary, term)
                        finally:
                            timings[entry["call_id"]] = (perf_counter() - lookup_started) * 1000
                            notify()

                    task = asyncio.create_task(loop.run_loop(client, timed, trace, api_key, config="C",
                                                              system_context=system_context, lookup_glossary=lookup))
                    try:
                        while not task.done():
                            notify()
                            await asyncio.wait({task}, timeout=0.1)
                        trace = await task
                    finally:
                        if not task.done():
                            task.cancel()
                            await asyncio.gather(task, return_exceptions=True)
    except Exception as error:
        trace["status"] = "error"
        trace["final_answer"] = f"Agent stopped: {loop.sanitize(str(error), api_key)}"
    notify()
    return snapshot()


def render_result(result, slots, running=False):
    trace = result["trace"]
    with slots[0].container():
        st.subheader("Answer")
        if trace.get("mode") == "live" and trace.get("live_coverage"):
            coverage = trace["live_coverage"]
            st.caption(f"Available complete-day interval: [{coverage['retention_start']}, "
                       f"{coverage['complete_days_end_exclusive']}) · "
                       f"Missing archive hours: {len(coverage['missing_complete_day_hours'])} · "
                       f"Latest successful ingestion: {coverage['last_ingested_at']}. "
                       "Data is as of ingestion time; missing or expired dates are not verified zero activity.")
        if trace.get("final_answer"):
            st.markdown(trace["final_answer"])
        elif running:
            st.info("Querying live data…" if trace.get("mode") == "live" else "Querying the frozen snapshot…")
        else:
            st.info("Choose an example or ask a question to begin.")
        if not running and failure_category(trace) is not None and trace.get("final_answer"):
            st.error(f"{failure_category(trace)} · {trace['status']}")
        columns, rows = trace.get("answer_columns"), trace.get("answer_rows")
        if columns is not None and rows is not None:
            labels = [name if columns.count(name) == 1 else f"{index + 1} · {name}" for index, name in enumerate(columns)]
            st.dataframe({label: [row[index] for row in rows] for index, label in enumerate(labels)}, width="stretch")
            spec = infer_chart(columns, rows)
            if spec["type"] != "table":
                components.html(chart_html(spec), height=355, scrolling=False)
            if trace.get("answer_truncated"):
                st.warning("The submitted result was truncated by the existing tool limit.")
    with slots[1].container():
        st.subheader("SQL")
        st.code(trace.get("answer_sql") or "-- Waiting for submitted SQL", language="sql")
    with slots[2].container():
        with st.expander("Agent trace", expanded=True):
            st.caption("Tool durations are UI-side wall-clock instrumentation. Context setup is outside the agent tool budget.")
            for step in result["setup_steps"]:
                st.caption(f"Context setup · {step['name']} · {json.dumps(step['arguments'])} · {step['elapsed_ms']:.1f} ms")
            for index, entry in enumerate(trace["tool_calls"], 1):
                elapsed = result["tool_timings_ms"].get(entry["call_id"])
                timing = f"{elapsed:.1f} ms" if elapsed is not None else "pending / not dispatched"
                st.markdown(f"**{index}. {entry['name']}** · {timing}")
                st.json(entry["arguments"])
                if entry.get("result_summary"):
                    st.code(entry["result_summary"], language="text")
    with slots[3].container():
        st.subheader("Stats")
        metrics = st.columns(4)
        for cell, label, value in zip(metrics, ("API rounds", "Prompt tokens", "Completion tokens", "Total elapsed"),
                                      (result["rounds"], trace["prompt_tokens"], trace["completion_tokens"], f"{result['elapsed_ms'] / 1000:.2f} s")):
            cell.metric(label, value)
        st.caption(f"{trace['tool_call_count']}/12 agent tool calls · config C · reference date {trace.get('reference_date', context.REFERENCE_DATE)}")


def main():
    st.set_page_config(page_title="GitHub Activity Explorer", page_icon="◈", layout="wide")
    st.title("GitHub Activity Explorer")
    selected_mode = live_context.mode()
    live_context.switch_mode(st.session_state, selected_mode)
    st.warning(BANNER if selected_mode == "eval" else "Live events · complete UTC days only · repo metadata frozen at 2026-10-22")
    st.caption(f"Mode: {selected_mode}")
    st.caption("Read-only snapshot · Config C · Local demo")
    questions = example_questions() if selected_mode == "eval" else {
        "d01": "Count events by type for the last 7 days",
        "d06": "Count collaboration_events by UTC date for the last 7 days",
        "d09": "Compare new_stars by repository for the last 7 days",
        "d12": "Count events by UTC date for the last 14 days",
    }
    st.session_state.setdefault("question", "")
    st.session_state.setdefault("demo_runs", [])
    for column, (id, label) in zip(st.columns(4), EXAMPLES):
        if column.button(label, key=f"example-{id}", width="stretch"):
            st.session_state["question"] = questions[id]
    with st.form("ask"):
        question = st.text_area("Ask about the GitHub activity snapshot", key="question", height=95)
        execute = st.form_submit_button("Run config C", type="primary")
    slots = [st.empty() for _ in range(4)]
    if execute and question.strip():
        result = asyncio.run(run_demo(question, on_update=lambda result: render_result(result, slots, running=True)))
        st.session_state["demo_runs"].append(result)
        st.session_state["last_demo"] = result
    result = st.session_state.get("last_demo")
    if result is None:
        result = {"trace": loop.new_trace("", context.REFERENCE_DATE if selected_mode == "eval" else live_context.utc_now().date().isoformat()), "setup_steps": [], "tool_timings_ms": {}, "rounds": 0, "elapsed_ms": 0}
    render_result(result, slots)


if __name__ == "__main__":
    main()
