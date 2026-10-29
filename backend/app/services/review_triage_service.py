"""Group similar pending reviews for faster human triage."""

from __future__ import annotations

import re
import sqlite3
from typing import List, Optional

from backend.app.schemas.agents import (
    ReviewTriageBatch,
    ReviewTriageItem,
    ReviewTriageResponse,
    TriageBatchApproveResult,
)
from backend.app.services.review_service import approve_item, list_review_items

_ACCESS = re.compile(r"\b(access|permission|entitlement|provisioning|ad group)\b", re.I)
_CONFLUENCE = re.compile(r"\b(confluence|wiki|page)\b", re.I)
_TICKET = re.compile(r"\b(ticket|jira|servicenow|request)\b", re.I)


def _group_key(query: str) -> tuple[str, str]:
    q = query.strip()
    if _ACCESS.search(q):
        return ("access_requests", "Access & permissions")
    if _CONFLUENCE.search(q):
        return ("confluence", "Confluence / wiki")
    if _TICKET.search(q):
        return ("tickets", "Tickets & requests")
    words = re.findall(r"[a-z0-9]+", q.lower())
    key = "_".join(words[:4]) if words else "other"
    label = " ".join(words[:4]).title() if words else "Other"
    return (key[:48], label[:60])


def build_triage(conn: sqlite3.Connection, status: str = "pending") -> ReviewTriageResponse:
    items = list_review_items(conn, status="pending")

    buckets: dict[str, ReviewTriageBatch] = {}
    for item in items:
        key, label = _group_key(item.query)
        if key not in buckets:
            buckets[key] = ReviewTriageBatch(
                group_key=key,
                label=label,
                count=0,
                items=[],
            )
        batch = buckets[key]
        batch.count += 1
        batch.items.append(
            ReviewTriageItem(
                review_id=item.id,
                query=item.query,
                confidence_score=item.confidence_score,
                status=item.status,
            )
        )

    batches = list(buckets.values())
    for batch in batches:
        batch.items.sort(key=lambda x: (-x.confidence_score, x.review_id))
    batches.sort(key=lambda b: (-b.count, b.label))

    return ReviewTriageResponse(
        total_pending=len(items),
        batches=batches,
    )


def batch_approve(
    conn: sqlite3.Connection,
    min_confidence: float,
    max_count: int,
    group_key: Optional[str] = None,
) -> TriageBatchApproveResult:
    triage = build_triage(conn)
    approved_ids: List[int] = []
    skipped: List[str] = []

    for batch in triage.batches:
        if group_key and batch.group_key != group_key:
            continue
        for item in batch.items:
            if len(approved_ids) >= max_count:
                skipped.append("max_count reached")
                break
            if item.confidence_score < min_confidence:
                skipped.append(f"#{item.review_id} below {min_confidence}%")
                continue
            try:
                approve_item(
                    conn,
                    item.review_id,
                    reviewer="batch-triage",
                    comment=f"Batch approve (≥{min_confidence}% confidence)",
                )
                approved_ids.append(item.review_id)
            except KeyError:
                skipped.append(f"#{item.review_id} not found")

    return TriageBatchApproveResult(approved_ids=approved_ids, skipped=skipped)
