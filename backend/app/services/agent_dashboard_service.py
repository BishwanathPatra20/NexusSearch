"""Exec-friendly automation + governance status."""

from __future__ import annotations

import sqlite3
from typing import List, Tuple

from backend.app.schemas.agents import AgentDashboardOut, AgentDashboardRunBrief
from backend.app.services.agent_run_store import list_runs
from backend.app.services.automation_schedule_service import get_schedule

# Health uses recurring zero-result patterns (2+ searches), not one-off typos.
_ZERO_RECURRING_YELLOW = 3
_ZERO_RECURRING_RED = 6
_PENDING_YELLOW = 5
_PENDING_RED = 15


def _count_zero_groups(conn: sqlite3.Connection, min_searches: int) -> int:
    row = conn.execute(
        """
        SELECT COUNT(*) AS c FROM (
            SELECT 1 FROM search_history
            WHERE results_count = 0
            GROUP BY lower(trim(query))
            HAVING COUNT(*) >= ?
        )
        """,
        (min_searches,),
    ).fetchone()
    return int(row["c"])


def _top_zero_hotspots(conn: sqlite3.Connection, limit: int = 3) -> List[str]:
    rows = conn.execute(
        """
        SELECT lower(trim(query)) AS q, COUNT(*) AS c
        FROM search_history
        WHERE results_count = 0
        GROUP BY lower(trim(query))
        HAVING COUNT(*) >= 2
        ORDER BY c DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [f"{r['q'][:48]} ({r['c']}×)" for r in rows]


def _health_color(pending_reviews: int, last_run_failed: bool, zero_recurring: int) -> str:
    if last_run_failed or pending_reviews > _PENDING_RED or zero_recurring > _ZERO_RECURRING_RED:
        return "red"
    if pending_reviews > _PENDING_YELLOW or zero_recurring > _ZERO_RECURRING_YELLOW:
        return "yellow"
    return "green"


def _health_detail(
    pending: int,
    last_run_failed: bool,
    zero_distinct: int,
    zero_recurring: int,
    hotspots: List[str],
) -> Tuple[List[str], List[str]]:
    reasons: List[str] = []
    actions: List[str] = []

    if last_run_failed:
        reasons.append("The most recent automation run failed.")
        actions.append("Open **Automations** → check run history and re-run failed agents.")
    if pending > _PENDING_RED:
        reasons.append(f"Review backlog is high ({pending} pending items).")
    elif pending > _PENDING_YELLOW:
        reasons.append(f"Review backlog is elevated ({pending} pending; yellow above {_PENDING_YELLOW}).")
    if pending > 0:
        actions.append(
            "Open **Governed Ask** → use triage batch approve or approve/reject pending items."
        )

    if zero_recurring > _ZERO_RECURRING_RED:
        reasons.append(
            f"Many recurring zero-result searches ({zero_recurring} query patterns with 2+ misses)."
        )
    elif zero_recurring > _ZERO_RECURRING_YELLOW:
        reasons.append(
            f"Recurring zero-result searches ({zero_recurring} patterns with 2+ misses)."
        )
    elif zero_distinct > _ZERO_RECURRING_YELLOW and zero_recurring == 0:
        reasons.append(
            f"{zero_distinct} distinct zero-result queries, but none repeated yet (informational)."
        )

    if hotspots:
        reasons.append("Top gaps: " + "; ".join(hotspots))

    if zero_recurring > 0 or zero_distinct > 0:
        actions.append(
            "Open **Analytics** → Synonyms; run **search_quality** on **Automations**."
        )
        actions.append(
            "POST **/api/v1/analytics/dedupe-search-gaps** to collapse duplicate zero-result rows (keeps one per query)."
        )

    if not reasons:
        reasons.append("Automations healthy and governance queue within targets.")

    # De-dupe while preserving order
    seen = set()
    actions = [a for a in actions if not (a in seen or seen.add(a))]

    return reasons, actions


def build_dashboard(conn: sqlite3.Connection) -> AgentDashboardOut:
    sched = get_schedule(conn)
    rows = list_runs(conn, limit=8)
    runs: List[AgentDashboardRunBrief] = []
    for row in rows:
        runs.append(
            AgentDashboardRunBrief(
                execution_id=row["execution_id"],
                agent_name=row["agent_name"],
                status=row["status"],
                finished_at=row["finished_at"],
            )
        )

    last_run_failed = bool(rows and rows[0]["status"] == "failed")

    pending = int(
        conn.execute(
            "SELECT COUNT(*) AS c FROM review_items WHERE status = 'pending'"
        ).fetchone()["c"]
    )
    zero_distinct = _count_zero_groups(conn, min_searches=1)
    zero_recurring = _count_zero_groups(conn, min_searches=2)
    hotspots = _top_zero_hotspots(conn)

    health = _health_color(pending, last_run_failed, zero_recurring)
    reasons, actions = _health_detail(
        pending, last_run_failed, zero_distinct, zero_recurring, hotspots
    )

    schedule_label = None
    if sched.enabled:
        schedule_label = f"{sched.day_pattern} {sched.hour:02d}:{sched.minute:02d} {sched.timezone}"

    return AgentDashboardOut(
        health=health,
        health_reasons=reasons,
        health_actions=actions,
        pending_reviews=pending,
        zero_result_query_groups=zero_distinct,
        zero_result_recurring_groups=zero_recurring,
        schedule_enabled=sched.enabled,
        schedule_label=schedule_label,
        last_run_at=sched.last_run_at,
        recent_runs=runs,
    )
