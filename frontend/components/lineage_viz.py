"""Lineage visualization — colorful vertical journey (distinct from Home workflow graph)."""

from __future__ import annotations

import html
import re
from typing import Any, Dict, List, Optional

import streamlit as st

_STAGE_META = {
    "question": ("❓", "lg-v2--question", "01"),
    "planner": ("🧭", "lg-v2--planner", "02"),
    "draft": ("✍️", "lg-v2--draft", "03"),
    "validation": ("🛡️", "lg-v2--validation", "04"),
    "review": ("👁️", "lg-v2--review", "05"),
    "approved": ("🏆", "lg-v2--approved", "06"),
    "sources": ("📎", "lg-v2--sources", "07"),
}


def _short(text: str, max_len: int = 120) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def render_lineage_timeline(timeline: Optional[List[Dict[str, Any]]]) -> None:
    """Chunky colorful vertical journey with animated rail."""
    if not timeline:
        st.caption("No lineage timeline for this item.")
        return

    steps: List[str] = []
    n = len(timeline)
    for i, stage in enumerate(timeline):
        stage_key = (stage.get("stage") or "question").lower()
        emoji, css_kind, step_no = _STAGE_META.get(stage_key, ("✦", "lg-v2--question", f"{i+1:02d}"))
        title = html.escape(str(stage.get("title") or "Stage"))
        detail = html.escape(_short(str(stage.get("detail") or "")))
        ts = stage.get("timestamp") or ""
        ts_short = html.escape(str(ts)[:19].replace("T", " ") if ts else "")
        delay = i * 0.14
        is_last = i == n - 1
        connector = ""
        if not is_last:
            connector = f"""
<div class="lg-v2-connector" style="animation-delay: {delay + 0.2}s" aria-hidden="true">
  <div class="lg-v2-connector-fill"></div>
  <div class="lg-v2-connector-spark" style="animation-delay: {i * 0.45}s"></div>
</div>
"""
        steps.append(
            f"""
<article class="lg-v2-step {css_kind}" style="animation-delay: {delay}s">
  <div class="lg-v2-rail-col">
    <div class="lg-v2-node" title="{title}">
      <span class="lg-v2-node-emoji">{emoji}</span>
      <span class="lg-v2-node-ring"></span>
    </div>
    {connector}
  </div>
  <div class="lg-v2-card">
    <div class="lg-v2-card-shine"></div>
    <div class="lg-v2-card-cap">
      <span class="lg-v2-step-no">Step {step_no}</span>
      <span class="lg-v2-cap-emoji">{emoji}</span>
    </div>
    <h3 class="lg-v2-card-title">{title}</h3>
    <p class="lg-v2-card-detail">{detail}</p>
    <div class="lg-v2-card-foot">{ts_short}</div>
  </div>
</article>
"""
        )

    pipeline_html = f"""
<div class="lg-v2" role="img" aria-label="Knowledge lineage journey">
  <div class="lg-v2-aurora" aria-hidden="true">
    <span class="lg-v2-blob lg-v2-blob-a"></span>
    <span class="lg-v2-blob lg-v2-blob-b"></span>
    <span class="lg-v2-blob lg-v2-blob-c"></span>
  </div>
  <header class="lg-v2-header">
    <h2 class="lg-v2-header-title">Knowledge journey</h2>
    <p class="lg-v2-header-sub">{n} stages</p>
  </header>
  <div class="lg-v2-track">
    {"".join(steps)}
  </div>
</div>
"""
    st.markdown(pipeline_html, unsafe_allow_html=True)


def render_lineage_summary_strip(data: Dict[str, Any]) -> None:
    """Compact status chips under the journey."""
    kid = data.get("knowledge_id")
    val = data.get("validation") or {}
    rev = data.get("review") or {}
    sources_n = len(data.get("sources") or [])
    chips = []
    if kid:
        chips.append(f'<span class="lg-v2-chip lg-v2-chip--ak">{html.escape(str(kid))}</span>')
    chips.append(f'<span class="lg-v2-chip">Sources <strong>{sources_n}</strong></span>')
    chips.append(
        f'<span class="lg-v2-chip">Validation <strong>{val.get("confidence_score", "—")}%</strong></span>'
    )
    chips.append(f'<span class="lg-v2-chip">Review <strong>{html.escape(str(rev.get("status", "—")))}</strong></span>')
    st.markdown(
        f'<div class="lg-v2-chips">{"".join(chips)}</div>',
        unsafe_allow_html=True,
    )


def section(title: str, body: str) -> None:
    st.markdown(f"**{title}**")
    st.markdown("---")
    st.markdown(body)
