from backend.app.services.hybrid_rerank_service import rerank_hits
from backend.app.services.knowledge_integrity_service import content_hash
from backend.app.schemas.models import DocumentStatus, SearchHit


def _hit(title: str, snippet: str, score: float) -> SearchHit:
    return SearchHit(
        chunk_id=1,
        document_id=1,
        document_title=title,
        file_name="a.html",
        page_number=1,
        chunk_index=0,
        snippet=snippet,
        score=score,
        document_status=DocumentStatus.ACTIVE,
    )


def test_hybrid_rerank_boosts_title_match():
    hits = [
        _hit("AFP Analytics", "network platform vpc", 60.0),
        _hit("Digital Marketing Platform Guide", "overview", 58.0),
    ]
    out = rerank_hits("Digital Marketing Platform", hits)
    assert out[0].document_title.startswith("Digital Marketing")


def test_content_hash_stable():
    h1 = content_hash("hello world")
    h2 = content_hash("hello world")
    assert h1 == h2
    assert len(h1) == 64


def test_dedupe_zero_result_queries_keeps_latest():
    import sqlite3

    from backend.app.db.schema import SCHEMA_SQL
    from backend.app.services.search_history_service import dedupe_zero_result_queries

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)
    for q in ("Direct LLM all models 20x", "direct llm all models 20x", "APDPA"):
        conn.execute(
            "INSERT INTO search_history (query, results_count) VALUES (?, 0)",
            (q,),
        )
    conn.execute(
        "INSERT INTO search_history (query, results_count) VALUES (?, 0)",
        ("1782008215",),
    )
    conn.execute(
        "INSERT INTO search_history (query, results_count) VALUES (?, 0)",
        ("1782008215",),
    )
    out = dedupe_zero_result_queries(conn)
    assert out["rows_deleted"] == 2
    assert out["patterns_collapsed"] == 2
    remaining = conn.execute(
        "SELECT lower(trim(query)) AS q, COUNT(*) AS c FROM search_history WHERE results_count=0 GROUP BY q"
    ).fetchall()
    assert all(r["c"] == 1 for r in remaining)
