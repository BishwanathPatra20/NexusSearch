import json
import sqlite3
from datetime import datetime
from typing import List, Optional

from backend.app.schemas.models import (
    ApprovedKnowledgeOut,
    ExecutionPlanOut,
    KnowledgeLineageOut,
    LineageIndexItem,
    LineageReviewOut,
    LineageSourceOut,
    LineageStageOut,
    LineageValidationOut,
    ReviewActionOut,
)
from backend.app.services.review_service import list_audit_trail


def _parse_plan(row: sqlite3.Row) -> Optional[ExecutionPlanOut]:
    if not row["plan_json"]:
        return None
    raw = json.loads(row["plan_json"])
    if "structured" not in raw:
        raw["structured"] = {
            "intent": "general",
            "action": "summarize",
            "requires_sources": True,
            "requires_review": True,
            "confidence_threshold": 80.0,
            "routing_notes": ["Legacy plan"],
        }
    return ExecutionPlanOut.model_validate(raw)


def _approved_row(conn: sqlite3.Connection, review_item_id: int) -> Optional[sqlite3.Row]:
    return conn.execute(
        """
        SELECT * FROM approved_knowledge
        WHERE review_item_id = ?
        ORDER BY approved_at DESC
        LIMIT 1
        """,
        (review_item_id,),
    ).fetchone()


def _knowledge_id(approved_row: Optional[sqlite3.Row]) -> Optional[str]:
    if approved_row is None:
        return None
    return f"AK-{int(approved_row['id']):04d}"


def _sources_enriched(conn: sqlite3.Connection, review_item_id: int) -> List[LineageSourceOut]:
    rows = conn.execute(
        """
        SELECT rs.*, d.title AS document_title, d.file_name, c.page_number, c.chunk_index
        FROM review_sources rs
        JOIN documents d ON d.id = rs.document_id
        JOIN document_chunks c ON c.id = rs.chunk_id
        WHERE rs.review_item_id = ?
        ORDER BY rs.relevance_score DESC
        """,
        (review_item_id,),
    ).fetchall()
    return [
        LineageSourceOut(
            chunk_id=r["chunk_id"],
            document_id=r["document_id"],
            relevance_score=r["relevance_score"],
            snippet=r["snippet"],
            file_name=r["file_name"],
            page_number=r["page_number"],
            document_title=r["document_title"],
            chunk_index=r["chunk_index"],
        )
        for r in rows
    ]


def _review_summary(conn: sqlite3.Connection, row: sqlite3.Row) -> LineageReviewOut:
    actions = conn.execute(
        """
        SELECT * FROM review_actions
        WHERE review_item_id = ?
        ORDER BY timestamp DESC
        """,
        (row["id"],),
    ).fetchall()
    last = actions[0] if actions else None
    label = None
    if last:
        label = f"{last['action']} by {last['reviewer']}"
    return LineageReviewOut(
        status=row["status"],
        final_answer=row["final_answer"],
        last_reviewer=last["reviewer"] if last else None,
        last_decision_at=datetime.fromisoformat(last["timestamp"]) if last else None,
        decision_label=label,
    )


