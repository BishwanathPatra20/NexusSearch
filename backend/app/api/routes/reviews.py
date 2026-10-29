from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from backend.app.db.connection import get_connection
from backend.app.schemas.agents import ReviewTriageResponse, TriageBatchApproveRequest, TriageBatchApproveResult
from backend.app.schemas.models import (
    ApprovedKnowledgeOut,
    ReviewActionOut,
    ReviewDecisionRequest,
    ReviewEditRequest,
    ReviewItemOut,
)
from backend.app.services.review_triage_service import batch_approve, build_triage
from backend.app.services.review_service import (
    approve_item,
    edit_and_approve,
    get_review_item,
    list_approved_knowledge,
    list_audit_trail,
    list_review_items,
    reject_item,
)

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("", response_model=List[ReviewItemOut])
def reviews_list(status: Optional[str] = Query(None)) -> List[ReviewItemOut]:
    with get_connection() as conn:
        return list_review_items(conn, status=status)


@router.get("/approved", response_model=List[ApprovedKnowledgeOut])
def approved_knowledge(limit: int = Query(50, ge=1, le=200)) -> List[ApprovedKnowledgeOut]:
    with get_connection() as conn:
        return list_approved_knowledge(conn, limit=limit)


@router.get("/triage", response_model=ReviewTriageResponse)
def reviews_triage() -> ReviewTriageResponse:
    with get_connection() as conn:
        return build_triage(conn)


@router.post("/triage/batch-approve", response_model=TriageBatchApproveResult)
def reviews_triage_batch_approve(body: TriageBatchApproveRequest) -> TriageBatchApproveResult:
    with get_connection() as conn:
        return batch_approve(
            conn,
            min_confidence=body.min_confidence,
            max_count=body.max_count,
            group_key=body.group_key,
        )


@router.get("/{review_item_id}", response_model=ReviewItemOut)
def review_detail(review_item_id: int) -> ReviewItemOut:
    try:
        with get_connection() as conn:
            return get_review_item(conn, review_item_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Review item not found")


@router.get("/{review_item_id}/audit", response_model=List[ReviewActionOut])
def review_audit(review_item_id: int) -> List[ReviewActionOut]:
    try:
        with get_connection() as conn:
            get_review_item(conn, review_item_id)
            return list_audit_trail(conn, review_item_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Review item not found")


@router.post("/{review_item_id}/approve", response_model=ReviewItemOut)
def review_approve(review_item_id: int, body: ReviewDecisionRequest) -> ReviewItemOut:
    try:
        with get_connection() as conn:
            return approve_item(conn, review_item_id, reviewer=body.reviewer, comment=body.comment)
    except KeyError:
        raise HTTPException(status_code=404, detail="Review item not found")


@router.post("/{review_item_id}/reject", response_model=ReviewItemOut)
def review_reject(review_item_id: int, body: ReviewDecisionRequest) -> ReviewItemOut:
    try:
        with get_connection() as conn:
            return reject_item(conn, review_item_id, reviewer=body.reviewer, comment=body.comment)
    except KeyError:
        raise HTTPException(status_code=404, detail="Review item not found")


@router.post("/{review_item_id}/edit", response_model=ReviewItemOut)
def review_edit(review_item_id: int, body: ReviewEditRequest) -> ReviewItemOut:
    try:
        with get_connection() as conn:
            return edit_and_approve(
                conn,
                review_item_id,
                body.final_answer,
                reviewer=body.reviewer,
                comment=body.comment,
            )
    except KeyError:
        raise HTTPException(status_code=404, detail="Review item not found")
