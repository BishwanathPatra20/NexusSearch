"""Run automation agents (Idea B)."""

from __future__ import annotations

import sqlite3
from typing import Any, Dict, List

from backend.app.services.agent_registry import list_agents
from backend.app.services.agent_run_store import finish_run, new_execution_id, start_run
from backend.app.services.automation import (
    corpus_steward,
    ingest_watcher,
    new_hire_autopilot,
    review_triage_agent,
    search_quality,
)

_AUTOMATION_HANDLERS = {
    "corpus_steward": corpus_steward.run,
    "new_hire_autopilot": new_hire_autopilot.run,
    "search_quality": search_quality.run,
    "ingest_watcher": ingest_watcher.run,
    "review_triage": review_triage_agent.run,
}


def automation_agent_names() -> List[str]:
    return list(_AUTOMATION_HANDLERS.keys())


def run_automation_agent(
    conn: sqlite3.Connection,
    agent_name: str,
    trigger: str = "manual",
) -> Dict[str, Any]:
    handler = _AUTOMATION_HANDLERS.get(agent_name)
    if handler is None:
        raise ValueError(f"Unknown automation agent: {agent_name}")

    if trigger.startswith("schedule"):
        enabled = {a.name: a.enabled for a in list_agents()}
        if not enabled.get(agent_name, True):
            raise RuntimeError(f"Agent disabled: {agent_name}")

    execution_id = new_execution_id("AUTO")
    start_run(conn, agent_name, trigger=trigger, execution_id=execution_id)
    try:
        result = handler(conn)
        result["execution_id"] = execution_id
        finish_run(conn, execution_id, "completed", result=result)
        return result
    except Exception as exc:
        finish_run(conn, execution_id, "failed", error=str(exc))
        raise


def run_automation_batch(
    conn: sqlite3.Connection,
    agent_names: List[str],
    trigger: str = "manual",
) -> List[Dict[str, Any]]:
    names = agent_names or automation_agent_names()
    runs: List[Dict[str, Any]] = []
    for name in names:
        if name not in _AUTOMATION_HANDLERS:
            runs.append(
                {
                    "agent": name,
                    "status": "failed",
                    "message": f"Unknown automation agent: {name}",
                }
            )
            continue
        try:
            result = run_automation_agent(conn, name, trigger=trigger)
            runs.append(
                {
                    "agent": name,
                    "status": "completed",
                    "message": result.get("message", "ok"),
                    "execution_id": result.get("execution_id"),
                }
            )
        except Exception as exc:  # noqa: BLE001 — continue batch
            runs.append({"agent": name, "status": "failed", "message": str(exc)})
    return runs
