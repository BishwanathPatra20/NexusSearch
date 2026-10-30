"""Landing content for NexusSearch home — Contra-style split hero + ISO accent card."""

from __future__ import annotations

import html
from typing import Dict, List, Optional

import streamlit as st

from frontend.components.workflow_graph import render_workflow_graph

_SOURCE_LABELS = {
    "confluence": "Confluence",
    "onboarding": "Onboarding",
    "folder": "Folder",
    "upload": "Upload",
}


def _source_label(source_type: Optional[str]) -> str:
    return _SOURCE_LABELS.get((source_type or "upload").lower(), source_type or "Upload")


def _sort_docs_newest(docs: List[Dict]) -> List[Dict]:
    return sorted(
        docs,
        key=lambda d: str(d.get("upload_date") or ""),
        reverse=True,
    )


def _render_recent_catalog(docs: List[Dict]) -> None:
    st.markdown(
        """
<div class="ns-workflow-panel ns-anim-panel">
  <h4>Recent catalog</h4>
  <p>Newest documents in your local index — titles and source type.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    if not docs:
        st.caption("Nothing indexed yet — ingest demo corpus or your Confluence pages.")
        if st.button("Open Ingest hub", key="home_catalog_ingest", use_container_width=True):
            st.switch_page("views/1_Upload.py")
        return
    for doc in _sort_docs_newest(docs)[:6]:
        title = doc.get("title") or doc.get("file_name") or "Untitled"
        src = _source_label(doc.get("source_type"))
        uploaded = doc.get("upload_date", "")
        if isinstance(uploaded, str) and "T" in uploaded:
            uploaded = uploaded.replace("T", " ")[:16]
        st.markdown(f"**{html.escape(str(title))}**  \n`{html.escape(src)}` · {html.escape(str(uploaded))}")
    if len(docs) > 6:
        st.caption(f"+ {len(docs) - 6} more in the library.")
    if st.button("Open Document viewer", key="home_catalog_viewer", use_container_width=True):
        st.switch_page("views/3_Document_Viewer.py")


def _render_review_queue_panel(api_ok: bool) -> None:
    st.markdown(
        """
<div class="ns-workflow-panel ns-anim-panel">
  <h4>Review queue</h4>
  <p>Pending <strong>Governed Ask</strong> drafts awaiting approval.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    if not api_ok:
        st.caption("Start the API to see pending reviews.")
        return
    try:
        from frontend.api_client import list_reviews

        pending = list_reviews("pending")
    except Exception:
        st.caption("Could not load the review queue.")
        return
    count = len(pending)
    st.metric("Pending", count)
    for item in pending[:3]:
        q = item.get("query", "")
        short = q if len(q) <= 52 else q[:49] + "…"
        st.caption(f"#{item.get('id')} · {short}")
    if count > 3:
        st.caption(f"+ {count - 3} more waiting.")
    if st.button("Open Governed Ask", key="home_catalog_queue", use_container_width=True):
        st.switch_page("views/5_Governed_Ask.py")


def _social_proof_line(doc_count: Optional[int], search_count: Optional[int]) -> str:
    parts: List[str] = []
    if doc_count is not None:
        parts.append(f"{doc_count:,} document{'s' if doc_count != 1 else ''} indexed")
    if search_count is not None:
        parts.append(f"{search_count:,} search{'es' if search_count != 1 else ''} logged")
    if not parts:
        return "Connect the API to see live corpus stats."
    return " · ".join(parts)


def _home_bg_decor_html() -> str:
    return """
<div class="ns-home-bg-decor" aria-hidden="true">
  <div class="ns-home-glass ns-home-glass--torus ns-home-glass--1"></div>
  <div class="ns-home-glass ns-home-glass--torus ns-home-glass--2"></div>
  <div class="ns-home-glass ns-home-glass--disc ns-home-glass--3"></div>
  <div class="ns-home-glow ns-home-glow--right"></div>
</div>
"""


def _hero_grid_html(
    version: str,
    doc_count: Optional[int] = None,
    search_count: Optional[int] = None,
) -> str:
    ver = html.escape(version)
    docs_label = f"{doc_count:,}" if doc_count is not None else "—"
    searches_label = f"{search_count:,}" if search_count is not None else "—"
    return f"""
<div class="ns-home-hero-grid">
  <div class="ns-home-copy">
    <span class="ns-home-pill">Office-safe · 127.0.0.1 · no cloud LLMs</span>
    <h1 class="ns-home-title">
      <span class="ns-home-title-line" style="font-size: clamp(3.4rem, 7.2vw, 5rem);">
        <span class="ns-home-title-sans">Search. Review.</span>
        <em class="ns-home-title-em">Approve.</em>
      </span>
    </h1>
    <p class="ns-home-lead">
      Local-first knowledge governance — ingest documents, search with citations,
      and promote human-reviewed answers with auditable lineage.
    </p>
    <ul class="ns-home-value-list">
      <li>Governed answers with source citations — no external LLM required</li>
      <li>Human review queue before knowledge is promoted to AK records</li>
      <li>Lineage from approved answers back to document chunks</li>
    </ul>
  </div>
  <div class="ns-home-visual" aria-hidden="false">
    <div class="ns-home-pro-stack">
      <article class="ns-home-pro-card">
        <header class="ns-home-pro-head">
          <h2 class="ns-home-pro-title">NexusSearch</h2>
          <span class="ns-home-pro-badge">v{ver} · local</span>
        </header>
        <ul class="ns-home-pro-features">
          <li>Citation-backed search on your corpus</li>
          <li>Extractive drafts with human review</li>
          <li>Approved knowledge &amp; lineage (AK-XXXX)</li>
        </ul>
        <footer class="ns-home-pro-foot">
          <div class="ns-home-pro-identity">
            <div class="ns-home-pro-avatar" aria-hidden="true">NS</div>
            <div class="ns-home-pro-identity-text">
              <span class="ns-home-pro-host">127.0.0.1 · office-safe</span>
              <span class="ns-home-pro-status"><span class="ns-home-pro-dot"></span>Governed mode</span>
            </div>
          </div>
          <div class="ns-home-pro-stat">
            <span class="ns-home-pro-stat-label">Corpus index</span>
            <span class="ns-home-pro-stat-value">{docs_label}</span>
            <span class="ns-home-pro-stat-sub">{searches_label} searches logged</span>
          </div>
        </footer>
      </article>
      <div class="ns-home-pro-float ns-home-pro-float--ak">
        <div class="ns-home-pro-float-stars" aria-hidden="true">★★★★★</div>
        <p class="ns-home-pro-float-quote">Reviewed and promoted — traceable to source chunks.</p>
        <span class="ns-home-pro-float-id">AK-0011</span>
        <span class="ns-home-pro-float-role">Approved answer</span>
      </div>
    </div>
  </div>
</div>
"""


def render_home(
    api_ok: bool,
    status: Optional[Dict],
    error: Optional[str],
) -> None:
    doc_count: Optional[int] = None
    search_count: Optional[int] = None
    docs: List[Dict] = []
    version = "1.1.0"
    if status:
        version = str(status.get("version", version))

    if api_ok:
        try:
            from frontend.api_client import analytics_summary, list_documents

            docs = list_documents()
            doc_count = len(docs)
            search_count = int(analytics_summary().get("total_searches", 0))
        except Exception:
            pass

    proof_line = _social_proof_line(doc_count, search_count)

    st.markdown(
        """
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Plus+Jakarta+Sans:wght@700;800&display=swap">
<div class="ns-home-landing">
""",
        unsafe_allow_html=True,
    )

    st.markdown(_home_bg_decor_html(), unsafe_allow_html=True)
    st.markdown(_hero_grid_html(version, doc_count, search_count), unsafe_allow_html=True)

    st.markdown('<div class="ns-home-hero-actions">', unsafe_allow_html=True)
    st.page_link(
        "views/1_Upload.py",
        label="Ingest demo corpus",
        use_container_width=False,
    )
    st.markdown(
        f'<p class="ns-home-proof">{html.escape(proof_line)}</p>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="ns-home-workflow-block">'
        '<div class="ns-section-label ns-anim-section">Workflows</div>',
        unsafe_allow_html=True,
    )
    render_workflow_graph()
    st.markdown("</div>", unsafe_allow_html=True)

    if api_ok:
        try:
            from frontend.api_client import agent_dashboard

            dash = agent_dashboard()
            health = dash.get("health", "green")
            if health not in ("green", "yellow", "red"):
                health = "green"
            health_label = health.title()
            pending = dash.get("pending_reviews", 0)
            gaps = dash.get("zero_result_recurring_groups", 0)
            st.markdown('<div class="ns-home-automation-block">', unsafe_allow_html=True)
            st.markdown(
                '<div class="ns-section-label ns-anim-section">Automation health</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
<div class="ns-home-health ns-home-health--{health}" role="status">
  <span class="ns-home-health-dot" aria-hidden="true"></span>
  <span class="ns-home-health-text">
    Automation health · <strong>{html.escape(health_label)}</strong>
    · {pending} pending review{'s' if pending != 1 else ''}
    · {gaps} recurring search gap{'s' if gaps != 1 else ''}
  </span>
</div>
""",
                unsafe_allow_html=True,
            )
            if health != "green":
                for reason in dash.get("health_reasons") or []:
                    st.caption(f"• {reason}")
                actions = dash.get("health_actions") or []
                if actions:
                    with st.expander("What to do next", expanded=False):
                        for action in actions:
                            st.markdown(f"- {action}")
                        b1, b2 = st.columns(2)
                        with b1:
                            if st.button("Governed Ask", key="home_dash_ask", use_container_width=True):
                                st.switch_page("views/5_Governed_Ask.py")
                        with b2:
                            if st.button("Analytics", key="home_dash_analytics", use_container_width=True):
                                st.switch_page("views/4_Analytics.py")
            st.markdown("</div>", unsafe_allow_html=True)
        except Exception:
            pass
    elif error:
        st.error(
            "Cannot reach the NexusSearch API. Run `./scripts/start-api.sh` and check "
            "http://127.0.0.1:8000/health."
        )
        st.caption(error)

    st.markdown('<div class="ns-home-catalog-block">', unsafe_allow_html=True)
    st.markdown(
        '<div class="ns-section-label ns-anim-section">Recent catalog</div>',
        unsafe_allow_html=True,
    )
    cat_left, cat_right = st.columns(2, gap="large")
    with cat_left:
        _render_recent_catalog(docs if api_ok else [])
    with cat_right:
        _render_review_queue_panel(api_ok)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
