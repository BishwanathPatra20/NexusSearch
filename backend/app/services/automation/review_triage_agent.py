"""Automation wrapper — write triage summary report."""

from __future__ import annotations

import sqlite3
from typing import Any, Dict

from backend.app.services.automation.report_util import write_report
from backend.app.services.review_triage_service import build_triage


def run(conn: sqlite3.Connection) -> Dict[str, Any]:
    triage = build_triage(conn, status="pending")
    lines = [
        "# Review triage report",
        "",
        f"Pending reviews: **{triage.total_pending}**",
        f"Batches: **{len(triage.batches)}**",
        "",
    ]
    for batch in triage.batches:
        lines.append(f"## {batch.label} ({batch.count})")
        for item in batch.items[:8]:
            lines.append(f"- #{item.review_id} · {item.confidence_score}% · {item.query[:80]}")
        lines.append("")
    report_path = write_report("review_triage", "inline", "\n".join(lines))
    return {
        "total_pending": triage.total_pending,
        "batch_count": len(triage.batches),
        "report_path": report_path,
        "message": f"Review triage: {triage.total_pending} pending in {len(triage.batches)} groups.",
    }
