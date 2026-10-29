"""POST /orchestrate — governed multi-agent pipeline with auditable steps."""

from __future__ import annotations

import re
import sqlite3
import time
from typing import List, Optional

from backend.app.agents.planner_agent import PlannerAgent
from backend.app.schemas.agents import (
    OrchestrateData,
    OrchestrateReviewOut,
    OrchestrateSourceOut,
    OrchestrateValidationOut,
)
from backend.app.schemas.search_filters import SearchFilters
from backend.app.services.agent_run_store import finish_run, new_execution_id, start_run
from backend.app.services.review_service import ask_and_queue


def _split_draft_lines(text: str) -> List[str]:
    lines: List[str] = []
    for part in re.split(r"[\n\r]+|(?<=[.!?])\s+", text.strip()):
        chunk = part.strip(" •-\t")
        if len(chunk) >= 3:
            lines.append(chunk)
    return lines or ([text.strip()] if text.strip() else [])


def _filters_from_request(
    status: Optional[str],
    tag: Optional[str],
    file_type: Optional[str],
) -> Optional[SearchFilters]:
    if not any([status, tag, file_type]):
        return None
    return SearchFilters(status=status, tag=tag, file_type=file_type)


def run_orchestration(
    conn: sqlite3.Connection,
    query: str,
    *,
    status: Optional[str] = None,
    tag: Optional[str] = None,
    file_type: Optional[str] = None,
    mode: str = "governed",
    submit_for_review: bool = True,
) -> tuple[OrchestrateData, int]:
    started = time.perf_counter()
    execution_id = new_execution_id("ORCH")
    start_run(conn, "orchestrate", trigger="api", execution_id=execution_id)
    steps: List[str] = ["planner"]

    try:
        filters = _filters_from_request(status, tag, file_type)

        if mode == "plan_only":
            plan_model = PlannerAgent().execute(query).to_api()
            data = OrchestrateData(
                execution_id=execution_id,
                plan=plan_model,
                evidence_count=0,
                draft_answer=[],
                draft_answer_text="",
                validation=OrchestrateValidationOut(score=0.0, supported=False, issues=[]),
                review=None,
                sources=[],
                steps_completed=steps,
            )
            finish_run(
                conn,
                execution_id,
                "completed",
                result={
                    "mode": mode,
                    "steps": steps,
                    "duration_ms": int((time.perf_counter() - started) * 1000),
                },
            )
            return data, int((time.perf_counter() - started) * 1000)

        steps.extend(["search", "rank", "evidence", "summarize", "validate"])
        ask_resp = ask_and_queue(
            conn,
            query,
            submit_for_review=submit_for_review,
            filters=filters,
        )
        if submit_for_review:
            steps.append("review")

        supported = ask_resp.confidence_score >= 55.0 and bool(ask_resp.sources)
        validation = OrchestrateValidationOut(
            score=float(ask_resp.confidence_score),
            supported=supported,
            issues=list(ask_resp.validator_notes or []),
        )
        sources = [
            OrchestrateSourceOut(
                document=(s.file_name or "document"),
                page=int(s.page_number or 0),
                chunk_id=int(s.chunk_id),
                score=float(s.relevance_score),
            )
            for s in ask_resp.sources
        ]
        review_out = (
            OrchestrateReviewOut(review_id=ask_resp.review_item_id, status=ask_resp.status)
            if submit_for_review
            else None
        )

        data = OrchestrateData(
            execution_id=execution_id,
            plan=ask_resp.plan,
            evidence_count=len(sources),
            draft_answer=_split_draft_lines(ask_resp.draft_answer),
            draft_answer_text=ask_resp.draft_answer,
            validation=validation,
            review=review_out,
            sources=sources,
            steps_completed=steps,
        )
        finish_run(
            conn,
            execution_id,
            "completed",
            result={
                "mode": mode,
                "steps": steps,
                "review_id": review_out.review_id if review_out else None,
                "duration_ms": int((time.perf_counter() - started) * 1000),
            },
        )
        return data, int((time.perf_counter() - started) * 1000)
    except Exception as exc:
        finish_run(conn, execution_id, "failed", error=str(exc))
        raise
