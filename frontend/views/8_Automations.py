"""Automations — scheduled agents, ingest watcher, reports."""

import streamlit as st

from frontend.api_client import (
    agents_inbox,
    agents_registry,
    get_automation_schedule,
    list_agent_runs,
    run_automations,
    save_automation_schedule,
)
from frontend.components.fluent_ui import render_page_header
from frontend.components.motion_ui import page_shell_close, page_shell_open, render_run_history_list

_AGENT_OPTIONS = [
    "corpus_steward",
    "new_hire_autopilot",
    "search_quality",
    "ingest_watcher",
    "review_triage",
]

page_shell_open("ns-automations-page")
render_page_header(
    "Automations",
    "Background agents for corpus health, onboarding, search, folder ingest, and review triage.",
)

tab_run, tab_schedule, tab_inbox, tab_runs, tab_registry = st.tabs(
    ["Run now", "Schedule", "Inbox", "Run history", "Agent registry"]
)

with tab_run:
    st.markdown("Leave agents **empty** to run all five, or pick specific jobs.")
    agents_pick = st.multiselect("Agents", _AGENT_OPTIONS, default=[])
    st.caption(
        "**ingest_watcher** needs `KNOWLEDGEPILOT_WATCH_ENABLED=true` and `KNOWLEDGEPILOT_WATCH_FOLDER` in `.env`."
    )
    if st.button("Run automations", type="primary", key="auto_run_btn"):
        try:
            result = run_automations(agents_pick or None)
            st.success(f"Batch **{result.get('batch_id', '')}** finished.")
            for run in result.get("runs") or []:
                icon = "✅" if run.get("status") == "completed" else "⚠️"
                st.write(f"{icon} **{run.get('agent')}** — {run.get('message')}")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))

with tab_schedule:
    st.markdown('<div class="ns-schedule-block">', unsafe_allow_html=True)
    st.markdown('<div class="ns-analytics-rule" aria-hidden="true"></div>', unsafe_allow_html=True)
    st.markdown("Runs while the **API is up** (no separate cron script required).")
    try:
        sched = get_automation_schedule()
    except Exception as exc:
        st.error(str(exc))
        sched = {}

    enabled = st.checkbox("Enable schedule", value=bool(sched.get("enabled")))
    day_pattern = st.selectbox(
        "Day",
        options=["monday", "weekdays", "daily"],
        format_func=lambda x: {
            "monday": "Every Monday",
            "weekdays": "Monday–Friday",
            "daily": "Every day",
        }[x],
        index=["monday", "weekdays", "daily"].index(sched.get("day_pattern", "monday")),
    )
    tz_options = ["UTC", "Asia/Kolkata", "America/Chicago", "America/New_York", "Europe/London"]
    tz_default = sched.get("timezone", "UTC")
    timezone = st.selectbox(
        "Timezone",
        tz_options,
        index=tz_options.index(tz_default) if tz_default in tz_options else 0,
    )
    tcol1, tcol2 = st.columns(2)
    with tcol1:
        hour = st.number_input("Hour (local)", 0, 23, int(sched.get("hour", 8)))
    with tcol2:
        minute = st.number_input("Minute", 0, 59, int(sched.get("minute", 0)))
    sched_agents = st.multiselect(
        "Agents to run",
        _AGENT_OPTIONS,
        default=sched.get("agents") or _AGENT_OPTIONS,
    )
    if sched.get("last_run_at"):
        st.caption(f"Last scheduled run: {sched['last_run_at']}")

    if st.button("Save schedule", type="primary", key="save_sched"):
        try:
            save_automation_schedule(
                enabled=enabled,
                day_pattern=day_pattern,
                hour=int(hour),
                minute=int(minute),
                agents=sched_agents or _AGENT_OPTIONS,
                timezone=timezone,
            )
            st.success("Schedule saved. API will run this batch on the next matching time.")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))
    st.markdown("</div>", unsafe_allow_html=True)

with tab_inbox:
    try:
        inbox = agents_inbox()
        items = inbox.get("items") or []
        if not items:
            st.caption("No automation runs yet — use **Run now** or enable **Schedule**.")
        for item in items:
            with st.container(border=True):
                st.markdown(f"**{item.get('agent_name')}** · `{item.get('execution_id')}`")
                st.caption(item.get("summary") or "")
                if item.get("report_path"):
                    st.code(item["report_path"])
    except Exception as exc:
        st.error(str(exc))

with tab_runs:
    try:
        runs = list_agent_runs()
        render_run_history_list(runs or [])
    except Exception as exc:
        st.error(str(exc))

with tab_registry:
    try:
        reg = agents_registry()
        st.dataframe(
            [
                {
                    "name": a.get("name"),
                    "kind": a.get("kind"),
                    "enabled": a.get("enabled"),
                    "description": a.get("description"),
                }
                for a in reg
            ],
            hide_index=True,
            use_container_width=True,
        )
    except Exception as exc:
        st.error(str(exc))

page_shell_close()
