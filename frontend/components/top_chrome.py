"""Top-right search and help."""

import streamlit as st

_CHROME_CSS = """
<style>
    .ns-topbar-row {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 0.45rem;
        margin-bottom: 0.75rem;
    }
    .ns-topbar-row input {
        height: 2rem !important;
        min-height: 2rem !important;
        font-size: 0.82rem !important;
    }
    .ns-help-btn .stButton > button {
        width: 2rem !important;
        min-width: 2rem !important;
        height: 2rem !important;
        padding: 0 !important;
    }
    /* .ns-search-hint colors live in enterprise_theme.py (dark vs light) */
</style>
"""


@st.dialog("Help")
def _help_dialog() -> None:
    st.markdown(
        "Use the sidebar: **Ingest hub** → **Search** → **Governed Ask** → **Lineage**. "
        "Details in **Settings → About**."
    )
    if st.button("Open Settings → About", type="primary", use_container_width=True):
        st.session_state["ns_open_settings_about"] = True
        st.switch_page("views/9_Settings.py")


def render_top_right_tools() -> None:
    st.markdown(_CHROME_CSS, unsafe_allow_html=True)

    _left, right = st.columns([5.2, 2.8])
    with right:
        st.markdown('<div class="ns-topbar-row">', unsafe_allow_html=True)
        search_col, help_col = st.columns([5.5, 0.5], gap="small")

        with search_col:
            st.markdown('<div class="ns-search-block">', unsafe_allow_html=True)
            with st.form("top_search", clear_on_submit=False, border=False):
                q = st.text_input(
                    "Search",
                    placeholder="Search corpus…",
                    label_visibility="collapsed",
                )
                submitted = st.form_submit_button("send")
                if submitted and q and q.strip():
                    st.session_state["pending_search_query"] = q.strip()
                    st.switch_page("views/2_Search.py")
            st.markdown(
                '<div class="ns-search-hint">Press Enter to submit the form</div>',
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with help_col:
            st.markdown('<div class="ns-help-btn">', unsafe_allow_html=True)
            if st.button("?", key="top_help_btn", help="Help"):
                _help_dialog()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
