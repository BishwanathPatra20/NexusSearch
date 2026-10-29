"""RAG bot API and extractive fallback."""

import sqlite3

from backend.app.db.schema import init_db
from backend.app.services.rag_service import chat, get_status


def test_rag_status_disabled_flags():
    from backend.app.config import settings

    assert settings.rag_bot_enabled is True


def test_rag_chat_extractive_without_ollama(monkeypatch):
    monkeypatch.setattr("backend.app.services.rag_service.settings.rag_llm_enabled", False)

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)

    out = chat(conn, "onboarding databricks", history=[])
    assert out.mode == "extractive"
    assert "Answer draft" not in out.answer
    assert "Question:" not in out.answer
    assert out.disclaimer


def test_rag_status_structure():
    st = get_status()
    assert st.enabled is True
    assert st.ollama_base_url.startswith("http")
