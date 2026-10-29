"""New-hire autopilot — sync guide + queue suggested asks as drafts."""

from __future__ import annotations

import sqlite3
from typing import Any, Dict, List

from backend.app.config import settings
from backend.app.integrations.confluence_client import ConfluenceApiError, ConfluenceConfigError
from backend.app.services.onboarding_service import (
    get_meta,
    link_health,
    suggested_asks,
    sync_guide_confluence_pages,
)
from backend.app.services.review_service import ask_and_queue, list_review_items


def _pending_queries(conn: sqlite3.Connection) -> set[str]:
    items = list_review_items(conn, status="pending")
    return {i.query.strip().lower() for i in items}


def run(conn: sqlite3.Connection) -> Dict[str, Any]:
    meta = get_meta(conn)
    result: Dict[str, Any] = {
        "onboarding_total": meta.total,
        "confluence_sync": None,
        "link_health": None,
        "drafts_created": [],
        "drafts_skipped": [],
        "report_path": None,
    }

    if meta.total == 0:
        result["message"] = "No onboarding rows — import workbook first."
        return result

    if settings.confluence_enabled and settings.confluence_sync_enabled:
        try:
            result["confluence_sync"] = sync_guide_confluence_pages(conn).model_dump()
        except (ConfluenceConfigError, ConfluenceApiError) as exc:
            result["confluence_sync"] = {"error": str(exc)}

    lh = link_health(conn)
    result["link_health"] = {
        "parseable": lh.parseable,
        "total_with_url": lh.total_with_url,
        "issues": len([i for i in lh.items if i.issue]),
    }

    pending = _pending_queries(conn)
    limit = max(1, min(settings.automation_suggested_ask_limit, 12))
    asks = suggested_asks(conn, limit=limit).items

    for item in asks:
        q = item.question.strip()
        if not q:
            continue
        if q.lower() in pending:
            result["drafts_skipped"].append({"query": q, "reason": "already pending"})
            continue
        try:
            resp = ask_and_queue(conn, q, submit_for_review=True)
            if resp.confidence_score < settings.automation_reject_below_score:
                from backend.app.services.review_service import reject_item

                reject_item(
                    conn,
                    resp.review_item_id,
                    reviewer="automation-agent",
                    comment="Auto-rejected: validation score below automation threshold",
                )
                result["drafts_skipped"].append(
                    {"query": q, "reason": f"low score {resp.confidence_score}"}
                )
            else:
                result["drafts_created"].append(
                    {"query": q, "review_id": resp.review_item_id, "score": resp.confidence_score}
                )
                pending.add(q.lower())
        except Exception as exc:  # noqa: BLE001 — per-question isolation
            result["drafts_skipped"].append({"query": q, "reason": str(exc)})

    lines = [
        "# New hire autopilot report",
        "",
        f"Onboarding items: **{meta.total}**",
        "",
        "## Confluence sync",
        str(result["confluence_sync"]),
        "",
        "## Link health",
        str(result["link_health"]),
        "",
        "## Drafts created",
    ]
    for row in result["drafts_created"]:
        lines.append(f"- #{row['review_id']} · {row['query']} ({row['score']}%)")
    lines.append("")
    lines.append("## Skipped")
    for row in result["drafts_skipped"]:
        lines.append(f"- {row['query']}: {row['reason']}")

    from backend.app.services.automation.report_util import write_report

    result["report_path"] = write_report("new_hire_autopilot", "inline", "\n".join(lines))
    result["message"] = (
        f"New hire autopilot: {len(result['drafts_created'])} drafts, "
        f"{len(result['drafts_skipped'])} skipped."
    )
    return result
