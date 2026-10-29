"""Corpus steward — sync, health, zero-result signals."""

from __future__ import annotations

import sqlite3
from typing import Any, Dict

from backend.app.config import settings
from backend.app.integrations.confluence_client import ConfluenceApiError, ConfluenceConfigError
from backend.app.services.analytics_service import get_summary
from backend.app.services.confluence_sync_service import get_status
from backend.app.services.onboarding_service import link_health, sync_guide_confluence_pages


def run(conn: sqlite3.Connection) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "confluence_sync": None,
        "link_health": None,
        "zero_result_queries": [],
        "knowledge_health_counts": {},
        "report_path": None,
    }

    if settings.confluence_enabled and settings.confluence_sync_enabled:
        status = get_status()
        if status.reachable:
            try:
                sync_result = sync_guide_confluence_pages(conn)
                summary["confluence_sync"] = sync_result.model_dump()
            except (ConfluenceConfigError, ConfluenceApiError) as exc:
                summary["confluence_sync"] = {"error": str(exc)}
        else:
            summary["confluence_sync"] = {"skipped": True, "reason": status.message or "not reachable"}

    health = link_health(conn)
    summary["link_health"] = {
        "total_with_url": health.total_with_url,
        "parseable": health.parseable,
        "broken": [i.model_dump() for i in health.items if i.issue],
    }

    analytics = get_summary(conn)
    summary["zero_result_queries"] = [
        {"query": z.query, "count": z.count} for z in analytics.zero_result_searches[:10]
    ]
    kh = analytics.knowledge_health
    summary["knowledge_health_counts"] = {
        "outdated": len(kh.outdated_documents),
        "untagged": len(kh.documents_without_tags),
        "never_accessed": len(kh.documents_never_accessed),
        "missing_version": len(kh.documents_missing_version),
        "potential_duplicates": len(kh.potential_duplicates),
    }

    lines = [
        "# Corpus steward report",
        "",
        "## Confluence (onboarding URLs)",
        str(summary["confluence_sync"]),
        "",
        "## Link health",
        f"- Parseable: **{summary['link_health']['parseable']}** / **{summary['link_health']['total_with_url']}**",
        "",
        "## Zero-result searches (top)",
    ]
    for row in summary["zero_result_queries"]:
        lines.append(f"- `{row['query']}` ({row['count']}x)")
    lines.extend(["", "## Knowledge health counts", str(summary["knowledge_health_counts"])])

    from backend.app.services.automation.report_util import write_report

    summary["report_path"] = write_report("corpus_steward", "inline", "\n".join(lines))
    summary["message"] = "Corpus steward completed."

    from backend.app.services.notify_service import notify

    lh = summary.get("link_health") or {}
    broken_n = len(lh.get("broken") or []) if isinstance(lh, dict) else 0
    issues = len(summary.get("zero_result_queries") or []) + broken_n
    if issues > 0:
        notify(
            "Corpus steward",
            f"Review recommended: {issues} issue signal(s) (zero-results / bad links). See {summary['report_path']}",
            level="warning",
        )
    return summary
