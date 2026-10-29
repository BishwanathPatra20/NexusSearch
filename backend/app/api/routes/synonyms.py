from fastapi import APIRouter, HTTPException

from backend.app.db.connection import get_connection
from backend.app.services.synonym_proposal_service import approve, dismiss, list_pending

router = APIRouter(prefix="/synonyms", tags=["synonyms"])


@router.get("/proposals")
def synonym_proposals_pending() -> dict:
    with get_connection() as conn:
        return {"items": list_pending(conn)}


@router.post("/proposals/{proposal_id}/approve")
def synonym_proposal_approve(proposal_id: int) -> dict:
    try:
        with get_connection() as conn:
            return approve(conn, proposal_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Proposal not found")


@router.post("/proposals/{proposal_id}/dismiss")
def synonym_proposal_dismiss(proposal_id: int) -> dict:
    with get_connection() as conn:
        dismiss(conn, proposal_id)
    return {"id": proposal_id, "status": "dismissed"}
