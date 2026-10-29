"""Scheduled Confluence space sync (Gebo/Onyx-style refresh, local PAT only)."""

from __future__ import annotations

import json
import logging
import sqlite3
from typing import Any, Dict, Optional

from backend.app.config import settings
from backend.app.integrations.confluence_client import ConfluenceApiError, ConfluenceConfigError
from backend.app.services.confluence_sync_service import sync_descendants, sync_space
from backend.app.services.governance_audit_service import log_event

logger = logging.getLogger("knowledgepilot.confluence_schedule")


def get_schedule(conn: sqlite3.Connection) -> Dict[str, Any]:
    row = conn.execute("SELECT * FROM confluence_sync_schedules WHERE id = 1").fetchone()
    if row is None:
        return {
            "enabled": False,
            "space_key": settings.confluence_scheduled_space_key,
            "parent_page_id": settings.confluence_scheduled_parent_page_id,
            "max_pages": settings.confluence_scheduled_max_pages,
            "last_run_at": None,
        }
    return {
        "enabled": bool(row["enabled"]),
        "space_key": row["space_key"],
        "parent_page_id": row["parent_page_id"],
        "max_pages": int(row["max_pages"]),
        "last_run_at": row["last_run_at"],
    }


def upsert_schedule(
    conn: sqlite3.Connection,
    *,
    enabled: bool,
    space_key: Optional[str] = None,
    parent_page_id: Optional[str] = None,
    max_pages: int = 50,
) -> Dict[str, Any]:
    conn.execute(
        """
        INSERT INTO confluence_sync_schedules (
            id, enabled, space_key, parent_page_id, max_pages, updated_at
        )
        VALUES (1, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(id) DO UPDATE SET
            enabled = excluded.enabled,
            space_key = excluded.space_key,
            parent_page_id = excluded.parent_page_id,
            max_pages = excluded.max_pages,
            updated_at = datetime('now')
        """,
        (
            1 if enabled else 0,
            (space_key or "").strip() or None,
            (parent_page_id or "").strip() or None,
            max(5, min(max_pages, 200)),
        ),
    )
    return get_schedule(conn)


def run_scheduled_sync(conn: sqlite3.Connection) -> Dict[str, Any]:
    sched = get_schedule(conn)
    if not sched.get("enabled"):
        return {"skipped": True, "reason": "schedule disabled"}
    if not settings.confluence_enabled or not settings.confluence_sync_enabled:
        return {"skipped": True, "reason": "confluence disabled in settings"}

    result: Dict[str, Any] = {"mode": None}
    try:
        parent = sched.get("parent_page_id")
        space = sched.get("space_key")
        max_pages = int(sched.get("max_pages") or 50)
        if parent:
            result["mode"] = "descendants"
            sync_result = sync_descendants(
                conn,
                str(parent),
                max_pages=max_pages,
                tags=["confluence", "scheduled-sync"],
            )
            result["indexed"] = sync_result.indexed
            result["requested"] = sync_result.requested
            result["errors"] = sync_result.errors
        elif space:
            result["mode"] = "space"
            sync_result = sync_space(
                conn,
                str(space),
                limit=min(max_pages, 100),
                tags=["confluence", "scheduled-sync", f"space:{space}"],
            )
            result["indexed"] = sync_result.pages_indexed
            result["errors"] = sync_result.errors
        else:
            return {"skipped": True, "reason": "set space_key or parent_page_id"}

        conn.execute(
            """
            UPDATE confluence_sync_schedules
            SET last_run_at = datetime('now')
            WHERE id = 1
            """
        )
        log_event(
            conn,
            event_type="confluence.scheduled_sync",
            resource_type="confluence",
            resource_id=parent or space,
            detail=result,
        )
        logger.info("Scheduled Confluence sync finished: %s", result)
        return result
    except (ConfluenceConfigError, ConfluenceApiError) as exc:
        log_event(
            conn,
            event_type="confluence.scheduled_sync_failed",
            resource_type="confluence",
            detail={"error": str(exc)},
        )
        return {"error": str(exc)}
