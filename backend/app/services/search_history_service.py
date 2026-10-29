"""Search history maintenance — dedupe repeated zero-result rows for health metrics."""

from __future__ import annotations

import sqlite3
from typing import Dict, List


def dedupe_zero_result_queries(conn: sqlite3.Connection) -> Dict[str, int]:
    """
    For each normalized query with results_count=0, keep the newest row only.
    Removes duplicate misses from automation health (same query searched many times).
    """
    groups = conn.execute(
        """
        SELECT lower(trim(query)) AS qkey, COUNT(*) AS c
        FROM search_history
        WHERE results_count = 0
        GROUP BY qkey
        HAVING COUNT(*) > 1
        """
    ).fetchall()
    deleted = 0
    kept = 0
    patterns: List[str] = []
    for row in groups:
        qkey = row["qkey"]
        patterns.append(qkey)
        keep_id = conn.execute(
            """
            SELECT id FROM search_history
            WHERE results_count = 0 AND lower(trim(query)) = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (qkey,),
        ).fetchone()
        if not keep_id:
            continue
        kid = int(keep_id["id"])
        kept += 1
        cur = conn.execute(
            """
            DELETE FROM search_history
            WHERE results_count = 0
              AND lower(trim(query)) = ?
              AND id != ?
            """,
            (qkey, kid),
        )
        deleted += cur.rowcount
    return {
        "patterns_collapsed": len(patterns),
        "rows_kept": kept,
        "rows_deleted": deleted,
        "sample_patterns": patterns[:10],
    }
