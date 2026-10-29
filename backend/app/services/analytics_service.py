import sqlite3
from typing import List

from backend.app.schemas.models import (
    AnalyticsSummary,
    SearchQualityItem,
    SearchVolumeDay,
    TopDocumentItem,
    TopSearchItem,
)
from backend.app.services.confluence_sync_service import get_corpus_stats
from backend.app.services.health_service import get_knowledge_health


def get_summary(conn: sqlite3.Connection) -> AnalyticsSummary:
    top_searches = conn.execute(
        """
        SELECT query, COUNT(*) AS count
        FROM search_history
        GROUP BY lower(trim(query))
        ORDER BY count DESC
        LIMIT 10
        """
    ).fetchall()

    zero_result = conn.execute(
        """
        SELECT query, COUNT(*) AS count
        FROM search_history
        WHERE results_count = 0
        GROUP BY lower(trim(query))
        ORDER BY count DESC
        LIMIT 10
        """
    ).fetchall()

    top_documents = conn.execute(
        """
        SELECT id AS document_id, title, file_name, view_count
        FROM documents
        ORDER BY view_count DESC, upload_date DESC
        LIMIT 10
        """
    ).fetchall()

    total_searches = conn.execute("SELECT COUNT(*) AS c FROM search_history").fetchone()["c"]

    volume_rows = conn.execute(
        """
        SELECT
            date(timestamp) AS day,
            COUNT(*) AS searches,
            SUM(CASE WHEN results_count = 0 THEN 1 ELSE 0 END) AS zero_results
        FROM search_history
        GROUP BY date(timestamp)
        ORDER BY day DESC
        LIMIT 30
        """
    ).fetchall()
    search_volume_by_day = [
        SearchVolumeDay(
            day=str(row["day"]),
            searches=int(row["searches"]),
            zero_results=int(row["zero_results"] or 0),
        )
        for row in reversed(volume_rows)
    ]

    quality_rows = conn.execute(
        """
        SELECT
            lower(trim(sh.query)) AS qkey,
            MIN(sh.query) AS query,
            COUNT(*) AS searches,
            SUM(CASE WHEN sh.results_count > 0 THEN 1 ELSE 0 END) AS successes
        FROM search_history sh
        GROUP BY qkey
        ORDER BY searches DESC
        LIMIT 10
        """
    ).fetchall()

    search_quality: List[SearchQualityItem] = []
    for row in quality_rows:
        searches = int(row["searches"])
        successes = int(row["successes"] or 0)
        rate = (successes / searches * 100.0) if searches else 0.0
        click_row = conn.execute(
            """
            SELECT AVG(click_position) AS avg_pos
            FROM search_clicks
            WHERE lower(trim(query)) = ?
            """,
            (row["qkey"],),
        ).fetchone()
        avg_pos = click_row["avg_pos"]
        search_quality.append(
            SearchQualityItem(
                query=row["query"],
                searches=searches,
                success_rate_pct=round(rate, 1),
                avg_click_position=round(float(avg_pos), 2) if avg_pos is not None else None,
            )
        )

    return AnalyticsSummary(
        top_searches=[TopSearchItem(query=r["query"], count=r["count"]) for r in top_searches],
        top_documents=[
            TopDocumentItem(
                document_id=r["document_id"],
                title=r["title"],
                file_name=r["file_name"],
                view_count=r["view_count"],
            )
            for r in top_documents
        ],
        zero_result_searches=[
            TopSearchItem(query=r["query"], count=r["count"]) for r in zero_result
        ],
        total_searches=int(total_searches),
        search_quality=search_quality,
        search_volume_by_day=search_volume_by_day,
        knowledge_health=get_knowledge_health(conn),
        confluence=get_corpus_stats(conn),
    )
