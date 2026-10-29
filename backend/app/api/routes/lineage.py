from typing import List

from fastapi import APIRouter, HTTPException, Query

from backend.app.db.connection import get_connection
from backend.app.schemas.models import KnowledgeLineageOut, LineageIndexItem
from backend.app.services.lineage_service import get_lineage, list_lineage_index

router = APIRouter(prefix="/lineage", tags=["lineage"])


@router.get("", response_model=List[LineageIndexItem])
def lineage_index(limit: int = Query(50, ge=1, le=200)) -> List[LineageIndexItem]:
    with get_connection() as conn:
        return list_lineage_index(conn, limit=limit)


@router.get("/{review_item_id}", response_model=KnowledgeLineageOut)
def lineage_detail(review_item_id: int) -> KnowledgeLineageOut:
    try:
        with get_connection() as conn:
            return get_lineage(conn, review_item_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Review item not found")
