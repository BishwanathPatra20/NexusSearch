"""Content integrity for approved knowledge (SHA-256 fingerprints, source chunk lineage)."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from typing import List


def content_hash(text: str) -> str:
    normalized = (text or "").strip().encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def source_chunk_ids_for_review(conn: sqlite3.Connection, review_item_id: int) -> List[int]:
    rows = conn.execute(
        """
        SELECT chunk_id FROM review_sources
        WHERE review_item_id = ?
        ORDER BY relevance_score DESC
        """,
        (review_item_id,),
    ).fetchall()
    return [int(r["chunk_id"]) for r in rows]


def insert_approved_knowledge(
    conn: sqlite3.Connection,
    *,
    review_item_id: int,
    query: str,
    approved_answer: str,
    reviewer: str,
) -> None:
    answer_hash = content_hash(approved_answer)
    chunk_ids = source_chunk_ids_for_review(conn, review_item_id)
    conn.execute(
        """
        INSERT INTO approved_knowledge (
            review_item_id, query, approved_answer, reviewer,
            content_hash, source_chunk_ids_json
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            review_item_id,
            query,
            approved_answer,
            reviewer,
            answer_hash,
            json.dumps(chunk_ids),
        ),
    )
