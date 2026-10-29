import streamlit as st

from frontend.api_client import (
    confluence_spaces,
    confluence_stats,
    confluence_status,
    confluence_sync,
    confluence_sync_descendants,
    confluence_sync_job,
    confluence_sync_page,
    confluence_sync_pages,
    confluence_validate_space,
    ingest_folder,
    upload_file,
)
from frontend.components.fluent_ui import render_page_header
from frontend.components.ingest_job_panel import render_job_panel
from frontend.components.motion_ui import page_shell_close, page_shell_open
from frontend.confluence_url_util import parse_page_ids_bulk

page_shell_open("ns-ingest-page")
render_page_header(
    "Ingest hub",
    "Files · folder export · Confluence live sync — one place to grow your governed corpus.",
)

tab_files, tab_folder, tab_confluence = st.tabs(["Files", "Folder ingest", "Confluence"])

with tab_files:
    uploaded = st.file_uploader(
        "Choose a file",
        type=["pdf", "docx", "txt", "md", "markdown", "html", "htm"],
    )
    title = st.text_input("Title (optional)", "", key="upload_title")
    tags_raw = st.text_input("Tags (comma-separated)", "deployment, onboarding", key="upload_tags")

    if uploaded and st.button("Upload and index", type="primary", key="upload_index_btn"):
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        try:
            result = upload_file(
                uploaded.name,
                uploaded.getvalue(),
                title=title or None,
                tags=tags,
            )
            doc = result["document"]
            st.success(f"Indexed **{doc['file_name']}** — {result['chunks_created']} chunks.")
            if doc.get("duplicate_of_ids"):
                st.warning(f"Potential duplicate of document id(s): {doc['duplicate_of_ids']}")
        except Exception as exc:
            st.error(f"Upload failed: {exc}")

with tab_folder:
    st.markdown("Index a **local folder** (e.g. Confluence HTML export). No cloud APIs.")
    folder_path = st.text_input("Absolute folder path", "", key="folder_path")
    folder_tags = st.text_input("Tags for all files", "documentation", key="folder_tags")
    if st.button("Start folder ingest (background job)", key="folder_job"):
        try:
            resp = ingest_folder(folder_path, tags=[t.strip() for t in folder_tags.split(",") if t.strip()])
            st.session_state["last_job_id"] = resp["job_id"]
            st.info(f"Job **{resp['job_id']}** queued.")
        except Exception as exc:
            st.error(str(exc))

