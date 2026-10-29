"""New hire guide — KT spreadsheet (access, Confluence, tickets, day plan)."""

from typing import Optional

import streamlit as st

from backend.app.onboarding_days import item_sort_key, sort_day_labels, title_redundant_with_day
from frontend.api_client import (
    confluence_status,
    confluence_sync_page,
    get_onboarding_items,
    get_onboarding_meta,
    import_onboarding_file,
    import_onboarding_default,
    onboarding_link_health,
    onboarding_sync_confluence,
)
from frontend.confluence_url_util import parse_page_id

from frontend.components.fluent_ui import render_page_header
from frontend.components.motion_ui import page_shell_close, page_shell_open

page_shell_open("ns-onboarding-page")
render_page_header(
    "New hire guide",
    "10-day KT: Confluence pages, global groups, access requests, and documents from your Excel workbook.",
)

try:
    meta = get_onboarding_meta()
except Exception as exc:
    st.error(f"Cannot load onboarding data: {exc}")
    st.stop()

with st.expander("Import / refresh workbook", expanded=meta.get("total", 0) == 0):
    st.markdown(
        """
1. Download **`Personalization_KT_Onboarding_10Day.xlsx`** from SharePoint (or use your latest copy).  
2. Either **upload below**, or save the file as:
   `config/onboarding/Personalization_KT_Onboarding_10Day.xlsx` and click **Import from default path**.  
3. Restart is not required — import rebuilds the guide and **Search** corpus automatically.
        """
    )
    uploaded = st.file_uploader("Upload Excel (.xlsx)", type=["xlsx", "xlsm"])
    col_a, col_b = st.columns(2)
    with col_a:
        if uploaded and st.button("Import uploaded file", type="primary"):
            try:
                result = import_onboarding_file(uploaded.name, uploaded.getvalue())
                st.success(result.get("message", "Imported."))
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
    with col_b:
        if st.button("Import from default path"):
            try:
                result = import_onboarding_default()
                st.success(result.get("message", "Imported."))
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

if meta.get("total", 0) == 0:
    st.info(
        "No onboarding rows yet. Upload your KT spreadsheet above so new teammates can "
        "find Confluence links, global groups, and how to raise access tickets."
    )
    st.stop()

if meta.get("source_file"):
    st.caption(
        f"Source: **{meta['source_file']}** · {meta['total']} items"
        + (f" · last import {meta.get('last_import_at', '')}" if meta.get("last_import_at") else "")
    )

with st.expander("Confluence sync from guide", expanded=False):
    st.caption("Bulk-sync every parseable Confluence URL in the workbook into Search.")
    col_sync, col_health = st.columns(2)
    with col_sync:
        if st.button("Sync all guide Confluence pages", type="primary", key="onb_bulk_sync"):
            try:
                if not confluence_status().get("reachable"):
                    st.error("Confluence not connected — check Ingest hub and `.env`.")
                else:
                    result = onboarding_sync_confluence()
                    st.success(result.get("message", "Done."))
                    if result.get("errors"):
                        with st.expander("Sync errors"):
                            for err in result["errors"]:
                                st.write(err)
            except Exception as exc:
                st.error(str(exc))
    with col_health:
        if st.button("Check Confluence link health", key="onb_link_health"):
            try:
                health = onboarding_link_health()
                st.caption(
                    f"**{health.get('parseable', 0)}** / **{health.get('total_with_url', 0)}** "
                    "URLs have a parseable page ID."
                )
                bad = [i for i in (health.get("items") or []) if i.get("issue")]
                if bad:
                    st.dataframe(
                        [
                            {
                                "title": i.get("title"),
                                "url": i.get("confluence_url"),
                                "issue": i.get("issue"),
                            }
                            for i in bad
                        ],
                        hide_index=True,
                        use_container_width=True,
                    )
            except Exception as exc:
                st.error(str(exc))

search_q = st.text_input("Filter this guide", placeholder="e.g. Databricks, global group, Confluence")

