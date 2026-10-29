import json
import sqlite3
from collections import Counter
from typing import List

from backend.app.schemas.models import (
    GovernanceKnowledgeMetrics,
    GovernanceMetricsOut,
    ReviewQualityMetrics,
    SearchQualityItem,
    TopSearchItem,
    TrustedDocumentItem,
    ValidatorInsightMetrics,
)


def _pct(part: int, whole: int) -> float:
    if whole <= 0:
        return 0.0
    return round(part / whole * 100.0, 1)


def get_governance_metrics(conn: sqlite3.Connection) -> GovernanceMetricsOut:
    total_asked = int(conn.execute("SELECT COUNT(*) AS c FROM review_items").fetchone()["c"])
    status_rows = conn.execute(
        "SELECT status, COUNT(*) AS c FROM review_items GROUP BY status"
    ).fetchall()
    counts = {r["status"]: int(r["c"]) for r in status_rows}
    pending = counts.get("pending", 0)
    approved = counts.get("approved", 0)
    rejected = counts.get("rejected", 0)
    edited = counts.get("edited", 0)
    decided = approved + rejected + edited
    review_quality = ReviewQualityMetrics(
        questions_asked=total_asked,
        pending=pending,
        approved=approved,
        rejected=rejected,
        edited=edited,
        approval_rate_pct=_pct(approved + edited, decided),
        rejection_rate_pct=_pct(rejected, decided),
        edit_rate_pct=_pct(edited, decided),
    )

    avg_row = conn.execute(
        "SELECT AVG(confidence_score) AS avg_score FROM review_items"
    ).fetchone()
    avg_score = round(float(avg_row["avg_score"] or 0.0), 1)
    low_conf = int(
        conn.execute(
            "SELECT COUNT(*) AS c FROM review_items WHERE confidence_score < 55"
        ).fetchone()["c"]
    )
    note_counter: Counter[str] = Counter()
    for row in conn.execute("SELECT validator_notes_json FROM review_items").fetchall():
        try:
            notes = json.loads(row["validator_notes_json"] or "[]")
            for note in notes:
                if note:
                    note_counter[str(note)] += 1
        except json.JSONDecodeError:
            continue
    common_notes = [
        TopSearchItem(query=text, count=count)
        for text, count in note_counter.most_common(8)
    ]
    validator_insights = ValidatorInsightMetrics(
        average_validation_score=avg_score,
        low_confidence_drafts=low_conf,
        common_validator_notes=common_notes,
    )

    approved_entries = int(
        conn.execute("SELECT COUNT(*) AS c FROM approved_knowledge").fetchone()["c"]
    )
    deprecated_citations = int(
        conn.execute(
            """
            SELECT COUNT(*) AS c
            FROM review_sources rs
            JOIN documents d ON d.id = rs.document_id
            WHERE d.status IN ('deprecated', 'archived')
            """
        ).fetchone()["c"]
    )
    trusted_rows = conn.execute(
        """
        SELECT
            d.id AS document_id,
            d.title,
            d.file_name,
            d.status,
            COUNT(rs.id) AS citation_count
        FROM review_sources rs
        JOIN documents d ON d.id = rs.document_id
        JOIN review_items ri ON ri.id = rs.review_item_id
        WHERE ri.status IN ('approved', 'edited')
           OR EXISTS (
                SELECT 1 FROM approved_knowledge ak WHERE ak.review_item_id = ri.id
           )
        GROUP BY d.id
        ORDER BY citation_count DESC
        LIMIT 10
        """
    ).fetchall()
    most_trusted = [
        TrustedDocumentItem(
            document_id=r["document_id"],
            title=r["title"],
            file_name=r["file_name"],
            citation_count=int(r["citation_count"]),
            document_status=r["status"],
        )
        for r in trusted_rows
    ]
    knowledge = GovernanceKnowledgeMetrics(
        approved_knowledge_entries=approved_entries,
        deprecated_source_citations=deprecated_citations,
        most_trusted_documents=most_trusted,
    )

    topic_rows = conn.execute(
        """
        SELECT query, COUNT(*) AS count
        FROM review_items
        GROUP BY lower(trim(query))
        ORDER BY count DESC
        LIMIT 10
        """
    ).fetchall()
    most_reviewed = [TopSearchItem(query=r["query"], count=r["count"]) for r in topic_rows]

    success_rows = conn.execute(
        """
        SELECT
            lower(trim(query)) AS qkey,
            MIN(query) AS query,
            COUNT(*) AS searches,
            SUM(CASE WHEN results_count > 0 THEN 1 ELSE 0 END) AS successes
        FROM search_history
        GROUP BY qkey
        HAVING successes > 0
        ORDER BY (CAST(successes AS REAL) / COUNT(*)) DESC, searches DESC
        LIMIT 10
        """
    ).fetchall()
    search_success: List[SearchQualityItem] = []
    for row in success_rows:
        searches = int(row["searches"])
        successes = int(row["successes"] or 0)
        search_success.append(
            SearchQualityItem(
                query=row["query"],
                searches=searches,
                success_rate_pct=_pct(successes, searches),
            )
        )

    zero_rows = conn.execute(
        """
        SELECT query, COUNT(*) AS count
        FROM search_history
        WHERE results_count = 0
        GROUP BY lower(trim(query))
        ORDER BY count DESC
        LIMIT 10
        """
    ).fetchall()
    zero_result = [TopSearchItem(query=r["query"], count=r["count"]) for r in zero_rows]

    return GovernanceMetricsOut(
        review_quality=review_quality,
        validator_insights=validator_insights,
        knowledge=knowledge,
        most_reviewed_topics=most_reviewed,
        search_success_queries=search_success,
        zero_result_searches=zero_result,
    )
