"""Agent catalog for GET /agents."""

from __future__ import annotations

from backend.app.config import settings
from backend.app.schemas.agents import AgentRegistryItem


def list_agents() -> list[AgentRegistryItem]:
    confluence_on = settings.confluence_enabled and settings.confluence_sync_enabled
    return [
        AgentRegistryItem(
            name="planner",
            kind="interactive",
            enabled=True,
            description="Classify intent and build execution plan",
        ),
        AgentRegistryItem(
            name="search",
            kind="interactive",
            enabled=True,
            description="Retrieve cited evidence chunks (FTS)",
        ),
        AgentRegistryItem(
            name="rank",
            kind="interactive",
            enabled=True,
            description="Score and order hits (embedded in search)",
        ),
        AgentRegistryItem(
            name="evidence",
            kind="interactive",
            enabled=True,
            description="Package citations for summary/validation",
        ),
        AgentRegistryItem(
            name="summarize",
            kind="interactive",
            enabled=True,
            description="Extractive draft answer (no cloud LLM)",
        ),
        AgentRegistryItem(
            name="validate",
            kind="interactive",
            enabled=True,
            description="Check draft against evidence",
        ),
        AgentRegistryItem(
            name="review",
            kind="interactive",
            enabled=True,
            description="Queue human governance review",
        ),
        AgentRegistryItem(
            name="orchestrate",
            kind="interactive",
            enabled=True,
            description="Run full governed pipeline (POST /orchestrate)",
        ),
        AgentRegistryItem(
            name="corpus_steward",
            kind="automation",
            enabled=True,
            description="Sync onboarding Confluence URLs, health + zero-result report",
        ),
        AgentRegistryItem(
            name="new_hire_autopilot",
            kind="automation",
            enabled=True,
            description="Post-import sync + draft reviews for suggested asks",
        ),
        AgentRegistryItem(
            name="search_quality",
            kind="automation",
            enabled=True,
            description="Propose synonym gaps from zero-result searches",
        ),
        AgentRegistryItem(
            name="confluence_sync",
            kind="automation",
            enabled=confluence_on,
            description="Confluence live sync (requires PAT in .env)",
        ),
        AgentRegistryItem(
            name="ingest_watcher",
            kind="automation",
            enabled=bool(settings.watch_enabled and settings.watch_folder),
            description="Index new files in KNOWLEDGEPILOT_WATCH_FOLDER",
        ),
        AgentRegistryItem(
            name="review_triage",
            kind="automation",
            enabled=True,
            description="Group similar pending reviews (report + Governed Ask UI)",
        ),
    ]
