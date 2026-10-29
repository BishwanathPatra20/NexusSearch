"""Animated workflow graph — original circles; whole node links to each page."""

from __future__ import annotations

import html

import streamlit as st

# url_path must match st.Page(..., url_path=...) in streamlit_app.py
_STEPS = [
    ("New hire guide", "KT · access · Confluence", "onboarding"),
    ("Search", "Cited results & paths", "search"),
    ("Governed Ask", "Review & approve", "governed-ask"),
    ("Lineage", "AK-XXXX → sources", "lineage"),
]


def render_workflow_graph() -> None:
    nodes_html = []
    for i, (title, sub, url_path) in enumerate(_STEPS):
        delay = i * 0.35
        safe_title = html.escape(title)
        safe_sub = html.escape(sub)
        nodes_html.append(
            f"""
<a class="ns-flow-node-link" href="/{html.escape(url_path)}" title="Open {safe_title}">
  <div class="ns-flow-node" style="animation-delay: {delay}s">
    <div class="ns-flow-ring"></div>
    <div class="ns-flow-title">{safe_title}</div>
    <div class="ns-flow-sub">{safe_sub}</div>
  </div>
</a>
"""
        )
        if i < len(_STEPS) - 1:
            nodes_html.append(
                f"""
<div class="ns-flow-connector" aria-hidden="true">
  <div class="ns-flow-line"></div>
  <div class="ns-flow-packet" style="animation-delay: {i * 0.4}s"></div>
  <span class="ns-flow-chevron">›</span>
</div>
"""
            )

    st.markdown(
        f"""
<div class="ns-flow-graph" role="navigation" aria-label="Workflow: guide, search, ask, lineage">
  {"".join(nodes_html)}
</div>
""",
        unsafe_allow_html=True,
    )
