from fastapi import APIRouter, HTTPException

from backend.app.config import settings
from backend.app.db.connection import get_connection
from backend.app.schemas.rag import RagChatRequest, RagChatResponse, RagStatusOut
from backend.app.services.rag_service import chat, get_status

router = APIRouter(prefix="/rag", tags=["rag"])


@router.get("/status", response_model=RagStatusOut)
def rag_status() -> RagStatusOut:
    return get_status()


@router.post("/chat", response_model=RagChatResponse)
def rag_chat(body: RagChatRequest) -> RagChatResponse:
    if not settings.rag_bot_enabled:
        raise HTTPException(status_code=403, detail="RAG bot is disabled")
    try:
        with get_connection() as conn:
            return chat(conn, body.message, body.history)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
