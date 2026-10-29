import json
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, Query

from backend.app.db.connection import get_connection
from backend.app.schemas.models import JobStatus
from backend.app.services.job_service import get_job, list_jobs

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _row_to_status(row) -> JobStatus:
    result = json.loads(row["result_json"]) if row["result_json"] else None
    return JobStatus(
        id=row["id"],
        job_type=row["job_type"],
        status=row["status"],
        result_json=result,
        error_message=row["error_message"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


@router.get("", response_model=List[JobStatus])
def jobs_index(limit: int = Query(default=15, ge=1, le=50)) -> List[JobStatus]:
    with get_connection() as conn:
        rows = list_jobs(conn, limit=limit)
    return [_row_to_status(row) for row in rows]


@router.get("/{job_id}", response_model=JobStatus)
def job_status(job_id: int) -> JobStatus:
    with get_connection() as conn:
        row = get_job(conn, job_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return _row_to_status(row)
