"""Optional local LLM via Ollama (127.0.0.1 only by default)."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import httpx

from backend.app.config import settings

logger = logging.getLogger("knowledgepilot.ollama")


def _client() -> httpx.Client:
    return httpx.Client(base_url=settings.ollama_base_url.rstrip("/"), timeout=settings.ollama_timeout_sec)


def probe() -> Tuple[bool, Optional[str]]:
    if not settings.rag_llm_enabled:
        return False, "Local LLM disabled (KNOWLEDGEPILOT_RAG_LLM_ENABLED=false)"
    try:
        with _client() as client:
            r = client.get("/api/tags")
            if r.status_code != 200:
                return False, f"Ollama HTTP {r.status_code}"
            return True, None
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def chat(messages: List[Dict[str, str]], *, model: Optional[str] = None) -> str:
    model_name = (model or settings.ollama_model).strip()
    payload: Dict[str, Any] = {
        "model": model_name,
        "messages": messages,
        "stream": False,
        "options": {"temperature": settings.ollama_temperature},
    }
    with _client() as client:
        r = client.post("/api/chat", json=payload)
        r.raise_for_status()
        data = r.json()
    message = data.get("message") or {}
    content = str(message.get("content") or "").strip()
    if not content:
        raise RuntimeError("Ollama returned an empty response")
    return content
