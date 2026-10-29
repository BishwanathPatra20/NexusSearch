"""Minimal motion for Analytics — calm fades, no home/lineage effects."""

from __future__ import annotations

import html
from typing import Any, Dict, List, Optional

import streamlit as st


def open_analytics_shell() -> None:
    st.markdown('<div class="ns-analytics-page">', unsafe_allow_html=True)


def close_analytics_shell() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def render_analytics_header(title: str, subtitle: Optional[str] = None) -> None:
    sub = f'<p class="ns-analytics-sub">{html.escape(subtitle)}</p>' if subtitle else ""
    st.markdown(
        f"""
<div class="ns-analytics-header">
  <h1 class="ns-analytics-title">{html.escape(title)}</h1>
  {sub}
  <div class="ns-analytics-rule" aria-hidden="true"></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_analytics_kpis(metrics: List[Dict[str, Any]]) -> None:
    cells = []
    for i, m in enumerate(metrics):
        label = html.escape(str(m.get("label", "")))
        value = html.escape(str(m.get("value", "")))
        hint = m.get("hint")
        hint_html = (
            f'<span class="ns-analytics-kpi-hint">{html.escape(str(hint))}</span>' if hint else ""
        )
        delay = 0.06 + i * 0.07
        cells.append(
            f"""
<div class="ns-analytics-kpi" style="animation-delay: {delay}s">
  <div class="ns-analytics-kpi-value">{value}</div>
  <div class="ns-analytics-kpi-label">{label}</div>
  {hint_html}
</div>
"""
        )
    st.markdown(f'<div class="ns-analytics-kpi-row">{"".join(cells)}</div>', unsafe_allow_html=True)
