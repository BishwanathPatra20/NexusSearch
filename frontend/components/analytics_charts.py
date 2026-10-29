"""Charts and CSV export for Analytics page (v1.1)."""

from __future__ import annotations

import csv
import io
from typing import Any, Dict

import pandas as pd
import streamlit as st


def render_search_charts(data: Dict[str, Any]) -> None:
    st.markdown('<div class="ns-analytics-panel ns-analytics-panel--charts">', unsafe_allow_html=True)
    volume = data.get("search_volume_by_day") or []
    if volume:
        df_vol = pd.DataFrame(volume)
        df_vol = df_vol.rename(
            columns={"day": "Day", "searches": "Searches", "zero_results": "Zero results"}
        )
        st.subheader("Search activity (last 30 days)")
        st.line_chart(df_vol.set_index("Day")[["Searches", "Zero results"]], use_container_width=True)
    else:
        st.caption("Search volume chart appears after users run searches.")

    top = data.get("top_searches") or []
    if top:
        st.subheader("Top queries")
        df_top = pd.DataFrame(top).rename(columns={"query": "Query", "count": "Count"})
        st.bar_chart(df_top.set_index("Query")["Count"], use_container_width=True)

    zero = data.get("zero_result_searches") or []
    if zero:
        st.subheader("Zero-result queries")
        df_zero = pd.DataFrame(zero).rename(columns={"query": "Query", "count": "Count"})
        st.bar_chart(df_zero.set_index("Query")["Count"], use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def build_analytics_csv(data: Dict[str, Any], gov: Dict[str, Any] | None = None) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["NexusSearch governance report"])
    writer.writerow(["total_searches", data.get("total_searches", 0)])
    cf = data.get("confluence") or {}
    writer.writerow(["confluence_pages_indexed", cf.get("pages_indexed", 0)])
    writer.writerow([])
    writer.writerow(["top_searches", "count"])
    for row in data.get("top_searches") or []:
        writer.writerow([row.get("query"), row.get("count")])
    writer.writerow([])
    writer.writerow(["zero_result_searches", "count"])
    for row in data.get("zero_result_searches") or []:
        writer.writerow([row.get("query"), row.get("count")])
    writer.writerow([])
    writer.writerow(["search_volume_day", "searches", "zero_results"])
    for row in data.get("search_volume_by_day") or []:
        writer.writerow([row.get("day"), row.get("searches"), row.get("zero_results")])
    if gov:
        rq = gov.get("review_quality") or {}
        writer.writerow([])
        writer.writerow(["governance_questions_asked", rq.get("questions_asked")])
        writer.writerow(["governance_approval_rate_pct", rq.get("approval_rate_pct")])
    return buf.getvalue()


def render_export_button(data: Dict[str, Any], gov: Dict[str, Any] | None = None) -> None:
    csv_text = build_analytics_csv(data, gov)
    st.download_button(
        "Download governance report (CSV)",
        data=csv_text,
        file_name="nexussearch_governance_report.csv",
        mime="text/csv",
        key="analytics_export_csv",
    )
