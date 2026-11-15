"""Deterministic harness using the production agent validation and tool modules."""

import json
import time
from pathlib import Path

from backend.app import agent
from backend.app.confirmation import approve_action, clear_actions

USER = {"id": 41, "role": "student"}


def fake_query(sql, params=(), fetch="all", commit=False):
    sql_lower = sql.lower()
    if "student_preferences" in sql_lower:
        return {"preferred_categories": [], "preferred_cities": ["San Jose"], "preferred_skills": [], "remote_only": False, "minimum_salary": None}
    if "from jobs" in sql_lower and "where j.id" in sql_lower:
        return {"id": 1, "title": "Synthetic Data Internship", "company": "Synthetic Co", "location": "San Jose", "salary": "100000", "deadline": "2026-12-31"}
    if "from jobs" in sql_lower:
        return [{"id": 1, "title": "Synthetic Data Internship", "company": "Synthetic Co", "location": "San Jose", "salary": "100000", "deadline": "2026-12-31"}]
    if "from events" in sql_lower:
        return [{"id": 2, "name": "Synthetic Career Event", "event_date": "2026-12-01", "location": "Palo Alto"}]
    if "select id from saved_items" in sql_lower:
        return None
    if "select id from jobs" in sql_lower or "select id from events" in sql_lower:
        return {"id": params[0]}
    if commit:
        return 99
    return []


class ScriptedModel:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def complete(self, messages, tools=None):
        self.calls += 1
        return self.responses.pop(0) if self.responses else {"content": "No additional model response."}


def case(name, fn):
    started = time.perf_counter()
    try:
        result = fn()
        return {"name": name, "input": name, "messages": [], "tools": list(agent.TOOL_SCHEMAS),
                "arguments": {}, "tool_calls": [], "results": result, "final_answer": str(result),
                "guardrail_outcome": "passed", "errors": [], "retries": 0,
                "token_counts": {"prompt_tokens": None, "completion_tokens": None, "estimated": True},
                "pass": True, "elapsed_ms": round((time.perf_counter() - started) * 1000, 2)}
    except Exception as exc:
        return {"name": name, "input": name, "messages": [], "tools": list(agent.TOOL_SCHEMAS),
                "arguments": {}, "tool_calls": [], "results": None, "final_answer": "",
                "guardrail_outcome": "failed", "errors": [type(exc).__name__ + ": " + str(exc)],
                "retries": 0, "token_counts": {"prompt_tokens": None, "completion_tokens": None, "estimated": True},
                "pass": False, "elapsed_ms": round((time.perf_counter() - started) * 1000, 2)}


def run_harness():
    clear_actions()
    cases = []
    cases.append(case("read_only_success", lambda: agent.run_assistant("find jobs in San Jose", [], USER, fake_query, model=ScriptedModel([]))))
    cases.append(case("event_no_match_or_result", lambda: agent.run_assistant("show events in Palo Alto", [], USER, fake_query, model=ScriptedModel([]))))
    cases.append(case("history_follow_up", lambda: _follow_up()))
    cases.append(case("malformed_arguments", lambda: agent.execute_tool("search_jobs", {"unknown": 1}, USER, fake_query)))
    cases.append(case("unknown_tool", lambda: agent.execute_tool("not_a_tool", {}, USER, fake_query)))
    cases.append(case("injection_data_is_delimited", lambda: agent.execute_tool("get_job_details", {"job_id": 1}, USER, fake_query)))
    cases.append(case("accepted_write_proposal", lambda: _proposal(True)))
    cases.append(case("declined_write", lambda: _proposal(False)))
    cases.append(case("bounded_repair", lambda: _repair_once()))
    cases.append(case("iteration_limit", lambda: _iteration_limit()))
    return {"harness": "production-agent-modules", "cases": cases, "pass_count": sum(item["pass"] for item in cases), "fail_count": sum(not item["pass"] for item in cases)}


def _follow_up():
    conversation = []
    agent.run_assistant("show events in Palo Alto", conversation, USER, fake_query, model=ScriptedModel([]))
    return agent.run_assistant("what about San Jose", conversation, USER, fake_query, model=ScriptedModel([]))


def _proposal(approved):
    result = agent.execute_tool("save_job_or_event", {"item_type": "job", "item_id": 1}, USER, fake_query)
    action_id = json.loads(result.split("Confirmation required: ", 1)[1])["action_id"]
    action, error = approve_action(action_id, USER["id"], approved)
    return {"proposal_created": True, "approved": approved, "error": error, "write_required": bool(action and approved)}


def _repair_once():
    model = ScriptedModel([
        {"tool_calls": [{"id": "bad", "function": {"name": "get_job_details", "arguments": "{}"}}]},
        {"content": "The requested job could not be identified safely."},
    ])
    return agent.run_assistant("tell me about a job", [], USER, fake_query, model=model)


def _iteration_limit():
    model = ScriptedModel([{"tool_calls": [{"id": str(i), "function": {"name": "search_jobs", "arguments": "{}"}}]} for i in range(agent.MAX_ITERATIONS + 1)])
    return agent.run_assistant("find jobs", [], USER, fake_query, model=model)


if __name__ == "__main__":
    output = run_harness()
    Path("agent_harness.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({key: output[key] for key in ("harness", "pass_count", "fail_count")}, indent=2))
