from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from backend.app.db.connection import get_connection
from backend.app.schemas.models import AnalyticsSummary, GovernanceMetricsOut
from backend.app.services.analytics_service import get_summary
from backend.app.services.audit_export_service import build_audit_csv
from backend.app.services.governance_service import get_governance_metrics

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def analytics_summary() -> AnalyticsSummary:
    with get_connection() as conn:
        return get_summary(conn)


@router.get("/governance", response_model=GovernanceMetricsOut)
def governance_metrics() -> GovernanceMetricsOut:
    with get_connection() as conn:
        return get_governance_metrics(conn)


@router.post("/dedupe-search-gaps")
def dedupe_search_gaps() -> dict:
    """Collapse duplicate zero-result rows per query (keeps latest); improves automation health."""
    from backend.app.services.search_history_service import dedupe_zero_result_queries

    with get_connection() as conn:
        return dedupe_zero_result_queries(conn)


@router.get("/export/audit-pack.csv", response_class=PlainTextResponse)
def export_audit_pack() -> PlainTextResponse:
    with get_connection() as conn:
        csv_text = build_audit_csv(conn)
    return PlainTextResponse(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=nexussearch_audit_pack.csv"},
    )
