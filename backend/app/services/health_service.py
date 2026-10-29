import sqlite3
from typing import List

from backend.app.schemas.models import DuplicatePair, KnowledgeHealthReport
from backend.app.services import document_service


def _summaries(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> List:
    rows = conn.execute(sql, params).fetchall()
    return [document_service._row_to_summary(conn, r, chunk_count=r["chunk_count"]) for r in rows]


def get_knowledge_health(conn: sqlite3.Connection) -> KnowledgeHealthReport:
    outdated = _summaries(
        conn,
        """
        SELECT d.*, COUNT(c.id) AS chunk_count
        FROM documents d
        LEFT JOIN document_chunks c ON c.document_id = d.id
        WHERE d.status IN ('deprecated', 'archived')
        GROUP BY d.id
        ORDER BY d.upload_date ASC
        LIMIT 20
        """,
    )
    without_tags = _summaries(
        conn,
        """
        SELECT d.*, COUNT(c.id) AS chunk_count
        FROM documents d
        LEFT JOIN document_chunks c ON c.document_id = d.id
        WHERE d.tags_json IN ('[]', '')
        GROUP BY d.id
        LIMIT 20
        """,
    )
    never_accessed = _summaries(
        conn,
        """
        SELECT d.*, COUNT(c.id) AS chunk_count
        FROM documents d
        LEFT JOIN document_chunks c ON c.document_id = d.id
        WHERE d.view_count = 0
        GROUP BY d.id
        ORDER BY d.upload_date DESC
        LIMIT 20
        """,
    )
    missing_version = _summaries(
        conn,
        """
        SELECT d.*, COUNT(c.id) AS chunk_count
        FROM documents d
        LEFT JOIN document_chunks c ON c.document_id = d.id
        WHERE d.version_label IS NULL OR trim(d.version_label) = ''
        GROUP BY d.id
        LIMIT 20
        """,
    )

    duplicates: List[DuplicatePair] = []
    rows = conn.execute(
        """
        SELECT id, title, file_name, content_fingerprint
        FROM documents
        WHERE content_fingerprint IS NOT NULL
        ORDER BY upload_date DESC
        """
    ).fetchall()
    seen_fp: dict[str, int] = {}
    for row in rows:
        fp = row["content_fingerprint"]
        if fp in seen_fp:
            other_id = seen_fp[fp]
            other = conn.execute(
                "SELECT title FROM documents WHERE id = ?", (other_id,)
            ).fetchone()
            duplicates.append(
                DuplicatePair(
                    document_id_a=other_id,
                    title_a=other["title"] if other else "",
                    document_id_b=row["id"],
                    title_b=row["title"],
                    similarity_pct=100.0,
                    reason="Identical content fingerprint",
                )
            )
            continue
        seen_fp[fp] = row["id"]

    for i, a in enumerate(rows):
        for b in rows[i + 1 : i + 40]:
            sim = document_service.title_similarity(a["title"], b["title"])
            if sim >= 0.92:
                duplicates.append(
                    DuplicatePair(
                        document_id_a=a["id"],
                        title_a=a["title"],
                        document_id_b=b["id"],
                        title_b=b["title"],
                        similarity_pct=round(sim * 100, 1),
                        reason="Similar title",
                    )
                )
        if len(duplicates) >= 15:
            break

    return KnowledgeHealthReport(
        outdated_documents=outdated,
        documents_without_tags=without_tags,
        documents_never_accessed=never_accessed,
        documents_missing_version=missing_version,
        potential_duplicates=duplicates[:15],
    )
