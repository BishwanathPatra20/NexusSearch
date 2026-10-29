from fastapi import APIRouter

from backend.app.config import settings
from backend.app.services.automation.ingest_watcher import watch_paths
from backend.app.services.confluence_sync_service import get_status

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/status")
def config_status() -> dict:
    cf = get_status()
    paths = [str(p) for p in watch_paths()] if settings.watch_enabled else []
    return {
        "confluence_enabled": settings.confluence_enabled,
        "confluence_sync_enabled": settings.confluence_sync_enabled,
        "confluence_reachable": cf.reachable,
        "watch_enabled": settings.watch_enabled,
        "watch_paths": paths,
        "api_key_configured": bool(settings.api_key),
        "notify_webhook_configured": bool(settings.notify_webhook_url),
        "synonyms_path": str(settings.synonyms_path),
        "agent_reports_dir": str(settings.agent_reports_dir),
        "offline_mode": settings.offline_mode,
        "rag_bot_enabled": settings.rag_bot_enabled,
        "rag_llm_enabled": settings.rag_llm_enabled,
    }
