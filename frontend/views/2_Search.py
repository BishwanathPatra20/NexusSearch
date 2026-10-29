import streamlit as st

from frontend.api_client import search
from frontend.components.fluent_ui import (
    render_confluence_live_card,
    render_page_header,
    render_search_result_card,
)
from frontend.components.motion_ui import page_shell_close, page_shell_open, render_empty_state, render_search_skeleton

page_shell_open("ns-search-page")
render_page_header(
    "Search",
    "Local corpus plus Confluence wiki lookup by page id or title when not ingested.",
)

with st.expander("Filters", expanded=False):
    f_status = st.selectbox(
        "Status",
        ["Any", "active", "deprecated", "archived", "draft"],
        index=0,
    )
    f_tag = st.text_input("Tag contains", "")
    f_type = st.selectbox("File type", ["Any", "pdf", "docx", "txt", "md", "html"], index=0)
    f_version = st.text_input("Version label (exact)", "")

st.markdown('<div class="ns-search-panel">', unsafe_allow_html=True)
_prefill = st.session_state.pop("pending_search_query", "")
query = st.text_input(
    "Query",
    value=_prefill,
    placeholder="e.g. Digital Marketing Platform, pageId, onboarding",
    label_visibility="visible",
)
st.markdown("</div>", unsafe_allow_html=True)

filter_key = f"{f_status}|{f_tag}|{f_type}|{f_version}"
search_cache_key = f"{query.strip().lower()}|{filter_key}"

if query:
    load_slot = st.empty()
    if st.session_state.get("_search_cache_key") != search_cache_key:
        with load_slot:
            render_search_skeleton()
            st.caption("Confluence wiki lookup can take up to ~15s — wait for results below.")
        try:
            st.session_state["_search_data"] = search(
                query,
                status=None if f_status == "Any" else f_status,
                tag=f_tag or None,
                file_type=None if f_type == "Any" else f_type,
                version_label=f_version or None,
            )
            st.session_state["_search_cache_key"] = search_cache_key
        except Exception as exc:
            load_slot.empty()
            st.error(f"Search failed: {exc}")
            st.stop()
        load_slot.empty()
    data = st.session_state.get("_search_data")
    if not data:
        st.stop()
    try:
        cap = f"**{data['results_count']}** local match(es) for **{data['query']}**"
        live_n = len(data.get("confluence_live") or [])
        if live_n:
            cap += f" · **{live_n}** from Confluence wiki"
        if data.get("synonym_groups"):
            cap += f" · synonyms: {', '.join(data['synonym_groups'])}"
        if data.get("expanded_terms"):
            cap += f" · terms: {', '.join(data['expanded_terms'][:12])}"
        st.markdown(cap)
        if data.get("filters_applied"):
            st.caption(f"Filters: {data['filters_applied']}")

        live = data.get("confluence_live") or []
        if live:
            st.markdown("### Confluence wiki")
            st.caption(
                "Pages from Confluence that are not in the local ingest index yet. "
                "Use **Ingest this page** to add governed citations."
            )
            for j, hit in enumerate(live, start=1):
                render_confluence_live_card(hit, j)
        elif data.get("confluence_live_error"):
            st.warning(f"Confluence live lookup: {data['confluence_live_error']}")

        if data["results_count"] == 0 and not live:
            render_empty_state(
                "No matches yet.",
                hint="Try a Confluence page id / exact title, or restart the API if live lookup never appears.",
            )

        if data["results_count"] > 0:
            st.markdown("### Local indexed corpus")
            for i, hit in enumerate(data["results"], start=1):
                render_search_result_card(
                    hit,
                    index=i,
                    query=data["query"],
                    search_id=data.get("search_id"),
                )
    except Exception as exc:
        st.error(f"Search failed: {exc}")

page_shell_close()
