import pandas as pd
import streamlit as st

from frontend.api_client import (
    analytics_summary,
    approve_synonym_proposal,
    dismiss_synonym_proposal,
    fetch_audit_pack_csv,
    governance_metrics,
    synonym_proposals,
)
from frontend.components.analytics_charts import render_export_button, render_search_charts
from frontend.components.analytics_ui import (
    close_analytics_shell,
    open_analytics_shell,
    render_analytics_header,
    render_analytics_kpis,
)

open_analytics_shell()
render_analytics_header(
    "Analytics",
    "Search quality, governance, and corpus health.",
)

tab_search, tab_governance, tab_health, tab_synonyms = st.tabs(
    ["Search", "Governance", "Corpus health", "Synonyms"]
)

with tab_search:
    try:
        data = analytics_summary()
    except Exception as exc:
        st.error(f"Could not load analytics: {exc}")
        st.stop()

    cf = data.get("confluence") or {}
    render_analytics_kpis(
        [
            {"label": "Total searches", "value": str(data.get("total_searches", 0))},
            {
                "label": "Confluence pages",
                "value": str(cf.get("pages_indexed", 0)),
                "hint": cf.get("last_synced_at") or "Not synced yet",
            },
            {
                "label": "Zero-result queries",
                "value": str(len(data.get("zero_result_searches") or [])),
            },
        ]
    )
    try:
        gov_export = governance_metrics()
    except Exception:
        gov_export = None
    render_export_button(data, gov_export)
    render_search_charts(data)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top searches")
        if data["top_searches"]:
            st.dataframe(pd.DataFrame(data["top_searches"]), hide_index=True, use_container_width=True)
    with col2:
        st.subheader("Zero-result searches")
        if data["zero_result_searches"]:
            st.dataframe(
                pd.DataFrame(data["zero_result_searches"]),
                hide_index=True,
                use_container_width=True,
            )
    st.subheader("Search quality")
    if data.get("search_quality"):
        st.dataframe(pd.DataFrame(data["search_quality"]), hide_index=True, use_container_width=True)
    st.subheader("Top documents (views)")
    if data["top_documents"]:
        st.dataframe(pd.DataFrame(data["top_documents"]), hide_index=True, use_container_width=True)

with tab_governance:
    try:
        audit_csv = fetch_audit_pack_csv()
        st.download_button(
            "Download audit pack (CSV)",
            data=audit_csv,
            file_name="nexussearch_audit_pack.csv",
            mime="text/csv",
            key="audit_pack_dl",
        )
    except Exception as exc:
        st.caption(f"Audit export unavailable: {exc}")
    try:
        gov = governance_metrics()
    except Exception as exc:
        st.error(f"Could not load governance metrics: {exc}")
        st.stop()

    rq = gov["review_quality"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Questions asked", rq["questions_asked"])
    c2.metric("Approval rate", f"{rq['approval_rate_pct']}%")
    c3.metric("Rejection rate", f"{rq['rejection_rate_pct']}%")
    c4.metric("Edit rate", f"{rq['edit_rate_pct']}%")

    st.caption(
        f"Pending {rq['pending']} · Approved {rq['approved']} · "
        f"Edited {rq['edited']} · Rejected {rq['rejected']}"
    )

    vi = gov["validator_insights"]
    st.subheader("Validator insights")
    v1, v2 = st.columns(2)
    v1.metric("Average validation score", f"{vi['average_validation_score']}%")
    v2.metric("Low-confidence drafts (<55%)", vi["low_confidence_drafts"])
    if vi.get("common_validator_notes"):
        st.dataframe(
            pd.DataFrame(vi["common_validator_notes"]),
            hide_index=True,
            use_container_width=True,
        )

    kn = gov["knowledge"]
    st.subheader("Institutional knowledge")
    k1, k2 = st.columns(2)
    k1.metric("Approved knowledge entries", kn["approved_knowledge_entries"])
    k2.metric("Deprecated/archived source citations", kn["deprecated_source_citations"])
    if kn.get("most_trusted_documents"):
        st.markdown("**Most trusted documents** (cited in approved answers)")
        st.dataframe(
            pd.DataFrame(kn["most_trusted_documents"]),
            hide_index=True,
            use_container_width=True,
        )

    st.subheader("Most reviewed topics (Ask pipeline)")
    if gov.get("most_reviewed_topics"):
        st.dataframe(
            pd.DataFrame(gov["most_reviewed_topics"]),
            hide_index=True,
            use_container_width=True,
        )

    g1, g2 = st.columns(2)
    with g1:
        st.subheader("Most successful searches")
        if gov.get("search_success_queries"):
            st.dataframe(
                pd.DataFrame(gov["search_success_queries"]),
                hide_index=True,
                use_container_width=True,
            )
    with g2:
        st.subheader("Zero-result searches")
        if gov.get("zero_result_searches"):
            st.dataframe(
                pd.DataFrame(gov["zero_result_searches"]),
                hide_index=True,
                use_container_width=True,
            )

with tab_health:
    try:
        data = analytics_summary()
    except Exception as exc:
        st.error(str(exc))
        st.stop()
    health = data.get("knowledge_health") or {}
    h1, h2 = st.columns(2)
    with h1:
        st.markdown("**Outdated (deprecated/archived)**")
        st.dataframe(
            pd.DataFrame(health.get("outdated_documents") or []),
            hide_index=True,
            use_container_width=True,
        )
        st.markdown("**Never accessed**")
        st.dataframe(
            pd.DataFrame(health.get("documents_never_accessed") or []),
            hide_index=True,
            use_container_width=True,
        )
    with h2:
        st.markdown("**Missing tags**")
        st.dataframe(
            pd.DataFrame(health.get("documents_without_tags") or []),
            hide_index=True,
            use_container_width=True,
        )
        st.markdown("**Missing version label**")
        st.dataframe(
            pd.DataFrame(health.get("documents_missing_version") or []),
            hide_index=True,
            use_container_width=True,
        )
    st.markdown("**Potential duplicates**")
    dupes = health.get("potential_duplicates") or []
    if dupes:
        st.dataframe(pd.DataFrame(dupes), hide_index=True, use_container_width=True)
    else:
        st.caption("No duplicates detected yet.")

with tab_synonyms:
    st.caption("Run **search_quality** automation to populate proposals from zero-result searches.")
    try:
        props = synonym_proposals().get("items") or []
    except Exception as exc:
        st.error(str(exc))
        props = []
    if not props:
        st.info("No pending synonym proposals.")
    for p in props:
        with st.container(border=True):
            st.markdown(
                f"**{p.get('canonical_key')}** → add `{p.get('suggested_term')}` "
                f"(hits: {p.get('hit_count')}, sample: {p.get('sample_query', '')[:60]})"
            )
            pid = int(p["id"])
            a1, a2 = st.columns(2)
            with a1:
                if st.button("Approve", key=f"syn_ap_{pid}"):
                    try:
                        approve_synonym_proposal(pid)
                        st.toast("Added to synonyms.json")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
            with a2:
                if st.button("Dismiss", key=f"syn_dis_{pid}"):
                    try:
                        dismiss_synonym_proposal(pid)
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))

close_analytics_shell()
