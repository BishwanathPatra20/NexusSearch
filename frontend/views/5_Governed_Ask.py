import streamlit as st

from frontend.api_client import (
    approve_review,
    ask,
    edit_review,
    get_onboarding_suggested_asks,
    list_approved_knowledge,
    list_reviews,
    reject_review,
    review_audit,
    review_triage,
    triage_batch_approve,
)
from frontend.components.fluent_ui import render_page_header
from frontend.components.motion_ui import (
    page_shell_close,
    page_shell_open,
    render_governed_step_strip,
    review_row_close,
    review_row_open,
)

page_shell_open("ns-governed-page")
render_page_header(
    "Governed Ask",
    "Plan → search → extractive draft → validate → human review → approved knowledge.",
)

tab_ask, tab_queue, tab_approved = st.tabs(["Ask", "Review queue", "Approved knowledge"])

with tab_ask:
    render_governed_step_strip(1 if st.session_state.get("last_ask") else 0)
    prefill = st.session_state.pop("pending_ask_question", "")
    question = st.text_area(
        "Question",
        value=prefill,
        placeholder="How do I get Databricks access?",
    )
    try:
        suggestions = get_onboarding_suggested_asks(limit=8).get("items") or []
    except Exception:
        suggestions = []
    if suggestions:
        st.caption("Suggested from your KT guide (click to fill):")
        cols = st.columns(min(4, len(suggestions)))
        for i, item in enumerate(suggestions[:8]):
            with cols[i % len(cols)]:
                if st.button(item["question"][:48] + ("…" if len(item["question"]) > 48 else ""), key=f"sug_{i}"):
                    st.session_state["pending_ask_question"] = item["question"]
                    st.rerun()
    if st.button("Generate draft answer", type="primary") and question.strip():
        try:
            result = ask(question.strip(), submit_for_review=True)
            st.session_state["last_ask"] = result
            st.success(
                f"Review item **#{result['review_item_id']}** created ({result['status']}). "
                f"Open **Lineage** page to trace end-to-end."
            )
        except Exception as exc:
            st.error(str(exc))

    result = st.session_state.get("last_ask")
    if result:
        plan = result.get("plan") or {}
        structured = plan.get("structured") or {}
        if structured:
            st.caption(
                f"Planner: intent **{structured.get('intent')}** · action **{structured.get('action')}** · "
                f"review required **{structured.get('requires_review')}**"
            )
        st.metric("Confidence", f"{result['confidence_score']}%")
        if result.get("validator_notes"):
            st.caption("Validator: " + " · ".join(result["validator_notes"]))
        st.text_area("Draft answer", result["draft_answer"], height=220)
        st.markdown("**Sources**")
        for src in result.get("sources") or []:
            st.markdown(
                f"- `{src.get('file_name')}` p.{src.get('page_number')} · "
                f"chunk {src['chunk_id']} · score {src['relevance_score']}"
            )

with tab_queue:
    render_governed_step_strip(2)
    status_filter = st.selectbox("Status", ["pending", "approved", "rejected", "edited", "all"])
    if status_filter == "pending":
        try:
            triage = review_triage()
            if triage.get("total_pending", 0) > 0:
                st.markdown("**Triage batches** — similar questions grouped (highest confidence first).")
                bcol1, bcol2 = st.columns(2)
                with bcol1:
                    min_sc = st.number_input("Batch approve min %", 50, 100, 85, key="triage_min_sc")
                with bcol2:
                    max_n = st.number_input("Max approvals", 1, 20, 5, key="triage_max_n")
                if st.button("Batch approve high-confidence in triage", key="triage_batch_btn"):
                    try:
                        res = triage_batch_approve(float(min_sc), int(max_n))
                        st.success(f"Approved: {res.get('approved_ids', [])}")
                        if res.get("skipped"):
                            st.caption("Skipped: " + "; ".join(res["skipped"][:8]))
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
                for batch in triage.get("batches") or []:
                    with st.expander(f"{batch.get('label')} ({batch.get('count')})"):
                        for row in batch.get("items") or []:
                            st.caption(
                                f"#{row.get('review_id')} · {row.get('confidence_score')}% · "
                                f"{row.get('query', '')[:72]}"
                            )
        except Exception:
            pass

    try:
        items = list_reviews(None if status_filter == "all" else status_filter)
    except Exception as exc:
        st.error(str(exc))
        items = []

    if not items:
        st.info("No review items in this queue.")
    for idx, item in enumerate(items):
        review_row_open(item.get("status", "pending"), idx)
        with st.container(border=True):
            st.markdown(f"**#{item['id']}** · `{item['query']}` · **{item['status']}** · {item['confidence_score']}%")
            st.text(item["draft_answer"][:500] + ("…" if len(item["draft_answer"]) > 500 else ""))
            edited = st.text_area(
                "Edit before approve",
                value=item.get("final_answer") or item["draft_answer"],
                key=f"edit_{item['id']}",
                height=160,
            )
            comment = st.text_input("Reviewer comment", key=f"comment_{item['id']}")
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("Approve", key=f"ap_{item['id']}"):
                    try:
                        approve_review(item["id"], comment=comment or None)
                        st.toast("Approved")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
            with c2:
                if st.button("Edit & approve", key=f"ed_{item['id']}"):
                    try:
                        edit_review(item["id"], edited, comment=comment or None)
                        st.toast("Edited and approved")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
            with c3:
                if st.button("Reject", key=f"rj_{item['id']}"):
                    try:
                        reject_review(item["id"], comment=comment or None)
                        st.toast("Rejected")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
            with st.expander("Audit trail"):
                try:
                    st.json(review_audit(item["id"]))
                except Exception as exc:
                    st.caption(str(exc))
        review_row_close()

with tab_approved:
    try:
        approved = list_approved_knowledge()
    except Exception as exc:
        st.error(str(exc))
        approved = []
    for row in approved:
        with st.container(border=True):
            st.markdown(f"**{row['query']}** · reviewer `{row['reviewer']}`")
            st.write(row["approved_answer"])

page_shell_close()
