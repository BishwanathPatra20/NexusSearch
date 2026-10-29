import streamlit as st

from frontend.api_client import get_lineage, list_lineage_index
from frontend.components.fluent_ui import render_page_header
from frontend.components.lineage_viz import render_lineage_summary_strip, render_lineage_timeline, section

render_page_header(
    "Lineage",
    "Trace questions from planner through review to AK-XXXX and source chunks.",
)

try:
    index = list_lineage_index()
except Exception as exc:
    st.error(f"Could not load lineage index: {exc}")
    st.stop()

if not index:
    st.info("No review items yet. Use **Governed Ask** to create one.")
    st.stop()

labels = {
    f"#{item['review_item_id']} · {item['question'][:60]}… ({item['status']})": item["review_item_id"]
    for item in index
}
choice = st.selectbox("Review item", list(labels.keys()))
review_id = labels[choice]

try:
    data = get_lineage(review_id)
except Exception as exc:
    st.error(str(exc))
    st.stop()

render_lineage_timeline(data.get("timeline"))
render_lineage_summary_strip(data)

col1, col2 = st.columns(2)
with col1:
    section("Question", data["question"])
    plan = data.get("plan") or {}
    structured = plan.get("structured") or {}
    if structured:
        section(
            "Planner",
            f"Intent: **{structured.get('intent')}**\n\n"
            f"Action: **{structured.get('action')}**\n\n"
            f"Requires review: **{structured.get('requires_review')}**",
        )
    section("Draft answer", data["draft_answer"])
with col2:
    val = data["validation"]
    section(
        "Validation",
        f"Supported: **{'Yes' if val['supported'] else 'No'}**\n\n"
        f"Score: **{val['confidence_score']}** (threshold {val['threshold']})\n\n"
        + ("\n".join(f"- {n}" for n in val.get("notes") or []) or "—"),
    )
    rev = data["review"]
    section(
        "Review",
        f"Status: **{rev['status']}**\n\n"
        f"Decision: {rev.get('decision_label') or '—'}\n\n"
        f"Reviewer: {rev.get('last_reviewer') or '—'}",
    )
    ak = data.get("approved_knowledge")
    if ak:
        section(
            "Approved knowledge",
            f"**{data.get('knowledge_id') or ''}**\n\n{ak['approved_answer']}\n\n"
            f"By {ak['reviewer']} at {ak['approved_at']}",
        )

st.markdown("**Sources**")
for src in data.get("sources") or []:
    with st.container(border=True):
        st.markdown(f"**{src.get('document_title')}** · `{src.get('file_name')}`")
        st.caption(
            f"Page {src.get('page_number')} · chunk {src.get('chunk_id')} "
            f"· relevance {src.get('relevance_score')}"
        )
        if src.get("snippet"):
            st.write(src["snippet"])
