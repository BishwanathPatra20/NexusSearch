"""Agent platform: registry, orchestrate (Idea A), automations (Idea B)."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request

from backend.app.api.agent_auth import require_agent_api_key
from backend.app.db.connection import get_connection
from backend.app.schemas.agents import (
    AgentEnvelope,
    AgentErrorBody,
    AgentInboxItem,
    AgentInboxResponse,
    AgentRegistryItem,
    AgentRunRecord,
    AutomationBatchResponse,
    AutomationRunRequest,
    AutomationRunSummary,
    AutomationScheduleIn,
    AutomationScheduleOut,
    OrchestrateRequest,
)
from backend.app.services.automation_schedule_service import get_schedule, save_schedule
from backend.app.services.agent_dashboard_service import build_dashboard
from backend.app.services.automation_scheduler import reload_scheduler
from backend.app.schemas.agents import AgentDashboardOut
from backend.app.services.agent_registry import list_agents
from backend.app.services.agent_run_store import get_run, list_runs
from backend.app.services.automation.runner import automation_agent_names, run_automation_batch
from backend.app.services.orchestration_service import run_orchestration

router = APIRouter(tags=["agents"])


def _request_id(request: Request) -> str:
    return request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]


def _ok(
    agent: str,
    data: dict,
    execution_id: Optional[str] = None,
    duration_ms: Optional[int] = None,
) -> AgentEnvelope:
    meta = {}
    if duration_ms is not None:
        meta["duration_ms"] = duration_ms
    return AgentEnvelope(
        success=True,
        agent=agent,
        execution_id=execution_id,
        data=data,
        metadata=meta,
    )


def _err(code: str, message: str, request_id: str, status: int = 400) -> HTTPException:
    return HTTPException(
        status_code=status,
        detail={
            "success": False,
            "error": AgentErrorBody(code=code, message=message, request_id=request_id).model_dump(),
        },
    )


@router.get("/agents", response_model=List[AgentRegistryItem])
def agents_registry() -> List[AgentRegistryItem]:
    return list_agents()


@router.post("/orchestrate", response_model=AgentEnvelope, dependencies=[Depends(require_agent_api_key)])
def orchestrate(body: OrchestrateRequest, request: Request) -> AgentEnvelope:
    rid = _request_id(request)
    try:
        with get_connection() as conn:
            data, duration_ms = run_orchestration(
                conn,
                body.query,
                status=body.filters.status,
                tag=body.filters.tag,
                file_type=body.filters.file_type,
                mode=body.mode,
                submit_for_review=body.submit_for_review,
            )
        return _ok(
            "orchestrate",
            data.model_dump(),
            execution_id=data.execution_id,
            duration_ms=duration_ms,
        )
    except ValueError as exc:
        raise _err("ORCH_001", str(exc), rid, 400) from exc
    except Exception as exc:
        raise _err("ORCH_500", str(exc), rid, 500) from exc


@router.post("/automations/run", response_model=AgentEnvelope, dependencies=[Depends(require_agent_api_key)])
def automations_run(body: AutomationRunRequest, request: Request) -> AgentEnvelope:
    rid = _request_id(request)
    batch_id = f"BATCH-{uuid.uuid4().hex[:10]}"
    names = body.agents if body.agents else automation_agent_names()
    try:
        with get_connection() as conn:
            runs = run_automation_batch(conn, names, trigger=body.trigger)
        payload = AutomationBatchResponse(
            batch_id=batch_id,
            runs=[
                AutomationRunSummary(
                    execution_id=r.get("execution_id") or batch_id,
                    agent=r["agent"],
                    status=r["status"],
                    message=r.get("message", ""),
                )
                for r in runs
            ],
        )
        return _ok("automation_batch", payload.model_dump(), execution_id=batch_id)
    except Exception as exc:
        raise _err("AUTO_500", str(exc), rid, 500) from exc


@router.get("/automations/runs", response_model=List[AgentRunRecord])
def automations_list_runs(limit: int = 30) -> List[AgentRunRecord]:
    with get_connection() as conn:
        rows = list_runs(conn, limit=limit)
    out: List[AgentRunRecord] = []
    for row in rows:
        result = json.loads(row["result_json"]) if row["result_json"] else None
        out.append(
            AgentRunRecord(
                execution_id=row["execution_id"],
                agent_name=row["agent_name"],
                status=row["status"],
                trigger=row["trigger"],
                result=result,
                error_message=row["error_message"],
                started_at=datetime.fromisoformat(row["started_at"]),
                finished_at=datetime.fromisoformat(row["finished_at"]) if row["finished_at"] else None,
            )
        )
    return out


@router.get("/automations/runs/{execution_id}", response_model=AgentRunRecord)
def automations_get_run(execution_id: str) -> AgentRunRecord:
    with get_connection() as conn:
        row = get_run(conn, execution_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Run not found")
    result = json.loads(row["result_json"]) if row["result_json"] else None
    return AgentRunRecord(
        execution_id=row["execution_id"],
        agent_name=row["agent_name"],
        status=row["status"],
        trigger=row["trigger"],
        result=result,
        error_message=row["error_message"],
        started_at=datetime.fromisoformat(row["started_at"]),
        finished_at=datetime.fromisoformat(row["finished_at"]) if row["finished_at"] else None,
    )


@router.get("/automations/dashboard", response_model=AgentDashboardOut)
def automations_dashboard() -> AgentDashboardOut:
    with get_connection() as conn:
        return build_dashboard(conn)


@router.get("/automations/schedule", response_model=AutomationScheduleOut)
def automations_get_schedule() -> AutomationScheduleOut:
    with get_connection() as conn:
        return get_schedule(conn)


@router.put("/automations/schedule", response_model=AutomationScheduleOut, dependencies=[Depends(require_agent_api_key)])
def automations_save_schedule(body: AutomationScheduleIn) -> AutomationScheduleOut:
    with get_connection() as conn:
        saved = save_schedule(conn, body)
    reload_scheduler()
    return saved


@router.get("/automations/inbox", response_model=AgentInboxResponse)
def automations_inbox(limit: int = 15) -> AgentInboxResponse:
    with get_connection() as conn:
        rows = list_runs(conn, limit=limit)
    items: List[AgentInboxItem] = []
    for row in rows:
        if row["agent_name"] == "orchestrate":
            continue
        result = json.loads(row["result_json"]) if row["result_json"] else {}
        summary = result.get("message") or row["status"]
        items.append(
            AgentInboxItem(
                execution_id=row["execution_id"],
                agent_name=row["agent_name"],
                status=row["status"],
                summary=summary,
                finished_at=datetime.fromisoformat(row["finished_at"]) if row["finished_at"] else None,
                report_path=result.get("report_path"),
            )
        )
    return AgentInboxResponse(items=items)
