"""Compliance-friendly CSV export (reviews + governance snapshot)."""

from __future__ import annotations

import csv
import io
import sqlite3
from datetime import datetime

from backend.app.services.governance_service import get_governance_metrics


def build_audit_csv(conn: sqlite3.Connection) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["NexusSearch audit export", datetime.utcnow().isoformat() + "Z"])
    writer.writerow([])

    gov = get_governance_metrics(conn)
    rq = gov.review_quality
    writer.writerow(["Governance metrics"])
    writer.writerow(["questions_asked", rq.questions_asked])
    writer.writerow(["approval_rate_pct", rq.approval_rate_pct])
    writer.writerow(["pending", rq.pending])
    writer.writerow([])

    writer.writerow(["Review actions (latest 200)"])
    writer.writerow(["review_item_id", "action", "reviewer", "timestamp", "comment"])
    rows = conn.execute(
        """
        SELECT review_item_id, action, reviewer, timestamp, comment
        FROM review_actions
        ORDER BY timestamp DESC
        LIMIT 200
        """
    ).fetchall()
    for r in rows:
        writer.writerow([r["review_item_id"], r["action"], r["reviewer"], r["timestamp"], r["comment"] or ""])

    writer.writerow([])
    writer.writerow(["Approved knowledge (latest 100)"])
    writer.writerow(["id", "review_item_id", "query", "reviewer", "approved_at"])
    approved = conn.execute(
        """
        SELECT id, review_item_id, query, reviewer, approved_at
        FROM approved_knowledge
        ORDER BY approved_at DESC
        LIMIT 100
        """
    ).fetchall()
    for r in approved:
        writer.writerow([r["id"], r["review_item_id"], r["query"], r["reviewer"], r["approved_at"]])

    return buf.getvalue()
