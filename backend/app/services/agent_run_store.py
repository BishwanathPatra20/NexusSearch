"""Persist automation agent runs for inbox / audit."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional


def ensure_agent_runs_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS agent_runs (
            execution_id TEXT PRIMARY KEY,
            agent_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'running',
            trigger TEXT NOT NULL DEFAULT 'manual',
            result_json TEXT,
            error_message TEXT,
            started_at TEXT NOT NULL DEFAULT (datetime('now')),
            finished_at TEXT
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_agent_runs_agent ON agent_runs(agent_name, started_at DESC)"
    )


def new_execution_id(prefix: str = "EX") -> str:
    stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"{prefix}-{stamp}-{uuid.uuid4().hex[:8]}"


def start_run(
    conn: sqlite3.Connection,
    agent_name: str,
    trigger: str = "manual",
    execution_id: Optional[str] = None,
) -> str:
    ensure_agent_runs_table(conn)
    eid = execution_id or new_execution_id()
    conn.execute(
        """
        INSERT INTO agent_runs (execution_id, agent_name, status, trigger)
        VALUES (?, ?, 'running', ?)
        """,
        (eid, agent_name, trigger),
    )
    return eid


def finish_run(
    conn: sqlite3.Connection,
    execution_id: str,
    status: str,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
) -> None:
    ensure_agent_runs_table(conn)
    conn.execute(
        """
        UPDATE agent_runs
        SET status = ?, result_json = ?, error_message = ?, finished_at = datetime('now')
        WHERE execution_id = ?
        """,
        (status, json.dumps(result) if result else None, error, execution_id),
    )


def get_run(conn: sqlite3.Connection, execution_id: str) -> Optional[sqlite3.Row]:
    ensure_agent_runs_table(conn)
    return conn.execute(
        "SELECT * FROM agent_runs WHERE execution_id = ?",
        (execution_id,),
    ).fetchone()


def list_runs(conn: sqlite3.Connection, limit: int = 30) -> List[sqlite3.Row]:
    ensure_agent_runs_table(conn)
    return conn.execute(
        """
        SELECT * FROM agent_runs
        ORDER BY started_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
