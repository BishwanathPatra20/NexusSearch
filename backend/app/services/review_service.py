import json
import sqlite3
from datetime import datetime
from typing import List, Optional

from backend.app.services.governance_audit_service import log_event
from backend.app.services.knowledge_integrity_service import insert_approved_knowledge
from backend.app.agents.pipeline import KnowledgePipeline
from backend.app.config import settings
from backend.app.schemas.models import (
    ApprovedKnowledgeOut,
    AskResponse,
    ExecutionPlanOut,
    ReviewActionOut,
    ReviewItemOut,
    ReviewSourceOut,
)
from backend.app.schemas.search_filters import SearchFilters


def _log_action(
    conn: sqlite3.Connection,
    review_item_id: int,
    action: str,
    reviewer: str,
    comment: Optional[str] = None,
    previous_answer: Optional[str] = None,
    new_answer: Optional[str] = None,
) -> None:
    conn.execute(
        """
        INSERT INTO review_actions (
            review_item_id, action, reviewer, comment, previous_answer, new_answer
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (review_item_id, action, reviewer, comment, previous_answer, new_answer),
    )


def _sources_for_item(conn: sqlite3.Connection, review_item_id: int) -> List[ReviewSourceOut]:
    rows = conn.execute(
        """
        SELECT rs.*, d.file_name, c.page_number
        FROM review_sources rs
        JOIN documents d ON d.id = rs.document_id
        JOIN document_chunks c ON c.id = rs.chunk_id
        WHERE rs.review_item_id = ?
        ORDER BY rs.relevance_score DESC
        """,
        (review_item_id,),
    ).fetchall()
    return [
        ReviewSourceOut(
            chunk_id=r["chunk_id"],
            document_id=r["document_id"],
            relevance_score=r["relevance_score"],
            snippet=r["snippet"],
            file_name=r["file_name"],
            page_number=r["page_number"],
        )
        for r in rows
    ]


def _row_to_review_item(conn: sqlite3.Connection, row: sqlite3.Row) -> ReviewItemOut:
    plan = None
    if row["plan_json"]:
        raw = json.loads(row["plan_json"])
        if "structured" not in raw:
            raw["structured"] = {
                "intent": "general",
                "action": "summarize",
                "requires_sources": True,
                "requires_review": True,
                "confidence_threshold": 80.0,
                "routing_notes": ["Legacy plan (pre-v0.5)"],
            }
        plan = ExecutionPlanOut.model_validate(raw)
    notes = json.loads(row["validator_notes_json"] or "[]")
    return ReviewItemOut(
        id=row["id"],
        query=row["query"],
        draft_answer=row["draft_answer"],
        final_answer=row["final_answer"],
        status=row["status"],
        confidence_score=row["confidence_score"],
        validator_notes=notes,
        plan=plan,
        sources=_sources_for_item(conn, row["id"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def ask_and_queue(
    conn: sqlite3.Connection,
    query: str,
    submit_for_review: bool = True,
    filters: Optional[SearchFilters] = None,
) -> AskResponse:
    pipeline = KnowledgePipeline()
    result = pipeline.run(conn, query, filters=filters)

    status = "pending"
    if (
        not submit_for_review
        and result.validation.confidence_score >= settings.review_auto_approve_min_confidence
    ):
        status = "approved"

    cursor = conn.execute(
        """
        INSERT INTO review_items (
            query, draft_answer, final_answer, status, confidence_score,
            validator_notes_json, plan_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            query,
            result.draft_answer,
            result.draft_answer if status == "approved" else None,
            status,
            result.validation.confidence_score,
            json.dumps(result.validation.notes),
            result.plan.model_dump_json(),
        ),
    )
    review_id = cursor.lastrowid
    assert review_id is not None

    for hit in result.hits:
        conn.execute(
            """
            INSERT INTO review_sources (
                review_item_id, chunk_id, document_id, relevance_score, snippet
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (review_id, hit.chunk_id, hit.document_id, hit.score, hit.snippet),
        )

    reviewer = settings.default_reviewer
    _log_action(conn, review_id, "submit_for_review", reviewer, comment="Pipeline completed")

    if status == "approved":
        _log_action(conn, review_id, "auto_approve", reviewer, new_answer=result.draft_answer)
        insert_approved_knowledge(
            conn,
            review_item_id=review_id,
            query=query,
            approved_answer=result.draft_answer,
            reviewer=reviewer,
        )

    item = _row_to_review_item(conn, conn.execute(
        "SELECT * FROM review_items WHERE id = ?", (review_id,)
    ).fetchone())

    return AskResponse(
        review_item_id=review_id,
        status=item.status,
        confidence_score=item.confidence_score,
        draft_answer=item.draft_answer,
        plan=result.plan,
        sources=item.sources,
        validator_notes=item.validator_notes,
    )


def list_review_items(conn: sqlite3.Connection, status: Optional[str] = None) -> List[ReviewItemOut]:
    if status:
        rows = conn.execute(
            "SELECT * FROM review_items WHERE status = ? ORDER BY created_at DESC",
            (status,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM review_items ORDER BY created_at DESC LIMIT 100"
        ).fetchall()
    return [_row_to_review_item(conn, r) for r in rows]


def get_review_item(conn: sqlite3.Connection, review_item_id: int) -> ReviewItemOut:
    row = conn.execute("SELECT * FROM review_items WHERE id = ?", (review_item_id,)).fetchone()
    if row is None:
        raise KeyError("Review item not found")
    return _row_to_review_item(conn, row)


def approve_item(
    conn: sqlite3.Connection,
    review_item_id: int,
    reviewer: Optional[str] = None,
    comment: Optional[str] = None,
) -> ReviewItemOut:
    row = conn.execute("SELECT * FROM review_items WHERE id = ?", (review_item_id,)).fetchone()
    if row is None:
        raise KeyError("Review item not found")
    reviewer_name = reviewer or settings.default_reviewer
    answer = row["final_answer"] or row["draft_answer"]
    conn.execute(
        """
        UPDATE review_items
        SET status = 'approved', final_answer = ?, updated_at = datetime('now')
        WHERE id = ?
        """,
        (answer, review_item_id),
    )
    _log_action(
        conn,
        review_item_id,
        "approve",
        reviewer_name,
        comment=comment,
        previous_answer=row["draft_answer"],
        new_answer=answer,
    )
    insert_approved_knowledge(
        conn,
        review_item_id=review_item_id,
        query=row["query"],
        approved_answer=answer,
        reviewer=reviewer_name,
    )
    log_event(
        conn,
        event_type="review.approved",
        actor=reviewer_name,
        resource_type="review_item",
        resource_id=str(review_item_id),
    )
    return get_review_item(conn, review_item_id)


def reject_item(
    conn: sqlite3.Connection,
    review_item_id: int,
    reviewer: Optional[str] = None,
    comment: Optional[str] = None,
) -> ReviewItemOut:
    row = conn.execute("SELECT * FROM review_items WHERE id = ?", (review_item_id,)).fetchone()
    if row is None:
        raise KeyError("Review item not found")
    reviewer_name = reviewer or settings.default_reviewer
    conn.execute(
        """
        UPDATE review_items SET status = 'rejected', updated_at = datetime('now') WHERE id = ?
        """,
        (review_item_id,),
    )
    _log_action(
        conn,
        review_item_id,
        "reject",
        reviewer_name,
        comment=comment,
        previous_answer=row["draft_answer"],
    )
    return get_review_item(conn, review_item_id)


def edit_and_approve(
    conn: sqlite3.Connection,
    review_item_id: int,
    final_answer: str,
    reviewer: Optional[str] = None,
    comment: Optional[str] = None,
) -> ReviewItemOut:
    row = conn.execute("SELECT * FROM review_items WHERE id = ?", (review_item_id,)).fetchone()
    if row is None:
        raise KeyError("Review item not found")
    reviewer_name = reviewer or settings.default_reviewer
    conn.execute(
        """
        UPDATE review_items
        SET status = 'edited', final_answer = ?, updated_at = datetime('now')
        WHERE id = ?
        """,
        (final_answer.strip(), review_item_id),
    )
    _log_action(
        conn,
        review_item_id,
        "edit",
        reviewer_name,
        comment=comment,
        previous_answer=row["draft_answer"],
        new_answer=final_answer.strip(),
    )
    insert_approved_knowledge(
        conn,
        review_item_id=review_item_id,
        query=row["query"],
        approved_answer=final_answer.strip(),
        reviewer=reviewer_name,
    )
    log_event(
        conn,
        event_type="review.edited_and_approved",
        actor=reviewer_name,
        resource_type="review_item",
        resource_id=str(review_item_id),
    )
    return get_review_item(conn, review_item_id)


def list_audit_trail(conn: sqlite3.Connection, review_item_id: int) -> List[ReviewActionOut]:
    rows = conn.execute(
        """
        SELECT * FROM review_actions
        WHERE review_item_id = ?
        ORDER BY timestamp ASC
        """,
        (review_item_id,),
    ).fetchall()
    return [
        ReviewActionOut(
            id=r["id"],
            action=r["action"],
            reviewer=r["reviewer"],
            comment=r["comment"],
            timestamp=datetime.fromisoformat(r["timestamp"]),
        )
        for r in rows
    ]


def list_approved_knowledge(conn: sqlite3.Connection, limit: int = 50) -> List[ApprovedKnowledgeOut]:
    rows = conn.execute(
        """
        SELECT * FROM approved_knowledge
        ORDER BY approved_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [
        ApprovedKnowledgeOut(
            id=r["id"],
            review_item_id=r["review_item_id"],
            query=r["query"],
            approved_answer=r["approved_answer"],
            reviewer=r["reviewer"],
            approved_at=datetime.fromisoformat(r["approved_at"]),
        )
        for r in rows
    ]
