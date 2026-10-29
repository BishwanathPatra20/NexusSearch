import streamlit as st

from frontend.api_client import get_chunks, list_documents, patch_document
from frontend.confluence_url_util import parse_page_id
from frontend.components.knowledge_path_viz import render_knowledge_path
from frontend.knowledge_path_util import build_knowledge_path

from frontend.components.fluent_ui import render_page_header
from frontend.components.motion_ui import page_shell_close, page_shell_open

page_shell_open("ns-docviewer-page")
render_page_header("Document viewer", "Lifecycle, relationships, and full text for each indexed file.")

source_filter = st.selectbox(
    "Source",
    [
        ("all", "All sources"),
        ("confluence", "Confluence (live sync)"),
        ("upload", "Uploaded files"),
        ("folder", "Folder ingest"),
        ("onboarding", "Onboarding corpus"),
    ],
    format_func=lambda x: x[1],
    index=0,
)
try:
    docs = list_documents(
        source_type=None if source_filter[0] == "all" else source_filter[0],
    )
except Exception as exc:
    st.error(f"Could not load documents: {exc}")
    st.stop()

if not docs:
    st.info("No documents for this filter. Use **Ingest hub** to add content.")
    st.stop()

options = {f"{d['title']} ({d['file_name']})": d["id"] for d in docs}
keys = list(options.keys())
default_index = 0
pending = st.session_state.pop("pending_document_id", None)
if pending is not None:
    for i, k in enumerate(keys):
        if options[k] == pending:
            default_index = i
            break
choice = st.selectbox("Select document", keys, index=default_index)
doc_id = options[choice]
doc = next(d for d in docs if d["id"] == doc_id)

uploaded = doc.get("upload_date", "")
st.markdown(
    f"**Status:** {doc.get('status', 'active')} · **Version:** {doc.get('version_label') or '—'} · "
    f"**Source:** {doc.get('source_type', 'upload')} · **Last indexed:** {uploaded}"
)
st.markdown(f"**Tags:** {', '.join(doc.get('tags') or []) or '—'}")
page_id = parse_page_id(doc.get("source_uri")) or parse_page_id(doc.get("source_link"))
if page_id:
    st.caption(f"Confluence pageId **{page_id}**")
if doc.get("source_link"):
    label = "Open in Confluence" if doc.get("source_type") == "confluence" else "Original source"
    st.markdown(f"**{label}:** [{doc['source_link']}]({doc['source_link']})")

render_knowledge_path(doc.get("knowledge_path") or build_knowledge_path(
    source_type=doc.get("source_type", "upload"),
    source_uri=doc.get("source_uri"),
    file_name=doc["file_name"],
    document_id=doc["id"],
))
with st.expander("Edit lifecycle & relationships"):
    new_status = st.selectbox(
        "Status",
        ["active", "deprecated", "archived", "draft"],
        index=["active", "deprecated", "archived", "draft"].index(doc.get("status", "active")),
    )
    version_label = st.text_input("Version label", doc.get("version_label") or "")
    related_raw = st.text_input(
        "Related document IDs (comma-separated)",
        ",".join(str(x) for x in doc.get("related_document_ids") or []),
    )
    if st.button("Save metadata"):
        related_ids = [int(x.strip()) for x in related_raw.split(",") if x.strip().isdigit()]
        try:
            updated = patch_document(
                doc_id,
                {
                    "status": new_status,
                    "version_label": version_label or None,
                    "related_document_ids": related_ids,
                },
            )
            st.success("Updated.")
            st.json(updated)
        except Exception as exc:
            st.error(str(exc))

try:
    chunks = get_chunks(doc_id)
except Exception as exc:
    st.error(str(exc))
    st.stop()

st.markdown(f"**Chunks:** {len(chunks)} · **Views:** {doc['view_count']}")
if doc.get("duplicate_of_ids"):
    st.warning(f"Potential duplicate of: {doc['duplicate_of_ids']}")

for ch in chunks:
    label = f"Page {ch['page_number']} · chunk {ch['chunk_index']} (id {ch['id']})"
    with st.expander(label):
        render_knowledge_path(
            build_knowledge_path(
                source_type=doc.get("source_type", "upload"),
                source_uri=doc.get("source_uri"),
                file_name=doc["file_name"],
                document_id=doc["id"],
                page_number=ch["page_number"],
                chunk_index=ch["chunk_index"],
                chunk_id=ch["id"],
                section=ch.get("section"),
            ),
            title="Chunk location",
            compact=True,
        )
        if ch.get("section"):
            st.caption(ch["section"])
        st.text(ch["content"][:8000])

page_shell_close()
