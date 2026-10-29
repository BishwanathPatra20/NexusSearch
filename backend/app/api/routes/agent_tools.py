"""Read-only agent/MCP-friendly JSON tools (localhost + optional API key)."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from backend.app.config import settings
from backend.app.db.connection import get_connection
from backend.app.services.lineage_service import get_lineage, list_lineage_index
from backend.app.services.search_service import search

router = APIRouter(prefix="/agent-tools", tags=["agent-tools"])


def _require_agent_auth(authorization: Optional[str] = Header(None)) -> None:
    key = (settings.api_key or "").strip()
    if not key:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    if authorization.removeprefix("Bearer ").strip() != key:
        raise HTTPException(status_code=403, detail="Invalid API key")


@router.get("/search")
def agent_search(
    q: str = Query(..., min_length=1, max_length=500),
    limit: int = Query(10, ge=1, le=25),
    _: None = Depends(_require_agent_auth),
) -> Dict[str, Any]:
    with get_connection() as conn:
        resp = search(conn, q, limit=limit)
    return resp.model_dump()


@router.get("/documents")
def agent_list_documents(
    limit: int = Query(25, ge=1, le=100),
    _: None = Depends(_require_agent_auth),
) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, title, file_name, source_type, source_uri, status, upload_date
            FROM documents
            ORDER BY upload_date DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


@router.get("/lineage/index")
def agent_lineage_index(
    limit: int = Query(25, ge=1, le=100),
    _: None = Depends(_require_agent_auth),
) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        items = list_lineage_index(conn, limit=limit)
    return [i.model_dump() for i in items]


@router.get("/lineage/{review_item_id}")
def agent_lineage_detail(
    review_item_id: int,
    _: None = Depends(_require_agent_auth),
) -> Dict[str, Any]:
    with get_connection() as conn:
        try:
            return get_lineage(conn, review_item_id).model_dump()
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
