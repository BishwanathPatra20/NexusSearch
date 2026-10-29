"""Search quality — synonym suggestions from zero-result queries."""

from __future__ import annotations

import json
import sqlite3
from typing import Any, Dict, List

from backend.app.config import settings
from backend.app.services.analytics_service import get_summary


def _suggest_synonym_key(query: str) -> str:
    token = query.strip().lower().split()[0] if query.strip() else ""
    return token[:40]


def run(conn: sqlite3.Connection) -> Dict[str, Any]:
    analytics = get_summary(conn)
    proposals: List[Dict[str, Any]] = []
    for item in analytics.zero_result_searches[:8]:
        key = _suggest_synonym_key(item.query)
        if not key or len(key) < 3:
            continue
        proposals.append(
            {
                "query": item.query,
                "count": item.count,
                "suggested_synonym_entry": {key: [item.query.strip()]},
                "note": "Review before adding to config/synonyms.json",
            }
        )

    existing: Dict[str, Any] = {}
    path = settings.synonyms_path
    if path.is_file():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}

    lines = [
        "# Search quality report",
        "",
        "Proposed synonym patches (not applied automatically):",
        "",
    ]
    for p in proposals:
        lines.append(f"- Query `{p['query']}` ({p['count']}x) → consider key `{list(p['suggested_synonym_entry'].keys())[0]}`")
    lines.extend(["", "## JSON snippets (copy after review)", "```json"])
    lines.append(json.dumps({k: v for p in proposals for k, v in p["suggested_synonym_entry"].items()}, indent=2))
    lines.append("```")
    lines.extend(["", f"Existing synonym keys: {len(existing)}"])

    from backend.app.services.automation.report_util import write_report

    report_path = write_report("search_quality", "inline", "\n".join(lines))

    from backend.app.services.notify_service import notify
    from backend.app.services.synonym_proposal_service import upsert_from_search_quality

    stored = upsert_from_search_quality(conn, proposals)
    if proposals:
        notify(
            "Search quality",
            f"{len(proposals)} zero-result pattern(s); {stored} new synonym proposal(s) pending approval.",
            level="info",
        )

    return {
        "proposals": proposals,
        "proposal_count": len(proposals),
        "proposals_stored": stored,
        "report_path": report_path,
        "message": f"Search quality: {len(proposals)} proposals ({stored} new in queue).",
    }
