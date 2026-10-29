"""Persist UI automation schedule (SQLite id=1)."""

from __future__ import annotations

import json
import sqlite3
from typing import List, Optional

from backend.app.schemas.agents import AutomationScheduleIn, AutomationScheduleOut


def ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS automation_schedules (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            enabled INTEGER NOT NULL DEFAULT 0,
            day_pattern TEXT NOT NULL DEFAULT 'monday',
            hour INTEGER NOT NULL DEFAULT 8,
            minute INTEGER NOT NULL DEFAULT 0,
            agents_json TEXT NOT NULL DEFAULT '[]',
            last_run_at TEXT,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )


def get_schedule(conn: sqlite3.Connection) -> AutomationScheduleOut:
    ensure_table(conn)
    row = conn.execute("SELECT * FROM automation_schedules WHERE id = 1").fetchone()
    if row is None:
        return AutomationScheduleOut(
            enabled=False,
            day_pattern="monday",
            hour=8,
            minute=0,
            timezone="UTC",
            agents=[],
            last_run_at=None,
        )
    agents = json.loads(row["agents_json"] or "[]")
    tz = row["timezone"] if "timezone" in row.keys() and row["timezone"] else "UTC"
    return AutomationScheduleOut(
        enabled=bool(row["enabled"]),
        day_pattern=row["day_pattern"],
        hour=int(row["hour"]),
        minute=int(row["minute"]),
        timezone=str(tz),
        agents=agents,
        last_run_at=row["last_run_at"],
    )


def save_schedule(conn: sqlite3.Connection, body: AutomationScheduleIn) -> AutomationScheduleOut:
    ensure_table(conn)
    agents_json = json.dumps(body.agents)
    conn.execute(
        """
        INSERT INTO automation_schedules (id, enabled, day_pattern, hour, minute, timezone, agents_json, updated_at)
        VALUES (1, ?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(id) DO UPDATE SET
            enabled = excluded.enabled,
            day_pattern = excluded.day_pattern,
            hour = excluded.hour,
            minute = excluded.minute,
            timezone = excluded.timezone,
            agents_json = excluded.agents_json,
            updated_at = datetime('now')
        """,
        (
            1 if body.enabled else 0,
            body.day_pattern,
            body.hour,
            body.minute,
            body.timezone or "UTC",
            agents_json,
        ),
    )
    return get_schedule(conn)


def touch_last_run(conn: sqlite3.Connection) -> None:
    ensure_table(conn)
    conn.execute(
        """
        UPDATE automation_schedules SET last_run_at = datetime('now') WHERE id = 1
        """
    )


def default_agent_list() -> List[str]:
    return [
        "corpus_steward",
        "new_hire_autopilot",
        "search_quality",
        "ingest_watcher",
        "review_triage",
    ]
