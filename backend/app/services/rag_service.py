"""Local RAG: retrieve from FTS corpus + optional Ollama generation."""

from __future__ import annotations

import re
import sqlite3
from typing import Dict, List, Optional

from backend.app.config import settings
from backend.app.schemas.models import SearchHit
from backend.app.schemas.rag import RagChatResponse, RagSourceOut, RagStatusOut
from backend.app.services.governance_audit_service import log_event
from backend.app.services import ollama_client
from backend.app.services.search_service import search

_PLAIN_MAX_CHARS = 480
_PLAIN_MAX_SNIPPETS = 2


def _trim_plain(text: str, max_chars: int = _PLAIN_MAX_CHARS) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_chars:
        return text
    cut = text[: max_chars - 1]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(".,;:") + "…"


def _plain_extractive_answer(query: str, hits: List[SearchHit]) -> str:
    if not hits:
        return (
            "I couldn't find that in your indexed docs. "
            "Try the Search page with different words, or ingest the Confluence page first."
        )
    lead = _trim_plain(hits[0].snippet, max_chars=320)
    lines = [lead]
    if len(hits) > 1 and hits[1].score >= hits[0].score * 0.55:
        extra = _trim_plain(hits[1].snippet, max_chars=180)
        if extra and extra not in lead:
            lines.append(extra)
    body = " ".join(lines)
    return _trim_plain(body, max_chars=_PLAIN_MAX_CHARS)


def _hits_to_sources(hits: List[SearchHit]) -> List[RagSourceOut]:
    out: List[RagSourceOut] = []
    for h in hits:
        out.append(
            RagSourceOut(
                chunk_id=h.chunk_id,
                document_id=h.document_id,
                document_title=h.document_title,
                file_name=h.file_name,
                page_number=h.page_number,
                snippet=h.snippet,
                score=h.score,
            )
        )
    return out


def _context_block(hits: List[SearchHit]) -> str:
    lines: List[str] = []
    for i, hit in enumerate(hits, start=1):
        snippet = " ".join(hit.snippet.split())
        lines.append(
            f"[{i}] title={hit.document_title!r} file={hit.file_name} "
            f"chunk={hit.chunk_id} page={hit.page_number}\n{snippet}"
        )
    return "\n\n".join(lines)


def _build_llm_messages(user_message: str, hits: List[SearchHit], history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    context = _context_block(hits) if hits else "(No indexed sources matched this question.)"
    system = (
        "You are a friendly corpus helper on the user's laptop. "
        "Use ONLY the numbered sources below. "
        "Write in short, plain English that anyone can understand — like explaining to a new coworker. "
        "Rules: "
        "2–5 short sentences OR at most 3 simple bullet points; "
        "no markdown headers, no jargon unless the source uses it; "
        "no long quotes; "
        "add [1] or [2] when you use a source; "
        "if sources are thin, say honestly you are not sure and suggest Search or ingest. "
        "Do not claim official policy — this is exploratory help only.\n\n"
        f"SOURCES:\n{context}"
    )
    messages: List[Dict[str, str]] = [{"role": "system", "content": system}]
    for turn in history[-6:]:
        role = turn.get("role", "user")
        content = (turn.get("content") or "").strip()
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_message.strip()})
    return messages


def get_status() -> RagStatusOut:
    reachable, err = ollama_client.probe()
    return RagStatusOut(
        enabled=settings.rag_bot_enabled,
        llm_enabled=settings.rag_llm_enabled,
        ollama_base_url=settings.ollama_base_url,
        ollama_model=settings.ollama_model,
        ollama_reachable=reachable,
        ollama_error=err,
    )


def chat(
    conn: sqlite3.Connection,
    message: str,
    history: Optional[List[Dict[str, str]]] = None,
) -> RagChatResponse:
    if not settings.rag_bot_enabled:
        raise ValueError("RAG bot is disabled (KNOWLEDGEPILOT_RAG_BOT_ENABLED=false)")

    hist = history or []
    response = search(conn, message.strip(), limit=settings.rag_top_k)
    hits = response.results
    sources = _hits_to_sources(hits)

    ollama_ok, _ = ollama_client.probe()
    mode = "extractive"
    model: Optional[str] = None
    answer: str

    if settings.rag_llm_enabled and ollama_ok:
        try:
            messages = _build_llm_messages(message, hits, hist)
            answer = ollama_client.chat(messages)
            mode = "ollama"
            model = settings.ollama_model
        except Exception:
            answer = _plain_extractive_answer(message, hits)
            mode = "extractive"
    else:
        answer = _plain_extractive_answer(message, hits)

    log_event(
        conn,
        event_type="rag.chat",
        actor="local-user",
        resource_type="rag",
        resource_id=str(response.search_id),
        detail={
            "query": message.strip(),
            "mode": mode,
            "model": model,
            "source_chunk_ids": [s.chunk_id for s in sources[: settings.rag_top_k]],
            "local_hits": len(hits),
        },
    )

    return RagChatResponse(
        answer=answer,
        mode=mode,
        sources=sources,
        ollama_available=ollama_ok,
        model=model,
    )
