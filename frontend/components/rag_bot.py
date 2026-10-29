"""Floating local RAG assistant — bottom-right dock (Android-style FAB)."""

from __future__ import annotations

import base64
import html
import os
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

from frontend.api_client import rag_chat, rag_status

_ICON_PATH = Path(__file__).resolve().parent.parent / "static" / "rag-bot-icon.png"
_RAG_ENABLED_ENV = os.environ.get("KNOWLEDGEPILOT_RAG_BOT_ENABLED", "true").strip().lower() not in (
    "0",
    "false",
    "no",
)


def _icon_data_uri() -> str:
    if not _ICON_PATH.is_file():
        return ""
    encoded = base64.b64encode(_ICON_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def inject_rag_fab_global_styles() -> None:
    icon_uri = _icon_data_uri()
    if icon_uri:
        fab_bg = f"url('{icon_uri}')"
        fab_bg_rule = f"""
  background: {fab_bg} center center / 100% 100% no-repeat !important;
  background-color: transparent !important;
  border: none !important;
"""
    else:
        fab_bg_rule = """
  background: linear-gradient(135deg, #22c55e, #16a34a) center/cover no-repeat !important;
  border: 2px solid #15803d !important;
"""
    st.markdown(
        f"""
<style>
/* FAB — bottom-right (icon fills circle) */
.stApp .st-key-rag_fab_shell {{
  position: fixed !important;
  bottom: 20px !important;
  right: 20px !important;
  left: auto !important;
  top: auto !important;
  z-index: 1000004 !important;
  width: 56px !important;
  min-width: 56px !important;
  max-width: 56px !important;
  margin: 0 !important;
  padding: 0 !important;
  background: transparent !important;
  border: none !important;
}}
.st-key-rag_fab_shell [data-testid="stVerticalBlock"] {{
  gap: 0 !important;
}}
.st-key-rag_fab_toggle,
.st-key-rag_fab_toggle [data-testid="stButton"] {{
  width: 56px !important;
  min-width: 56px !important;
}}
.st-key-rag_fab_toggle button {{
  width: 56px !important;
  height: 56px !important;
  min-height: 56px !important;
  max-width: 56px !important;
  border-radius: 50% !important;
  padding: 0 !important;
  overflow: hidden !important;
  {fab_bg_rule}
  box-shadow: 0 6px 20px rgba(22, 163, 74, 0.45) !important;
  line-height: 0 !important;
  animation: ns-rag-fab-pulse 2.8s ease-in-out infinite;
}}
.st-key-rag_fab_toggle button:hover {{
  transform: scale(1.05);
  filter: brightness(1.05);
}}
.st-key-rag_fab_toggle button p,
.st-key-rag_fab_toggle button span,
.st-key-rag_fab_toggle button div {{
  display: none !important;
  visibility: hidden !important;
}}

/* Chat panel — always light (readable on any app theme) */
.stApp .st-key-rag_panel_shell {{
  position: fixed !important;
  bottom: 88px !important;
  right: 20px !important;
  left: auto !important;
  top: auto !important;
  z-index: 1000003 !important;
  width: min(380px, calc(100vw - 40px)) !important;
  max-width: min(380px, calc(100vw - 40px)) !important;
  margin: 0 !important;
  padding: 0 !important;
  background: #ffffff !important;
  color: #0f172a !important;
  border: 1px solid rgba(15, 23, 42, 0.12) !important;
  border-radius: 16px !important;
  box-shadow: 0 16px 48px rgba(15, 23, 42, 0.18) !important;
  overflow: hidden !important;
}}
.st-key-rag_panel_shell [data-testid="stVerticalBlock"] {{
  gap: 0.35rem !important;
  padding: 0.75rem 0.85rem 0.65rem !important;
  background: #ffffff !important;
}}
.st-key-rag_panel_shell p,
.st-key-rag_panel_shell span,
.st-key-rag_panel_shell label,
.st-key-rag_panel_shell strong,
.st-key-rag_panel_shell [data-testid="stMarkdownContainer"],
.st-key-rag_panel_shell [data-testid="stMarkdownContainer"] p {{
  color: #0f172a !important;
  -webkit-text-fill-color: #0f172a !important;
}}
.st-key-rag_panel_shell [data-testid="stCaptionContainer"] p {{
  color: #475569 !important;
  -webkit-text-fill-color: #475569 !important;
}}
.st-key-rag_panel_shell [data-testid="stChatMessage"] {{
  padding: 0.35rem 0 !important;
  background: transparent !important;
}}
.st-key-rag_panel_shell [data-testid="stChatMessageContent"] {{
  color: #0f172a !important;
  background: #f1f5f9 !important;
  border: 1px solid rgba(15, 23, 42, 0.08) !important;
  border-radius: 10px !important;
  padding: 0.5rem 0.65rem !important;
}}
.st-key-rag_panel_shell [data-testid="stAlert"] {{
  background: #fef3c7 !important;
  color: #78350f !important;
}}
.st-key-rag_panel_shell [data-testid="stAlert"] p {{
  color: #78350f !important;
  -webkit-text-fill-color: #78350f !important;
}}
.st-key-rag_messages {{
  max-height: min(280px, 42vh);
  overflow-y: auto;
  margin: 0.25rem 0 0.5rem;
  padding-right: 0.25rem;
  background: #ffffff !important;
}}
.st-key-rag_panel_shell .stTextInput input {{
  font-size: 0.88rem !important;
  color: #0f172a !important;
  background: #ffffff !important;
  border: 1px solid rgba(15, 23, 42, 0.18) !important;
}}
.st-key-rag_panel_shell [data-testid="stTextInput"] label {{
  color: #0f172a !important;
}}
.st-key-rag_panel_shell .st-key-rag_close_panel button {{
  min-width: 2rem !important;
  width: 2rem !important;
  padding: 0.2rem !important;
  color: #0f172a !important;
  background: #f1f5f9 !important;
  border: 1px solid rgba(15, 23, 42, 0.12) !important;
}}
.st-key-rag_panel_shell [data-testid="stFormSubmitButton"] button,
.st-key-rag_panel_shell .st-key-rag_send_btn button {{
  color: #0f172a !important;
  background: #e2e8f0 !important;
}}
.st-key-rag_panel_shell .st-key-rag_clear_chat button {{
  color: #0f172a !important;
  background: #f8fafc !important;
  border: 1px solid rgba(15, 23, 42, 0.12) !important;
}}
@keyframes ns-rag-fab-pulse {{
  0%, 100% {{ box-shadow: 0 6px 20px rgba(22, 163, 74, 0.4); }}
  50% {{ box-shadow: 0 8px 24px rgba(22, 163, 74, 0.55), 0 0 0 5px rgba(34, 197, 94, 0.15); }}
}}
</style>
""",
        unsafe_allow_html=True,
    )


def _fetch_status() -> Dict[str, Any]:
    try:
        return rag_status()
    except Exception as exc:
        return {
            "enabled": _RAG_ENABLED_ENV,
            "llm_enabled": True,
            "ollama_reachable": False,
            "ollama_model": "llama3.2",
            "ollama_error": str(exc),
            "api_unreachable": True,
        }


def _ensure_session() -> None:
    if "rag_panel_open" not in st.session_state:
        st.session_state.rag_panel_open = False
    if "rag_messages" not in st.session_state:
        st.session_state.rag_messages = []


def _submit_message(messages: List[Dict[str, Any]], prompt: str, status: Dict[str, Any]) -> None:
    prompt = prompt.strip()
    if not prompt:
        return
    messages.append({"role": "user", "content": prompt})
    history = [{"role": m["role"], "content": m["content"]} for m in messages[:-1]]
    if status.get("api_unreachable"):
        messages.append(
            {
                "role": "assistant",
                "content": "API unreachable — restart with `./scripts/start-api.sh`, then try again.",
                "sources": [],
            }
        )
    else:
        try:
            resp = rag_chat(prompt, history=history)
            messages.append(
                {
                    "role": "assistant",
                    "content": resp.get("answer") or "",
                    "sources": resp.get("sources") or [],
                    "mode": resp.get("mode"),
                }
            )
        except Exception as exc:
            messages.append(
                {"role": "assistant", "content": f"RAG request failed: {exc}", "sources": []}
            )
    st.session_state.rag_messages = messages


def _render_panel(status: Dict[str, Any]) -> None:
    messages: List[Dict[str, Any]] = st.session_state.rag_messages

    h1, h2 = st.columns([5, 1])
    with h1:
        st.markdown("**Corpus assistant**")
    with h2:
        if st.button("✕", key="rag_close_panel", help="Minimize"):
            st.session_state.rag_panel_open = False
            st.rerun()

    st.caption("Short plain-English answers from your index · not official policy")
    if status.get("api_unreachable"):
        st.warning("Restart API: `./scripts/start-api.sh`")
    elif status.get("ollama_reachable"):
        st.caption(f"Ollama · {status.get('ollama_model', 'local model')}")
    else:
        st.caption("Extractive mode (Ollama optional for natural replies)")

    with st.container(key="rag_messages"):
        if not messages:
            st.markdown(
                '<p style="color:#475569;font-size:0.85rem;margin:0.5rem 0;">'
                "Ask about ingested docs, onboarding, or Confluence pages in your index."
                "</p>",
                unsafe_allow_html=True,
            )
        for msg in messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                sources = msg.get("sources") or []
                if sources and msg["role"] == "assistant":
                    bits = [
                        html.escape(s.get("document_title") or s.get("file_name") or "source")
                        for s in sources[:4]
                    ]
                    if bits:
                        st.caption("Sources: " + " · ".join(bits))

    with st.form("rag_chat_form", clear_on_submit=True, border=False):
        c_in, c_go = st.columns([5, 1])
        with c_in:
            draft = st.text_input(
                "Message",
                placeholder="Ask about your corpus…",
                key="rag_prompt_input",
                label_visibility="collapsed",
            )
        with c_go:
            send = st.form_submit_button("➤", use_container_width=True)

    if send and draft.strip():
        _submit_message(list(messages), draft, status)
        st.rerun()

    if st.button("Clear conversation", key="rag_clear_chat"):
        st.session_state.rag_messages = []
        st.rerun()


def render_rag_bot_dock() -> None:
    if not _RAG_ENABLED_ENV:
        return

    status = _fetch_status()
    if not status.get("enabled", True):
        return

    _ensure_session()

    if st.session_state.rag_panel_open:
        with st.container(key="rag_panel_shell"):
            _render_panel(status)

    with st.container(key="rag_fab_shell"):
        if st.button(" ", key="rag_fab_toggle", help="Corpus assistant"):
            st.session_state.rag_panel_open = not st.session_state.rag_panel_open
            st.rerun()