tab_timeline, tab_access, tab_wiki, tab_tickets, tab_all = st.tabs(
    ["By day", "Access & groups", "Confluence", "Tickets", "All items"]
)

_CATEGORY_ICONS = {
    "access": "🔐",
    "confluence": "📘",
    "ticket": "🎫",
    "document": "📄",
    "general": "📌",
}


def _load(category: Optional[str] = None) -> dict:
    data = get_onboarding_items(q=search_q or None, category=category)
    items = data.get("items") or []
    items = sorted(
        items,
        key=lambda i: item_sort_key(
            i.get("day_label"),
            i.get("title", ""),
            i.get("sheet_name", ""),
            int(i.get("row_index") or 0),
        ),
    )
    data["items"] = items
    return data


def _render_card(
    item: dict,
    show_day_in_header: bool = True,
    *,
    key_prefix: str,
) -> None:
    icon = _CATEGORY_ICONS.get(item.get("category", ""), "📌")
    day = item.get("day_label")
    header = f"{icon} {item['title']}"
    if show_day_in_header and day and not title_redundant_with_day(item["title"], day):
        header += f" · {day}"
    with st.container(border=True):
        st.markdown(f"**{header}**")
        if item.get("owner"):
            st.caption(f"POC: {item['owner']}")
        if item.get("access_group"):
            st.markdown(f"**Global group / access:** `{item['access_group']}`")
        if item.get("description"):
            st.write(item["description"])
        links = []
        if item.get("confluence_url"):
            links.append(f"[Open Confluence]({item['confluence_url']})")
        if item.get("ticket_url"):
            links.append(f"[Raise / track request]({item['ticket_url']})")
        if links:
            st.markdown(" · ".join(links))

        page_id = parse_page_id(item.get("confluence_url"))
        c1, c2, c3 = st.columns(3)
        with c1:
            if page_id and st.button(
                "Sync wiki page",
                key=f"sync_{key_prefix}_{item['id']}_{page_id}",
            ):
                try:
                    if not confluence_status().get("reachable"):
                        st.error("Confluence not connected — check Ingest hub.")
                    else:
                        result = confluence_sync_page(page_id, tags=["confluence", "onboarding"])
                        st.success(result.get("message", "Synced."))
                except Exception as exc:
                    st.error(str(exc))
        with c2:
            if st.button("Search this topic", key=f"search_{key_prefix}_{item['id']}"):
                st.session_state["pending_search_query"] = item["title"]
                st.switch_page("views/2_Search.py")
        with c3:
            if item.get("access_group") and st.button(
                "Ask about access",
                key=f"ask_{key_prefix}_{item['id']}",
            ):
                st.session_state["pending_ask_question"] = (
                    f"How do I get access to {item['access_group']}?"
                )
                st.switch_page("views/5_Governed_Ask.py")


with tab_timeline:
    data = _load()
    days = data.get("days") or []
    if not days:
        for item in data.get("items", []):
            _render_card(item, key_prefix="byday")
    else:
        for day in sort_day_labels(days):
            st.subheader(day)
            day_data = get_onboarding_items(q=search_q or None, day=day)
            for item in day_data.get("items", []):
                _render_card(
                    item,
                    show_day_in_header=False,
                    key_prefix=f"byday_{day}",
                )

with tab_access:
    data = _load(category="access")
    if not data.get("items"):
        st.caption("No rows tagged as access — check column headers or use **All items**.")
    for item in data.get("items", []):
        _render_card(item, key_prefix="access")

with tab_wiki:
    data = _load(category="confluence")
    for item in data.get("items", []):
        _render_card(item, key_prefix="wiki")

with tab_tickets:
    data = _load(category="ticket")
    for item in data.get("items", []):
        _render_card(item, key_prefix="tickets")

with tab_all:
    data = _load()
    for item in data.get("items", []):
        _render_card(item, key_prefix="all")

st.divider()
st.markdown(
    "Tip: use **Search** for free-text lookup across the imported guide "
    "(try *onboarding*, a tool name, or a group name)."
)
page_shell_close()
