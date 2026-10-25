"""Minimal DeepSeek tool-calling loop over the local read-only MCP server."""

from copy import deepcopy
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import re
import sys

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import get_default_environment, stdio_client
from openai import AsyncOpenAI

from agent.error_feedback import whitelist_feedback


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL = "deepseek-chat"


def sanitize(value, api_key):
    """Remove the API key from strings anywhere in a surfaced trace or message."""
    if isinstance(value, str):
        return value.replace(api_key, "[REDACTED]") if api_key else value
    if isinstance(value, dict):
        return {sanitize(key, api_key): sanitize(item, api_key) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [sanitize(item, api_key) for item in value]
    return value


def reference_date():
    value = os.environ.get("AGENT_REF_DATE", datetime.now(timezone.utc).date().isoformat())
    try:
        if date.fromisoformat(value).isoformat() != value:
            raise ValueError
    except ValueError:
        raise ValueError("AGENT_REF_DATE must be a valid YYYY-MM-DD date.") from None
    return value


def openai_tools(tools):
    return [{"type": "function", "function": {
        "name": tool.name, "description": tool.description or "", "parameters": deepcopy(tool.input_schema),
    }} for tool in tools] + [{"type": "function", "function": {
        "name": "submit_answer",
        "description": "Execute the exact final-answer SQL and submit its result for scoring, exactly once.",
        "parameters": {"type": "object", "properties": {"sql": {"type": "string"}},
                       "required": ["sql"], "additionalProperties": False},
    }}]


def new_trace(question, ref_date=None):
    return {
        "question": question, "final_answer": "", "answer_sql": None, "answer_columns": None,
        "answer_rows": None, "answer_truncated": None, "submitted": False, "tool_call_count": 0,
        "prompt_tokens": 0, "completion_tokens": 0, "status": "error",
        "reference_date": ref_date, "model": MODEL, "tool_calls": [], "api_responses": [],
    }


def parse_sql(content):
    match = re.search(r"```sql\s*(.*?)```", content, flags=re.IGNORECASE | re.DOTALL)
    return (match.group(1) if match else content).strip()


async def run_baseline(client, session, trace, api_key, context):
    try:
        response = await client.chat.completions.create(
            model=MODEL, temperature=0, messages=sanitize([
                {"role": "system", "content": (
                    f"Today's date is {trace['reference_date']} (UTC). Return one read-only DuckDB SELECT query answering the question. "
                    "Use date literals, never CURRENT_DATE or CURRENT_TIMESTAMP. Return SQL in a ```sql block.\n\n" + (context or ""))},
                {"role": "user", "content": trace["question"]},
            ], api_key),
        )
        usage = response.usage
        trace["prompt_tokens"] = int(usage.prompt_tokens or 0) if usage else 0
        trace["completion_tokens"] = int(usage.completion_tokens or 0) if usage else 0
        trace["api_responses"].append({"prompt_tokens": trace["prompt_tokens"],
                                       "completion_tokens": trace["completion_tokens"],
                                       "total_tokens": int(usage.total_tokens or 0) if usage else 0})
        message = response.choices[0].message
        if message.tool_calls or not isinstance(message.content, str) or not message.content.strip():
            raise ValueError("Baseline requires a nonempty SQL text response without tool calls.")
        sql = parse_sql(sanitize(message.content, api_key))
        trace["tool_call_count"] = 1
        result = await session.call_tool("run_query", arguments={"sql": sql})
        text = "\n".join(block.text for block in result.content if block.type == "text")
        if result.is_error:
            raise RuntimeError(text)
        payload = result.structured_content if result.structured_content is not None else json.loads(text)
        trace.update(answer_sql=sql, answer_columns=payload["columns"], answer_rows=payload["rows"],
                     answer_truncated=payload["truncated"], submitted=True, status="completed",
                     final_answer=json.dumps(payload, ensure_ascii=False, allow_nan=False))
    except Exception as error:
        trace["final_answer"] = f"Baseline stopped: {sanitize(str(error), api_key)}"
    return sanitize(trace, api_key)


async def run_loop(client, session, trace, api_key, *, config="B", system_context=None, lookup_glossary=None):
    if config == "A":
        return await run_baseline(client, session, trace, api_key, system_context)
    feedback_enabled = config == "C3"
    if feedback_enabled:
        config = "C"
    sql_errors = 0
    try:
        if config not in ("B", "C"):
            raise ValueError("config must be A, B, or C.")
        if config == "C" and lookup_glossary is None:
            raise ValueError("Config C requires lookup_glossary.")
        if config == "B":
            lookup_glossary = None
        available = (await session.list_tools()).tools
        tools = openai_tools(available)
        if lookup_glossary is not None:
            tools.append({"type": "function", "function": {
                "name": "lookup_glossary", "description": "Look up whole glossary sections by title or metric name.",
                "parameters": {"type": "object", "properties": {"term": {"type": "string"}},
                               "required": ["term"], "additionalProperties": False},
            }})
        names = {tool["function"]["name"] for tool in tools}
        messages = [
            {"role": "system", "content": (
                f"Today's date is {trace['reference_date']} (UTC). "
                "Answer the question by querying the local DuckDB GitHub activity snapshot through "
                "the four read-only MCP tools: list_tables, describe_table, sample_values, and run_query. "
                "Use the injected reference date as a SQL date literal. Never use CURRENT_DATE or CURRENT_TIMESTAMP. "
                "Use tool results as evidence and explain missing or truncated data. "
                "You have at most 12 tool calls. SQL errors are returned for you to correct; "
                "three consecutive SQL errors, including failed submissions, stop the run. "
                "When you are confident a query's result IS the final answer, you MUST call submit_answer with that exact SQL. "
                "After submitting, make no further tool calls; write your final summary as text. "
                "Every question requires exactly one submission."
            )},
            {"role": "user", "content": sanitize(trace["question"], api_key)},
        ]
        if system_context is not None:
            messages[0]["content"] += "\n\n" + sanitize(system_context, api_key)
        while True:
            response = await client.chat.completions.create(
                model=MODEL, temperature=0, messages=sanitize(messages, api_key), tools=tools,
            )
            usage = response.usage
            prompt_tokens = int(usage.prompt_tokens or 0) if usage else 0
            completion_tokens = int(usage.completion_tokens or 0) if usage else 0
            trace["api_responses"].append({
                "prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens,
                "total_tokens": int(usage.total_tokens or 0) if usage else 0,
            })
            trace["prompt_tokens"] += prompt_tokens
            trace["completion_tokens"] += completion_tokens
            if not response.choices:
                raise RuntimeError("The model returned no choices.")
            message = response.choices[0].message
            calls = message.tool_calls or []
            if not calls:
                if not isinstance(message.content, str) or not message.content.strip():
                    raise RuntimeError("The model returned no plain-text answer or tool calls.")
                trace["final_answer"] = message.content
                trace["status"] = "completed" if trace["submitted"] else "no_submission"
                break
            # Copy only protocol fields, never reasoning content or raw SDK objects.
            assistant_calls = []
            for call in calls:
                if call.type != "function" or call.function.name not in names:
                    raise RuntimeError("The model requested an unknown or unsupported tool.")
                arguments = json.loads(call.function.arguments)
                if not isinstance(arguments, dict):
                    raise ValueError("Tool arguments must be a JSON object.")
                arguments = sanitize(arguments, api_key)
                assistant_calls.append({
                    "id": sanitize(call.id, api_key), "type": "function",
                    "function": {"name": call.function.name, "arguments": json.dumps(arguments, ensure_ascii=False)},
                })
            messages.append({"role": "assistant", "content": sanitize(message.content, api_key), "tool_calls": assistant_calls})
            rejection_budget_exhausted = False
            for call in assistant_calls:
                name = call["function"]["name"]
                arguments = json.loads(call["function"]["arguments"])
                if trace["submitted"]:
                    trace["tool_calls"].append({
                        "call_id": call["id"], "name": name, "arguments": arguments,
                        "is_error": True, "rejected": True, "result_summary": "Answer already submitted.",
                    })
                    messages.append({"role": "tool", "tool_call_id": call["id"], "content": "Answer already submitted."})
                    if trace["tool_call_count"] < 12:
                        trace["tool_call_count"] += 1
                    else:
                        rejection_budget_exhausted = True
                    continue
                if trace["tool_call_count"] >= 12:
                    raise RuntimeError("Stopped at the limit of 12 tool calls; no additional tool was dispatched.")
                if name == "submit_answer" and (set(arguments) != {"sql"} or not isinstance(arguments["sql"], str)):
                    raise ValueError("submit_answer requires exactly one string argument: sql.")
                if name == "lookup_glossary" and (set(arguments) != {"term"} or not isinstance(arguments["term"], str)):
                    raise ValueError("lookup_glossary requires exactly one string argument: term.")
                trace["tool_call_count"] += 1
                entry = {"call_id": call["id"], "name": name, "arguments": arguments,
                         "is_error": False, "result_summary": ""}
                trace["tool_calls"].append(entry)
                if name == "lookup_glossary":
                    content = sanitize(lookup_glossary(arguments["term"]), api_key)
                    entry["result_summary"] = content[:1000]
                    messages.append({"role": "tool", "tool_call_id": call["id"], "content": content})
                    continue
                try:
                    result = await session.call_tool("run_query" if name == "submit_answer" else name, arguments=arguments)
                except Exception as error:
                    entry["is_error"] = True
                    entry["result_summary"] = sanitize(str(error), api_key)[:1000]
                    raise RuntimeError(f"Tool request failed: {sanitize(str(error), api_key)}") from None
                payload = result.structured_content
                if payload is None:
                    payload = "\n".join(block.text for block in result.content if block.type == "text")
                payload = sanitize(payload, api_key)
                content = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False, allow_nan=False)
                entry["is_error"] = bool(result.is_error)
                if feedback_enabled and name == "run_query" and result.is_error:
                    feedback = whitelist_feedback(content)
                    if feedback != content:
                        entry["raw_error"] = content
                        content = feedback
                entry["result_summary"] = content[:1000]
                messages.append({"role": "tool", "tool_call_id": call["id"], "content": content})
                if name in {"run_query", "submit_answer"}:
                    if result.is_error:
                        sql_errors += 1
                        if sql_errors >= 3:
                            raise RuntimeError("Stopped after 3 consecutive SQL errors.")
                    else:
                        sql_errors = 0
                        if name == "submit_answer":
                            if not isinstance(payload, dict):
                                raise ValueError("Successful submission returned no structured result.")
                            trace.update(answer_sql=arguments["sql"], answer_columns=payload["columns"],
                                         answer_rows=payload["rows"], answer_truncated=payload["truncated"], submitted=True)
            if rejection_budget_exhausted:
                raise RuntimeError("Answer already submitted.")
    except Exception as error:
        trace["status"] = "error"
        trace["final_answer"] = f"Agent stopped: {sanitize(str(error), api_key)}"
    return sanitize(trace, api_key)


async def answer_question(question):
    trace = new_trace(question)
    api_key = ""
    try:
        try:
            load_dotenv(PROJECT_ROOT / ".env", override=False)
        except Exception:
            raise RuntimeError("Unable to load the project .env configuration.") from None
        api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY is missing or empty.")
        trace["reference_date"] = reference_date()
        parameters = StdioServerParameters(
            command=sys.executable, args=["-B", str(PROJECT_ROOT / "agent/mcp_server.py")],
            cwd=str(PROJECT_ROOT), env=get_default_environment(),
        )
        async with AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com", max_retries=0, timeout=60.0) as client:
            async with stdio_client(parameters) as (reader, writer):
                async with ClientSession(reader, writer, read_timeout_seconds=20) as session:
                    await session.initialize()
                    trace = await run_loop(client, session, trace, api_key)
    except Exception as error:
        trace["status"] = "error"
        trace["final_answer"] = f"Agent stopped: {sanitize(str(error), api_key)}"
    return sanitize(trace, api_key)
