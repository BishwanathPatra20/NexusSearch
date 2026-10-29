"""Shared minimal UI motion — distinct tiers per page."""

from __future__ import annotations

import html
from typing import Optional, Sequence

import streamlit as st

_RUN_STATUS_CLASS = {
    "completed": ("green", "ns-run-dot--green"),
    "failed": ("red", "ns-run-dot--red"),
    "running": ("yellow", "ns-run-dot--yellow"),
    "processing": ("yellow", "ns-run-dot--yellow"),
}

_REVIEW_STATUS_CLASS = {
    "pending": "ns-review-row--pending",
    "approved": "ns-review-row--approved",
    "rejected": "ns-review-row--rejected",
    "edited": "ns-review-row--edited",
}


def page_shell_open(css_class: str) -> None:
    st.markdown(f'<div class="{html.escape(css_class)}">', unsafe_allow_html=True)


def page_shell_close() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def render_calm_header(title: str, subtitle: Optional[str] = None) -> None:
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


def render_governed_step_strip(active_step: int) -> None:
    """Ask → Validate → Queue. active_step: 0, 1, or 2."""
    steps = [("Ask", "Question"), ("Validate", "Draft & score"), ("Queue", "Human review")]
    active_step = max(0, min(2, active_step))
    pct = (active_step / 2) * 100 if active_step else 8
    nodes = []
    for i, (name, sub) in enumerate(steps):
        state = "done" if i < active_step else ("active" if i == active_step else "todo")
        nodes.append(
            f"""
<div class="ns-gov-step ns-gov-step--{state}" style="animation-delay: {i * 0.06}s">
  <div class="ns-gov-step-dot"></div>
  <div class="ns-gov-step-label">{html.escape(name)}</div>
  <div class="ns-gov-step-sub">{html.escape(sub)}</div>
</div>
"""
        )
    st.markdown(
        f"""
<div class="ns-gov-strip" role="navigation" aria-label="Governed Ask flow">
  <div class="ns-gov-strip-track" style="--ns-gov-progress: {pct}%">
    <div class="ns-gov-strip-fill"></div>
  </div>
  <div class="ns-gov-strip-steps">{"".join(nodes)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def review_row_open(status: str, index: int = 0) -> None:
    css = _REVIEW_STATUS_CLASS.get((status or "pending").lower(), "ns-review-row--pending")
    delay = min(index, 12) * 0.04
    st.markdown(
        f'<div class="ns-review-row {css}" style="animation-delay: {delay}s">',
        unsafe_allow_html=True,
    )


def review_row_close() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def render_run_history_list(runs: Sequence[dict]) -> None:
    if not runs:
        st.caption("No runs logged.")
        return
    rows = []
    for i, r in enumerate(runs):
        status = (r.get("status") or "unknown").lower()
        _, dot_cls = _RUN_STATUS_CLASS.get(status, ("yellow", "ns-run-dot--yellow"))
        delay = min(i, 15) * 0.035
        rows.append(
            f"""
<div class="ns-run-row" style="animation-delay: {delay}s">
  <span class="ns-run-dot {dot_cls}" aria-hidden="true"><span class="ns-run-dot-core"></span></span>
  <div class="ns-run-body">
    <div class="ns-run-title">{html.escape(str(r.get("agent_name") or r.get("agent") or "—"))}</div>
    <div class="ns-run-meta">{html.escape(str(r.get("execution_id") or ""))}</div>
  </div>
  <div class="ns-run-end">
    <span class="ns-run-status">{html.escape(status)}</span>
    <span class="ns-run-time">{html.escape(str(r.get("finished_at") or r.get("finished") or ""))}</span>
  </div>
</div>
"""
        )
    st.markdown(f'<div class="ns-run-list">{"".join(rows)}</div>', unsafe_allow_html=True)


def render_empty_state(message: str, *, hint: Optional[str] = None) -> None:
    hint_html = f'<p class="ns-empty-hint">{html.escape(hint)}</p>' if hint else ""
    st.markdown(
        f"""
<div class="ns-empty-state">
  <p class="ns-empty-msg">{html.escape(message)}</p>
  {hint_html}
</div>
""",
        unsafe_allow_html=True,
    )


def render_search_skeleton() -> None:
    st.markdown(
        """
<div class="ns-search-skeleton" aria-hidden="true">
  <div class="ns-search-skel-line ns-search-skel-line--a"></div>
  <div class="ns-search-skel-line ns-search-skel-line--b"></div>
  <div class="ns-search-skel-block"></div>
  <div class="ns-search-skel-block ns-search-skel-block--short"></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_job_progress_bar(job_status: str, *, label: Optional[str] = None) -> None:
    norm = job_status.lower()
    if norm in ("completed", "done", "success"):
        pct, phase = 100, "done"
    elif norm in ("failed", "error"):
        pct, phase = 100, "failed"
    elif norm in ("processing", "running"):
        pct, phase = 62, "active"
    else:
        pct, phase = 18, "queued"
    lbl = html.escape(label or f"Job {job_status}")
    st.markdown(
        f"""
<div class="ns-job-progress ns-job-progress--{phase}">
  <div class="ns-job-progress-label">{lbl}</div>
  <div class="ns-job-progress-track"><div class="ns-job-progress-fill" style="width: {pct}%"></div></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_ingest_steps(status: str) -> None:
    """Queued → Processing → Done checkmarks."""
    order = ["queued", "processing", "completed"]
    st_l = status.lower()
    active = 0
    if st_l in ("processing", "running"):
        active = 1
    elif st_l in ("completed", "done"):
        active = 2
    elif st_l in ("failed", "error"):
        active = 1
    parts = []
    for i, name in enumerate(["Queued", "Processing", "Done"]):
        state = "done" if i < active else ("active" if i == active else "todo")
        if st_l in ("failed", "error") and i == 1:
            state = "failed"
        mark = "✓" if state == "done" else ("!" if state == "failed" else str(i + 1))
        parts.append(
            f'<div class="ns-ingest-step ns-ingest-step--{state}"><span class="ns-ingest-step-mark">{mark}</span>'
            f'<span>{name}</span></div>'
        )
        if i < 2:
            parts.append('<div class="ns-ingest-step-line"></div>')
    st.markdown(f'<div class="ns-ingest-steps">{"".join(parts)}</div>', unsafe_allow_html=True)