with tab_confluence:
    st.markdown(
        "Sync **page IDs**, **bulk lists**, or **child pages** under a parent (e.g. P360 tree). "
        "Re-sync refreshes wiki content in Search."
    )
    try:
        status = confluence_status()
    except Exception as exc:
        st.error(f"Could not reach Confluence API: {exc}")
        st.stop()

    if not status.get("enabled"):
        st.warning("Enable Confluence in `.env` and restart the API. See `docs/CONFLUENCE_PAT.md`.")
        st.stop()

    if status.get("reachable"):
        st.success(
            f"Connected as **{status.get('user_display_name') or 'user'}** · {status.get('base_url')}"
        )
    else:
        st.error(status.get("message", "Not connected"))
        st.stop()

    try:
        stats = confluence_stats()
        st.caption(
            f"**{stats.get('pages_indexed', 0)}** Confluence pages indexed locally"
            + (f" · last sync {stats.get('last_synced_at')}" if stats.get("last_synced_at") else "")
        )
    except Exception:
        pass

    mode = st.radio(
        "Sync mode",
        ["Single page (re-sync)", "Multiple page IDs / URLs", "Parent + children", "Whole space"],
        horizontal=True,
    )
    page_tags = st.text_input("Tags (optional)", "confluence, personalization, p360", key="cf_tags")

    def _tags() -> list:
        return [t.strip() for t in page_tags.split(",") if t.strip()]

    if mode == "Single page (re-sync)":
        page_id = st.text_input("Page ID", value="1512556436", key="cf_single_id")
        if st.button("Sync / refresh this page", type="primary", key="cf_sync_single"):
            try:
                result = confluence_sync_page(page_id, tags=_tags(), replace_existing=True)
                if result.get("indexed"):
                    st.success(result.get("message", "Done."))
                else:
                    st.warning(result.get("message", "Not indexed."))
            except Exception as exc:
                st.error(str(exc))

    elif mode == "Multiple page IDs / URLs":
        bulk = st.text_area(
            "Page IDs or Confluence URLs (one per line or comma-separated)",
            height=120,
            placeholder="1512556436\nhttps://confluence.../pages/viewpage.action?pageId=1261308608",
        )
        if st.button("Sync all listed pages", type="primary", key="cf_sync_bulk"):
            ids = parse_page_ids_bulk(bulk)
            if not ids:
                st.warning("No page IDs found in input.")
            else:
                try:
                    result = confluence_sync_pages(ids, tags=_tags())
                    st.success(f"Indexed **{result['indexed']}** / {result['requested']} pages.")
                    if result.get("errors"):
                        with st.expander("Errors"):
                            for err in result["errors"]:
                                st.write(err)
                except Exception as exc:
                    st.error(str(exc))

    elif mode == "Parent + children":
        parent = st.text_input("Parent page ID", value="1512556436", key="cf_parent")
        max_pages = st.slider("Max pages (parent + descendants)", 5, 150, 40)
        col_now, col_job = st.columns(2)
        with col_now:
            if st.button("Sync now", type="primary", key="cf_sync_desc_now"):
                try:
                    result = confluence_sync_descendants(parent, max_pages=max_pages, tags=_tags())
                    st.success(f"Indexed **{result['indexed']}** / {result['requested']} pages.")
                except Exception as exc:
                    st.error(str(exc))
        with col_job:
            if st.button("Queue background job", key="cf_sync_desc_job"):
                try:
                    resp = confluence_sync_job(parent_page_id=parent, max_pages=max_pages, tags=_tags())
                    st.session_state["last_job_id"] = resp["job_id"]
                    st.info(f"Job **{resp['job_id']}** queued.")
                except Exception as exc:
                    st.error(str(exc))

    else:
        space_key = st.text_input("Space key", value="DEC").strip().upper()
        sync_limit = st.slider("Max pages this run", 5, 150, 50)
        if st.button("Check space key", key="cf_check_space"):
            try:
                info = confluence_validate_space(space_key)
                st.success(f"Found space **{info['name']}** ({info['key']})")
            except Exception as exc:
                st.error(str(exc))
        col_s, col_j = st.columns(2)
        with col_s:
            if st.button("Sync space now", type="primary", key="cf_sync_space_now"):
                try:
                    result = confluence_sync(space_key, limit=sync_limit, tags=_tags())
                    st.success(
                        f"Indexed **{result['pages_indexed']}** / {result['pages_fetched']} pages "
                        f"from **{result['space_key']}**."
                    )
                except Exception as exc:
                    st.error(str(exc))
        with col_j:
            if st.button("Queue DEC-scale background job", key="cf_sync_space_job"):
                try:
                    resp = confluence_sync_job(
                        space_key=space_key,
                        limit=sync_limit,
                        tags=_tags(),
                    )
                    st.session_state["last_job_id"] = resp["job_id"]
                    st.info(f"Job **{resp['job_id']}** queued.")
                except Exception as exc:
                    st.error(str(exc))

    with st.expander("Browse space list (optional)"):
        try:
            spaces = confluence_spaces()
            filter_q = st.text_input("Filter", placeholder="DEC", key="space_filter")
            if filter_q.strip():
                q = filter_q.strip().lower()
                spaces = [
                    s
                    for s in spaces
                    if q in s.get("key", "").lower() or q in (s.get("name") or "").lower()
                ]
            st.caption(f"{len(spaces)} spaces.")
            for s in spaces[:60]:
                st.text(f"{s['name']} ({s['key']})")
        except Exception as exc:
            st.warning(str(exc))

st.divider()
render_job_panel("ingest_global")
page_shell_close()
