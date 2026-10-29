"""Pending synonym proposals from search_quality — approve merges into synonyms.json."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.app.config import settings
from backend.app.services.synonym_service import reload_synonyms_cache


def ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS synonym_proposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            canonical_key TEXT NOT NULL,
            suggested_term TEXT NOT NULL,
            sample_query TEXT,
            hit_count INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )


def upsert_from_search_quality(conn: sqlite3.Connection, proposals: List[Dict[str, Any]]) -> int:
    ensure_table(conn)
    added = 0
    for p in proposals:
        entry = p.get("suggested_synonym_entry") or {}
        for key, terms in entry.items():
            term = (terms[0] if terms else p.get("query", "")).strip()
            if not key or not term:
                continue
            exists = conn.execute(
                """
                SELECT id FROM synonym_proposals
                WHERE status = 'pending' AND canonical_key = ? AND suggested_term = ?
                """,
                (key, term),
            ).fetchone()
            if exists:
                continue
            conn.execute(
                """
                INSERT INTO synonym_proposals (canonical_key, suggested_term, sample_query, hit_count)
                VALUES (?, ?, ?, ?)
                """,
                (key, term, p.get("query"), int(p.get("count") or 0)),
            )
            added += 1
    return added


def list_pending(conn: sqlite3.Connection, limit: int = 50) -> List[Dict[str, Any]]:
    ensure_table(conn)
    rows = conn.execute(
        """
        SELECT * FROM synonym_proposals
        WHERE status = 'pending'
        ORDER BY hit_count DESC, created_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [dict(r) for r in rows]


def _load_synonyms() -> Dict[str, List[str]]:
    path = settings.synonyms_path
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _save_synonyms(data: Dict[str, List[str]]) -> None:
    path = settings.synonyms_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    reload_synonyms_cache()


def approve(conn: sqlite3.Connection, proposal_id: int) -> Dict[str, Any]:
    ensure_table(conn)
    row = conn.execute(
        "SELECT * FROM synonym_proposals WHERE id = ? AND status = 'pending'",
        (proposal_id,),
    ).fetchone()
    if row is None:
        raise KeyError("Proposal not found")
    key = row["canonical_key"]
    term = row["suggested_term"]
    data = _load_synonyms()
    existing = data.get(key, [])
    if term not in existing:
        data[key] = sorted(set(existing + [term]))
        _save_synonyms(data)
    conn.execute(
        "UPDATE synonym_proposals SET status = 'approved' WHERE id = ?",
        (proposal_id,),
    )
    return {"id": proposal_id, "canonical_key": key, "added_term": term}


def dismiss(conn: sqlite3.Connection, proposal_id: int) -> None:
    ensure_table(conn)
    conn.execute(
        "UPDATE synonym_proposals SET status = 'dismissed' WHERE id = ? AND status = 'pending'",
        (proposal_id,),
    )
