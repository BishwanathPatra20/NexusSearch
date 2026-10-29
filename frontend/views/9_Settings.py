"""Platform status and about — single Settings page."""

import streamlit as st

from frontend.api_client import config_status
from frontend.components.about_content import render_about_section
from frontend.components.motion_ui import page_shell_close, page_shell_open, render_calm_header

page_shell_open("ns-settings-page")
render_calm_header(
    "Settings",
    "Platform status and about NexusSearch.",
)

if st.session_state.pop("ns_open_settings_about", False):
    st.caption("Select the **About** tab below.")

tab_status, tab_about = st.tabs(["Status & config", "About"])

with tab_status:
    try:
        st.json(config_status())
    except Exception as exc:
        st.error(str(exc))
    st.markdown(
        """
**Common `.env` keys**

- `KNOWLEDGEPILOT_CONFLUENCE_*` — live Confluence sync  
- `KNOWLEDGEPILOT_WATCH_ENABLED` + `KNOWLEDGEPILOT_WATCH_FOLDERS` — ingest watcher  
- `KNOWLEDGEPILOT_NOTIFY_WEBHOOK_URL` — optional webhook + `data/notifications.log`  
- `KNOWLEDGEPILOT_API_KEY` — optional Bearer for automations  
"""
    )

with tab_about:
    render_about_section()

page_shell_close()
