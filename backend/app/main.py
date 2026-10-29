import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import (
    agent_tools,
    agents,
    analytics,
    ask,
    config_status,
    confluence,
    documents,
    governance,
    synonyms,
    jobs,
    lineage,
    onboarding,
    reviews,
    search,
    rag,
)
from backend.app.config import settings
from backend.app.db.connection import bootstrap_database, get_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("knowledgepilot")

bootstrap_database()


def _maybe_import_onboarding_workbook() -> None:
    from backend.app.services.onboarding_service import default_xlsx_path, get_meta, import_xlsx

    path = default_xlsx_path()
    if not path.is_file():
        return
    try:
        with get_connection() as conn:
            meta = get_meta(conn)
            if meta.total > 0:
                return
            result = import_xlsx(conn, path)
            logger.info("Onboarding workbook auto-imported: %s", result.message)
    except Exception as exc:
        logger.warning("Onboarding auto-import skipped: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.offline_mode:
        logger.info(
            "KnowledgePilot started in offline mode — no external services configured."
        )
    _maybe_import_onboarding_workbook()
    from backend.app.services.automation_scheduler import reload_scheduler

    reload_scheduler()
    from backend.app.services.automation_scheduler import reload_confluence_scheduler

    reload_confluence_scheduler()
    yield
    from backend.app.services.automation_scheduler import shutdown_scheduler

    shutdown_scheduler()


app = FastAPI(
    title="NexusSearch API",
    description="Local-first knowledge governance platform — v1.1",
    version="1.1.0",
    lifespan=lifespan,
)

# Restrict CORS to local Streamlit origins only (office-safe default).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8501",
        "http://localhost:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prefix = settings.api_prefix
app.include_router(confluence.router, prefix=prefix)
app.include_router(documents.router, prefix=prefix)
app.include_router(search.router, prefix=prefix)
app.include_router(rag.router, prefix=prefix)
app.include_router(governance.router, prefix=prefix)
app.include_router(agent_tools.router, prefix=prefix)
app.include_router(analytics.router, prefix=prefix)
app.include_router(jobs.router, prefix=prefix)
app.include_router(ask.router, prefix=prefix)
app.include_router(reviews.router, prefix=prefix)
app.include_router(lineage.router, prefix=prefix)
app.include_router(onboarding.router, prefix=prefix)
app.include_router(agents.router, prefix=prefix)
app.include_router(synonyms.router, prefix=prefix)
app.include_router(config_status.router, prefix=prefix)


@app.get("/")
def root() -> dict:
    return {
        "service": "nexussearch",
        "status": "ok",
        "health": "/health",
        "api": prefix,
        "docs": "/docs",
        "ui": "http://127.0.0.1:8501",
    }


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "nexussearch",
        "version": app.version,
        "offline_mode": settings.offline_mode,
        "host": settings.host,
    }
