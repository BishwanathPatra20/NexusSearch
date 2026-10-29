"""Fluent / spatial UI building blocks (information-first, no blur on dense data)."""

from __future__ import annotations

import html
import re
from typing import Any, Dict, List, Optional

import streamlit as st

from frontend.components.knowledge_path_viz import render_knowledge_path


def render_page_header(title: str, subtitle: Optional[str] = None) -> None:
    sub = f'<p class="ns-page-sub">{html.escape(subtitle)}</p>' if subtitle else ""
    st.markdown(
        f"""
<div class="ns-page-header ns-anim-page-in">
  <h1 class="ns-page-title">{html.escape(title)}</h1>
  {sub}
</div>
""",
        unsafe_allow_html=True,
    )


def render_section_label(text: str) -> None:
    st.markdown(
        f'<div class="ns-section-label ns-anim-section">{html.escape(text)}</div>',
        unsafe_allow_html=True,
    )


def render_glass_metrics(metrics: List[Dict[str, Any]]) -> None:
    """Hero / dashboard stats only — light glass, not for tables or result lists."""
    cells = []
    for i, m in enumerate(metrics):
        label = html.escape(str(m.get("label", "")))
        value = html.escape(str(m.get("value", "")))
        hint = m.get("hint")
        hint_html = f'<span class="ns-metric-hint">{html.escape(hint)}</span>' if hint else ""
        delay = 0.1 + i * 0.08
        cells.append(
            f"""
<div class="ns-glass-metric ns-anim-metric" style="animation-delay: {delay}s">
  <div class="ns-metric-value">{value}</div>
  <div class="ns-metric-label">{label}</div>
  {hint_html}
</div>
"""
        )
    st.markdown(f'<div class="ns-glass-metric-row">{"".join(cells)}</div>', unsafe_allow_html=True)


def _highlight_snippet(snippet: str, query: str) -> str:
    safe = html.escape(snippet)
    terms = [t for t in re.split(r"\W+", query.strip()) if len(t) >= 2]
    for term in sorted(set(terms), key=len, reverse=True):
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        safe = pattern.sub(lambda m: f'<mark class="ns-snippet-hit">{m.group(0)}</mark>', safe)
    return safe


def _source_label(hit: Dict[str, Any]) -> str:
    if hit.get("source_type") == "confluence" or (hit.get("file_name") or "").startswith("confluence-"):
        return "Confluence"
    path = hit.get("knowledge_path") or []
    for node in path:
        if node.get("kind") in ("source", "repository", "file"):
            return str(node.get("label", "Document"))
    fn = hit.get("file_name", "")
    if fn.endswith(".md"):
        return "Markdown"
    if fn.endswith(".pdf"):
        return "PDF"
    if fn.endswith(".html"):
        return "Confluence export"
    return "Document"


def render_confluence_live_card(hit: Dict[str, Any], index: int) -> None:
    """Live Confluence page — may not be in the local ingest index."""
    title = html.escape(hit.get("title", "Untitled"))
    snippet = html.escape(hit.get("snippet", ""))
    page_id = html.escape(str(hit.get("page_id", "")))
    space = hit.get("space_key")
    space_chip = html.escape(str(space)) if space else "—"
    indexed = hit.get("indexed_locally")
    badge = "Also in local index" if indexed else "Live from Confluence (not ingested)"
    web_url = hit.get("web_url")

    st.markdown(
        f"""
<div class="ns-result-card ns-result-card--live-cf ns-anim-result">
  <div class="ns-result-head">
    <div class="ns-result-title">{title}</div>
    <div class="ns-result-score">LIVE</div>
  </div>
  <div class="ns-result-meta">
    <span class="ns-chip ns-chip-source">Confluence</span>
    <span class="ns-chip">pageId {page_id}</span>
    <span class="ns-chip">Space {space_chip}</span>
    <span class="ns-chip ns-chip-status">{html.escape(badge)}</span>
  </div>
  <div class="ns-result-snippet">{snippet}</div>
</div>
""",
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns([1, 2])
    with c1:
        if web_url:
            st.link_button("Open in Confluence", web_url, use_container_width=True)
    with c2:
        if not indexed and st.button(
            "Ingest this page",
            key=f"live_cf_ingest_{page_id}_{index}",
            use_container_width=True,
        ):
            from frontend.api_client import confluence_sync_page

            try:
                confluence_sync_page(str(hit.get("page_id")), tags=["confluence", "search-live"])
                st.success("Page indexed — run the same search again for local citations.")
            except Exception as exc:
                st.error(str(exc))
    st.markdown('<div class="ns-result-spacer"></div>', unsafe_allow_html=True)


def render_search_result_card(
    hit: Dict[str, Any],
    index: int,
    query: str,
    search_id: Optional[int],
) -> None:
    """Solid depth card — readable, no glassmorphism."""
    title = html.escape(hit.get("document_title", "Untitled"))
    score = hit.get("score", 0)
    page = hit.get("page_number", "—")
    status = html.escape(str(hit.get("document_status", "active")))
    source = html.escape(_source_label(hit))
    snippet = _highlight_snippet(hit.get("snippet", ""), query)
    chunk_id = hit.get("chunk_id")
    doc_id = hit.get("document_id")
    source_link = hit.get("source_link")

    anim_delay = min(index * 0.06, 0.45)
    st.markdown(
        f"""
<div class="ns-result-card ns-anim-result" style="animation-delay: {anim_delay}s">
  <div class="ns-result-head">
    <div class="ns-result-title">{title}</div>
    <div class="ns-result-score">{score}%</div>
  </div>
  <div class="ns-result-meta">
    <span class="ns-chip ns-chip-source">{source}</span>
    <span class="ns-chip">Page {page}</span>
    <span class="ns-chip ns-chip-status">{status}</span>
  </div>
  <div class="ns-result-snippet">{snippet}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    render_knowledge_path(hit.get("knowledge_path"), compact=True)

    if hit.get("ranking_reasons"):
        st.caption("Ranking: " + " · ".join(hit["ranking_reasons"]))

    if hit.get("related_documents"):
        names = ", ".join(r["title"] for r in hit["related_documents"])
        st.caption(f"Related: {names}")

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        if st.button("View document", key=f"view_doc_{chunk_id}_{index}", use_container_width=True):
            st.session_state["pending_document_id"] = doc_id
            st.switch_page("views/3_Document_Viewer.py")
    with c2:
        if source_link:
            label = "Open in Confluence" if hit.get("source_type") == "confluence" else "Open source"
            st.link_button(label, source_link, use_container_width=True)
        elif hit.get("confluence_page_id"):
            st.caption(f"Confluence pageId {hit['confluence_page_id']}")
    with c3:
        if st.button(f"Record click (#{index})", key=f"click_{chunk_id}_{index}", use_container_width=True):
            from frontend.api_client import record_search_click

            record_search_click(
                query=query,
                chunk_id=chunk_id,
                click_position=index,
                search_id=search_id,
            )
            st.toast("Click recorded for search quality.")

    st.markdown('<div class="ns-result-spacer"></div>', unsafe_allow_html=True)