def _build_timeline(
    row: sqlite3.Row,
    plan: Optional[ExecutionPlanOut],
    validation: LineageValidationOut,
    review: LineageReviewOut,
    approved: Optional[ApprovedKnowledgeOut],
    audit: List[ReviewActionOut],
    sources_count: int = 0,
) -> List[LineageStageOut]:
    created = datetime.fromisoformat(row["created_at"])
    stages: List[LineageStageOut] = [
        LineageStageOut(stage="question", title="Question", detail=row["query"], timestamp=created),
    ]
    if plan and plan.structured:
        detail = f"intent={plan.structured.intent}, action={plan.structured.action}"
        stages.append(LineageStageOut(stage="planner", title="Planner decision", detail=detail, timestamp=created))
    stages.append(
        LineageStageOut(
            stage="draft",
            title="Draft answer",
            detail=(row["draft_answer"][:240] + "…") if len(row["draft_answer"]) > 240 else row["draft_answer"],
            timestamp=created,
        )
    )
    val_detail = f"Supported: {'Yes' if validation.supported else 'No'} · Score: {validation.confidence_score}"
    stages.append(LineageStageOut(stage="validation", title="Validation", detail=val_detail, timestamp=created))
    if audit:
        stages.append(
            LineageStageOut(
                stage="review",
                title="Review",
                detail=review.decision_label or review.status,
                timestamp=review.last_decision_at,
            )
        )
    if approved:
        chunk_note = ""
        if approved.source_chunk_ids:
            chunk_note = f" · {len(approved.source_chunk_ids)} source chunk(s)"
        hash_note = ""
        if approved.content_hash:
            hash_note = f" · sha256 {approved.content_hash[:12]}…"
        stages.append(
            LineageStageOut(
                stage="approved",
                title="Approved knowledge",
                detail=(
                    f"AK-{approved.id:04d} · {approved.reviewer}{chunk_note}{hash_note}"
                ),
                timestamp=approved.approved_at,
            )
        )
    src_detail = (
        f"{sources_count} chunk(s) — see list below"
        if sources_count
        else "See sources below"
    )
    stages.append(LineageStageOut(stage="sources", title="Source chunks", detail=src_detail))
    return stages


def get_lineage(conn: sqlite3.Connection, review_item_id: int) -> KnowledgeLineageOut:
    row = conn.execute("SELECT * FROM review_items WHERE id = ?", (review_item_id,)).fetchone()
    if row is None:
        raise KeyError("Review item not found")

    plan = _parse_plan(row)
    threshold = 80.0
    if plan and plan.structured:
        threshold = plan.structured.confidence_threshold
    notes = json.loads(row["validator_notes_json"] or "[]")
    score = float(row["confidence_score"])
    validation = LineageValidationOut(
        supported=score >= min(threshold, 55.0),
        confidence_score=score,
        threshold=threshold,
        notes=notes,
    )

    approved_row = _approved_row(conn, review_item_id)
    approved_out = None
    if approved_row:
        chunk_ids: List[int] = []
        if approved_row["source_chunk_ids_json"]:
            try:
                chunk_ids = [int(x) for x in json.loads(approved_row["source_chunk_ids_json"] or "[]")]
            except (TypeError, ValueError, json.JSONDecodeError):
                chunk_ids = []
        approved_out = ApprovedKnowledgeOut(
            id=approved_row["id"],
            review_item_id=approved_row["review_item_id"],
            query=approved_row["query"],
            approved_answer=approved_row["approved_answer"],
            reviewer=approved_row["reviewer"],
            approved_at=datetime.fromisoformat(approved_row["approved_at"]),
            content_hash=approved_row["content_hash"],
            source_chunk_ids=chunk_ids,
        )

    audit = list_audit_trail(conn, review_item_id)
    review = _review_summary(conn, row)
    sources = _sources_enriched(conn, review_item_id)
    timeline = _build_timeline(
        row, plan, validation, review, approved_out, audit, sources_count=len(sources)
    )

    return KnowledgeLineageOut(
        review_item_id=review_item_id,
        knowledge_id=_knowledge_id(approved_row),
        question=row["query"],
        plan=plan,
        draft_answer=row["draft_answer"],
        validation=validation,
        review=review,
        approved_knowledge=approved_out,
        sources=sources,
        audit=audit,
        timeline=timeline,
    )


def list_lineage_index(conn: sqlite3.Connection, limit: int = 50) -> List[LineageIndexItem]:
    rows = conn.execute(
        """
        SELECT
            ri.id,
            ri.query,
            ri.status,
            ri.created_at,
            (
                SELECT id FROM approved_knowledge
                WHERE review_item_id = ri.id
                ORDER BY approved_at DESC
                LIMIT 1
            ) AS ak_id
        FROM review_items ri
        ORDER BY ri.created_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    items: List[LineageIndexItem] = []
    for r in rows:
        kid = f"AK-{int(r['ak_id']):04d}" if r["ak_id"] else None
        items.append(
            LineageIndexItem(
                review_item_id=r["id"],
                knowledge_id=kid,
                question=r["query"],
                status=r["status"],
                created_at=datetime.fromisoformat(r["created_at"]),
            )
        )
    return items
