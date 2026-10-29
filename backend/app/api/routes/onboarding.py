from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field

from backend.app.db.connection import get_connection
from backend.app.integrations.confluence_client import ConfluenceApiError, ConfluenceConfigError
from backend.app.schemas.onboarding import (
    OnboardingConfluenceSyncResult,
    OnboardingImportResult,
    OnboardingLinkHealthResponse,
    OnboardingListResponse,
    OnboardingMeta,
    SuggestedAsksResponse,
)
from backend.app.services.onboarding_service import (
    default_xlsx_path,
    get_meta,
    import_xlsx,
    link_health,
    list_items,
    suggested_asks,
    sync_guide_confluence_pages,
)
router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.get("/meta", response_model=OnboardingMeta)
def onboarding_meta() -> OnboardingMeta:
    with get_connection() as conn:
        return get_meta(conn)


@router.get("/suggested-asks", response_model=SuggestedAsksResponse)
def onboarding_suggested_asks(limit: int = Query(12, ge=1, le=50)) -> SuggestedAsksResponse:
    with get_connection() as conn:
        return suggested_asks(conn, limit=limit)


@router.get("/items", response_model=OnboardingListResponse)
def onboarding_items(
    q: Optional[str] = Query(None, max_length=200),
    category: Optional[str] = Query(None),
    day: Optional[str] = Query(None),
    limit: int = Query(500, ge=1, le=2000),
) -> OnboardingListResponse:
    with get_connection() as conn:
        return list_items(conn, q=q, category=category, day=day, limit=limit)


@router.post("/import-file", response_model=OnboardingImportResult)
async def import_onboarding_file(file: UploadFile = File(...)) -> OnboardingImportResult:
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xlsm")):
        raise HTTPException(status_code=400, detail="Upload an Excel workbook (.xlsx)")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    from backend.app.config import settings

    settings.onboarding_dir.mkdir(parents=True, exist_ok=True)
    dest = settings.onboarding_dir / Path(file.filename).name
    dest.write_bytes(data)

    with get_connection() as conn:
        try:
            result = import_xlsx(conn, dest)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    _maybe_run_new_hire_autopilot()
    return result


@router.post("/import-default", response_model=OnboardingImportResult)
def import_default_workbook() -> OnboardingImportResult:
    path = default_xlsx_path()
    if not path.is_file():
        raise HTTPException(
            status_code=404,
            detail=(
                f"Place your workbook at {path} or use POST /onboarding/import-file "
                "from the New hire guide page."
            ),
        )
    with get_connection() as conn:
        result = import_xlsx(conn, path)
    _maybe_run_new_hire_autopilot()
    return result


def _maybe_run_new_hire_autopilot() -> None:
    try:
        from backend.app.services.automation.runner import run_automation_agent

        with get_connection() as conn:
            run_automation_agent(conn, "new_hire_autopilot", trigger="event_import")
    except Exception:
        pass  # import must succeed even if automation fails


@router.get("/link-health", response_model=OnboardingLinkHealthResponse)
def onboarding_link_health() -> OnboardingLinkHealthResponse:
    with get_connection() as conn:
        return link_health(conn)


class OnboardingConfluenceSyncBody(BaseModel):
    tags: list[str] = Field(default_factory=lambda: ["confluence", "onboarding"])


@router.post("/sync-confluence", response_model=OnboardingConfluenceSyncResult)
def onboarding_sync_confluence(body: OnboardingConfluenceSyncBody) -> OnboardingConfluenceSyncResult:
    try:
        with get_connection() as conn:
            return sync_guide_confluence_pages(conn, tags=body.tags)
    except ConfluenceConfigError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ConfluenceApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
