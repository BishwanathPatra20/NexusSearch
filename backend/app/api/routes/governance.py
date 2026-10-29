"""Governance audit API (immutable event log)."""

from typing import List, Optional

from fastapi import APIRouter, Query

from backend.app.db.connection import get_connection
from backend.app.services.governance_audit_service import GovernanceAuditEventOut, list_events

router = APIRouter(prefix="/governance", tags=["governance"])


@router.get("/audit", response_model=List[GovernanceAuditEventOut])
def governance_audit(
    limit: int = Query(100, ge=1, le=500),
    event_type: Optional[str] = Query(None),
) -> List[GovernanceAuditEventOut]:
    with get_connection() as conn:
        return list_events(conn, limit=limit, event_type=event_type)
