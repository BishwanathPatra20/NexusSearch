from typing import Optional

from fastapi import APIRouter, Query

from backend.app.db.connection import get_connection
from backend.app.schemas.models import SearchClickRequest, SearchResponse
from backend.app.schemas.search_filters import SearchFilters
from backend.app.services.search_service import record_click, search

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
def search_documents(
    q: str = Query(..., min_length=1, max_length=500),
    status: Optional[str] = Query(None, description="active, deprecated, archived, draft"),
    tag: Optional[str] = Query(None),
    file_type: Optional[str] = Query(None, description="pdf, docx, txt, md, html"),
    version_label: Optional[str] = Query(None),
) -> SearchResponse:
    filters = SearchFilters(
        status=status,
        tag=tag,
        file_type=file_type,
        version_label=version_label,
    )
    with get_connection() as conn:
        return search(conn, q, filters=filters)


@router.post("/click", status_code=204)
def search_click(body: SearchClickRequest) -> None:
    with get_connection() as conn:
        record_click(
            conn,
            query=body.query,
            chunk_id=body.chunk_id,
            click_position=body.click_position,
            search_id=body.search_id,
        )
