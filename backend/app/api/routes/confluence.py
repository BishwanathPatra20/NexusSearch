from typing import List

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query

from backend.app.db.connection import get_connection
from backend.app.integrations.confluence_client import ConfluenceApiError, ConfluenceConfigError
from backend.app.schemas.confluence import (
    ConfluenceDescendantsSyncRequest,
    ConfluencePageSyncRequest,
    ConfluencePageSyncResult,
    ConfluencePagesSyncRequest,
    ConfluencePagesSyncResult,
    ConfluenceSpaceOut,
    ConfluenceSpaceValidate,
    ConfluenceStatus,
    ConfluenceSyncJobRequest,
    ConfluenceSyncJobResponse,
    ConfluenceSyncRequest,
    ConfluenceSyncResult,
)
from backend.app.schemas.models import ConfluenceCorpusStats
from backend.app.services.confluence_sync_service import (
    get_corpus_stats,
    get_status,
    list_spaces,
    sync_descendants,
    sync_page,
    sync_pages,
    sync_space,
    validate_space,
)
from backend.app.services.job_service import create_job, process_confluence_sync_job

router = APIRouter(prefix="/confluence", tags=["confluence"])


@router.get("/status", response_model=ConfluenceStatus)
def confluence_status() -> ConfluenceStatus:
    return get_status()


@router.get("/stats", response_model=ConfluenceCorpusStats)
def confluence_stats() -> ConfluenceCorpusStats:
    with get_connection() as conn:
        return get_corpus_stats(conn)


@router.get("/search-live")
def confluence_search_live(
    q: str = Query(..., min_length=2, max_length=500),
    limit: int = Query(5, ge=1, le=15),
) -> dict:
    """Live Confluence title/site search via PAT (pages not required to be ingested)."""
    from backend.app.services.confluence_live_search_service import confluence_live_for_search

    try:
        with get_connection() as conn:
            hits, err = confluence_live_for_search(conn, q, local_hits=[])
            hits = hits[:limit]
            return {
                "query": q,
                "count": len(hits),
                "error": err,
                "results": [h.model_dump() for h in hits],
            }
    except ConfluenceConfigError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ConfluenceApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/space/{space_key}", response_model=ConfluenceSpaceValidate)
def confluence_validate_space(space_key: str) -> ConfluenceSpaceValidate:
    try:
        return validate_space(space_key)
    except ConfluenceConfigError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ConfluenceApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/spaces", response_model=List[ConfluenceSpaceOut])
def confluence_spaces(limit: int = Query(500, ge=1, le=500)) -> List[ConfluenceSpaceOut]:
    try:
        return list_spaces(limit=limit)
    except ConfluenceConfigError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ConfluenceApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/sync-page", response_model=ConfluencePageSyncResult)
def confluence_sync_page(body: ConfluencePageSyncRequest) -> ConfluencePageSyncResult:
    try:
        with get_connection() as conn:
            return sync_page(
                conn,
                page_id=body.page_id.strip(),
                tags=body.tags,
                replace_existing=body.replace_existing,
            )
    except ConfluenceConfigError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ConfluenceApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/sync-pages", response_model=ConfluencePagesSyncResult)
def confluence_sync_pages(body: ConfluencePagesSyncRequest) -> ConfluencePagesSyncResult:
    try:
        with get_connection() as conn:
            return sync_pages(
                conn,
                page_ids=body.page_ids,
                tags=body.tags,
                replace_existing=body.replace_existing,
            )
    except ConfluenceConfigError as exc:
        raise HTTPException(status_code=403 if "disabled" in str(exc).lower() else 400, detail=str(exc)) from exc
    except ConfluenceApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/sync-descendants", response_model=ConfluencePagesSyncResult)
def confluence_sync_descendants(body: ConfluenceDescendantsSyncRequest) -> ConfluencePagesSyncResult:
    try:
        with get_connection() as conn:
            return sync_descendants(
                conn,
                parent_page_id=body.parent_page_id.strip(),
                max_pages=body.max_pages,
                include_parent=body.include_parent,
                tags=body.tags,
                replace_existing=body.replace_existing,
            )
    except ConfluenceConfigError as exc:
        raise HTTPException(status_code=403 if "disabled" in str(exc).lower() else 400, detail=str(exc)) from exc
    except ConfluenceApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/sync", response_model=ConfluenceSyncResult)
def confluence_sync(body: ConfluenceSyncRequest) -> ConfluenceSyncResult:
    try:
        with get_connection() as conn:
            return sync_space(
                conn,
                space_key=body.space_key.strip(),
                limit=body.limit,
                tags=body.tags,
                replace_existing=body.replace_existing,
            )
    except ConfluenceConfigError as exc:
        raise HTTPException(status_code=403 if "disabled" in str(exc).lower() else 400, detail=str(exc)) from exc
    except ConfluenceApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/sync-job", response_model=ConfluenceSyncJobResponse)
def confluence_sync_job(
    body: ConfluenceSyncJobRequest,
    background_tasks: BackgroundTasks,
) -> ConfluenceSyncJobResponse:
    if not body.space_key and not body.parent_page_id:
        raise HTTPException(status_code=400, detail="Provide space_key or parent_page_id")
    payload = body.model_dump()
    with get_connection() as conn:
        job_id = create_job(conn, "confluence_sync", payload)
    background_tasks.add_task(process_confluence_sync_job, job_id)
    return ConfluenceSyncJobResponse(
        job_id=job_id,
        message="Confluence sync queued (local background worker).",
    )


@router.get("/sync-schedule")
def confluence_sync_schedule_get() -> dict:
    with get_connection() as conn:
        from backend.app.services.confluence_schedule_service import get_schedule

        return get_schedule(conn)


@router.put("/sync-schedule")
def confluence_sync_schedule_put(body: dict) -> dict:
    from backend.app.services.automation_scheduler import reload_confluence_scheduler
    from backend.app.services.confluence_schedule_service import upsert_schedule

    with get_connection() as conn:
        result = upsert_schedule(
            conn,
            enabled=bool(body.get("enabled")),
            space_key=body.get("space_key"),
            parent_page_id=body.get("parent_page_id"),
            max_pages=int(body.get("max_pages") or 50),
        )
    reload_confluence_scheduler()
    return result


@router.post("/sync-schedule/run-now")
def confluence_sync_schedule_run_now() -> dict:
    with get_connection() as conn:
        from backend.app.services.confluence_schedule_service import run_scheduled_sync

        return run_scheduled_sync(conn)
