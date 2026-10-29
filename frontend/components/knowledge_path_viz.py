"""Knowledge location trail — plain language for business users."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import streamlit as st

from frontend.knowledge_path_util import nodes_for_display, path_summary_sentence

_KIND_STYLE = {
    "root": ("#1e3a5f", "#e0f2fe"),
    "repository": ("#334155", "#f1f5f9"),
    "source": ("#0f766e", "#ecfdf5"),
    "folder": ("#64748b", "#f8fafc"),
    "ellipsis": ("#94a3b8", "#f8fafc"),
    "file": ("#1d4ed8", "#eff6ff"),
    "page": ("#0369a1", "#f0f9ff"),
    "section": ("#6d28d9", "#f5f3ff"),
    "chunk": ("#c2410c", "#fff7ed"),
}


def _node_html(node: Dict[str, Any]) -> str:
    kind = node.get("kind", "folder")
    fg, bg = _KIND_STYLE.get(kind, ("#475569", "#f8fafc"))
    active = node.get("active", False)
    border = "2px solid #ea580c" if active else "1px solid rgba(15,23,42,0.1)"
    weight = "700" if active else "500"
    icon = node.get("icon", "")
    label = node.get("label", "")
    display = f"{icon} {label}".strip() if icon else label
    return (
        f'<div class="kp-node" style="color:{fg};background:{bg};border:{border};'
        f'font-weight:{weight};" title="{kind}">{display}</div>'
    )


def render_knowledge_path(
    nodes: Optional[List[Dict[str, Any]]],
    *,
    title: str = "Where this answer comes from",
    compact: bool = False,
) -> None:
    if not nodes:
        return

    display = nodes_for_display(nodes)
    st.markdown(f'<div class="kp-title">{title}</div>', unsafe_allow_html=True)
    st.caption(path_summary_sentence(nodes))

    parts = []
    for i, node in enumerate(display):
        parts.append(_node_html(node))
        if i < len(display) - 1:
            parts.append('<div class="kp-edge" aria-hidden="true"></div>')

    height = "56px" if compact else "62px"
    if compact:
        wrap_bg = "rgba(15, 23, 42, 0.55)"
        wrap_border = "rgba(255, 255, 255, 0.08)"
        title_color = "#9ca3af"
    else:
        wrap_bg = "linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%)"
        wrap_border = "rgba(0,0,0,0.06)"
        title_color = "#334155"
    html = f"""
    <style>
    .kp-wrap {{
        margin: 0.35rem 0 0.75rem 0;
        padding: 0.75rem 0.85rem;
        border-radius: 8px;
        background: {wrap_bg};
        border: 1px solid {wrap_border};
        overflow-x: auto;
    }}
    .kp-title {{
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        color: {title_color};
        margin-bottom: 0.25rem;
    }}
    .kp-track {{
        display: flex;
        align-items: center;
        gap: 0;
        min-height: {height};
        flex-wrap: nowrap;
    }}
    .kp-node {{
        flex: 0 0 auto;
        font-size: 0.82rem;
        line-height: 1.25;
        padding: 0.45rem 0.65rem;
        border-radius: 10px;
        white-space: nowrap;
        font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
    }}
    .kp-edge {{
        flex: 0 0 22px;
        height: 2px;
        margin: 0 3px;
        background: linear-gradient(90deg, #cbd5e1 0%, #64748b 50%, #cbd5e1 100%);
        position: relative;
    }}
    .kp-edge::after {{
        content: "";
        position: absolute;
        right: -1px;
        top: -3px;
        border: 4px solid transparent;
        border-left-color: #64748b;
    }}
    </style>
    <div class="kp-wrap kp-wrap-animate">
      <div class="kp-track">{"".join(parts)}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
