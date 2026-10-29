"""Immutable governance audit trail (search, review, sync, live Confluence)."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GovernanceAuditEventOut(BaseModel):
    id: int
    event_type: str
    actor: str
    resource_type: str
    resource_id: Optional[str] = None
    detail_json: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


def log_event(
    conn: sqlite3.Connection,
    *,
    event_type: str,
    actor: str = "local-user",
    resource_type: str = "system",
    resource_id: Optional[str] = None,
    detail: Optional[Dict[str, Any]] = None,
) -> None:
    conn.execute(
        """
        INSERT INTO governance_audit_events (
            event_type, actor, resource_type, resource_id, detail_json
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            event_type,
            actor,
            resource_type,
            resource_id,
            json.dumps(detail or {}, default=str),
        ),
    )


def list_events(
    conn: sqlite3.Connection,
    *,
    limit: int = 100,
    event_type: Optional[str] = None,
) -> List[GovernanceAuditEventOut]:
    if event_type:
        rows = conn.execute(
            """
            SELECT * FROM governance_audit_events
            WHERE event_type = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (event_type, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT * FROM governance_audit_events
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    out: List[GovernanceAuditEventOut] = []
    for row in rows:
        out.append(
            GovernanceAuditEventOut(
                id=int(row["id"]),
                event_type=row["event_type"],
                actor=row["actor"],
                resource_type=row["resource_type"],
                resource_id=row["resource_id"],
                detail_json=json.loads(row["detail_json"] or "{}"),
                created_at=datetime.fromisoformat(row["created_at"]),
            )
        )
    return out
