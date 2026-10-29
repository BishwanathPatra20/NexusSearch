"""Shared background job status panel for Ingest hub."""

import httpx
import streamlit as st

from frontend.api_client import get_job, list_jobs
from frontend.components.motion_ui import render_ingest_steps, render_job_progress_bar


def _show_job(job: dict, job_id: int) -> None:
    status = job.get("status", "queued")
    render_ingest_steps(status)
    render_job_progress_bar(
        status,
        label=f"Job #{job_id} · {job.get('job_type', 'ingest')} · {status}",
    )
    if job.get("error_message"):
        st.error(job["error_message"])


def render_job_panel(key_prefix: str = "ingest") -> None:
    st.markdown("**Background jobs**")
    st.caption("Queue a job from **Folder ingest** or **Confluence** — the id appears in the success message.")

    recent: list = []
    try:
        recent = list_jobs(limit=15)
    except Exception:
        recent = []

    last_id = st.session_state.get("last_job_id")
    default_id = int(last_id) if last_id else None

    if recent:
        labels = {
            f"#{j['id']} · {j.get('job_type', '?')} · {j.get('status', '?')}": int(j["id"])
            for j in recent
        }
        pick = st.selectbox(
            "Recent jobs",
            list(labels.keys()),
            index=0
            if default_id is None
            else next(
                (i for i, k in enumerate(labels) if labels[k] == default_id),
                0,
            ),
            key=f"{key_prefix}_recent_pick",
        )
        job_id = labels[pick]
    else:
        job_id = st.number_input(
            "Job id",
            min_value=1,
            value=int(default_id or 1),
            key=f"{key_prefix}_job_id",
            help="No jobs in the database yet — start a background ingest first.",
        )
        if not recent and not last_id:
            st.caption("No ingestion jobs yet. Job **#1** only exists after you queue a run.")

    refresh = st.button("Refresh job status", key=f"{key_prefix}_refresh_job")
    auto = last_id is not None and int(last_id) == int(job_id)

    if not (refresh or auto):
        return

    try:
        job = get_job(int(job_id))
        _show_job(job, int(job_id))
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            st.info(
                f"No job **#{job_id}** in the database. "
                "Queue **folder** or **Confluence** background ingest, then pick it from **Recent jobs**."
            )
        else:
            st.error(str(exc))
    except Exception as exc:
        st.error(str(exc))
