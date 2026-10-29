import re
import sqlite3
from typing import List, Optional, Tuple

from backend.app.constants import STATUS_RANK_BOOST, DocumentStatus
from backend.app.config import settings
from backend.app.knowledge_path import build_knowledge_path
from backend.app.schemas.models import RelatedDocumentBrief, SearchHit, SearchResponse
from backend.app.schemas.search_filters import SearchFilters
from backend.app.services import document_service
from backend.app.services.confluence_live_search_service import confluence_live_for_search
from backend.app.services.governance_audit_service import log_event
from backend.app.services.hybrid_rerank_service import rerank_hits
from backend.app.integrations.confluence_url import parse_page_id_from_source_uri
from backend.app.services.synonym_service import (
    build_fts_query_from_expansion,
    build_fts_query_or_from_expansion,
    expand_query,
)
from backend.app.services.text_snippet import clean_search_snippet

_FTS_TOKEN = re.compile(r"[^\w]+", re.UNICODE)


def _build_fts_query(raw: str) -> str:
    """Legacy single-term AND query (used when synonym file missing)."""
    terms = [t for t in _FTS_TOKEN.split(raw.strip()) if len(t) >= 2]
    if not terms:
        terms = [raw.strip()] if raw.strip() else []
    if not terms:
        return ""
    return " AND ".join(f'"{t}"' for t in terms)


def _fts_query_for(raw: str) -> Tuple[str, List[str], List[str], List[List[str]]]:
    flat, groups, per_token = expand_query(raw)
    if per_token:
        fts = build_fts_query_from_expansion(per_token)
        if fts:
            return fts, flat, groups, per_token
    return _build_fts_query(raw), flat, groups, per_token


def _fts_relaxed_query(per_token: List[List[str]], raw: str) -> str:
    if per_token:
        relaxed = build_fts_query_or_from_expansion(per_token)
        if relaxed:
            return relaxed
    terms = [t for t in _FTS_TOKEN.split(raw.strip()) if len(t) >= 2]
    if not terms:
        return ""
    return " OR ".join(f'"{t}"' for t in terms)


def _status_boost(status: str) -> Tuple[float, List[str]]:
    try:
        st = DocumentStatus(status)
    except ValueError:
        st = DocumentStatus.ACTIVE
    boost = STATUS_RANK_BOOST.get(st, 0.0)
    reasons: List[str] = []
    if boost > 0:
        reasons.append(f"+ {st.value.title()} document")
    elif boost < 0:
        reasons.append(f"- {st.value.title()} document (deprioritized)")
    return boost, reasons


def _filter_clauses(filters: Optional[SearchFilters]) -> Tuple[str, List[object]]:
    if filters is None:
        return "", []
    parts: List[str] = []
    params: List[object] = []
    if filters.status:
        parts.append("d.status = ?")
        params.append(filters.status.lower())
    if filters.tag:
        parts.append("(d.tags_json LIKE ? OR d.tags_json LIKE ?)")
        tag = filters.tag.strip().lower()
        params.extend([f'%"{tag}"%', f"%{tag}%"])
    if filters.file_type:
        parts.append("d.file_type = ?")
        params.append(filters.file_type.lower().lstrip("."))
    if filters.version_label:
        parts.append("d.version_label = ?")
        params.append(filters.version_label.strip())
    if not parts:
        return "", []
    return " AND " + " AND ".join(parts), params


def search(
    conn: sqlite3.Connection,
    query: str,
    limit: int = 25,
    filters: Optional[SearchFilters] = None,
) -> SearchResponse:
    fts_query, expanded_terms, synonym_groups, per_token = _fts_query_for(query)
    filter_sql, filter_params = _filter_clauses(filters)
    filters_applied = filters.model_dump(exclude_none=True) if filters else {}
    relaxed_match = False

    if not fts_query:
        live_hits, live_err = confluence_live_for_search(conn, query, [])
        effective = len(live_hits)
        cur = conn.execute(
            "INSERT INTO search_history (query, results_count) VALUES (?, ?)",
            (query.strip(), effective),
        )
        return SearchResponse(
            search_id=cur.lastrowid,
            query=query,
            expanded_terms=expanded_terms,
            synonym_groups=synonym_groups,
            results_count=effective,
            results=[],
            filters_applied=filters_applied,
            confluence_live=live_hits,
            confluence_live_error=live_err,
        )

    sql = f"""
        SELECT
            c.id AS chunk_id,
            c.document_id,
            c.page_number,
            c.chunk_index,
            d.title AS document_title,
            d.file_name,
            d.source_type,
            d.source_uri,
            d.source_link,
            d.status,
            d.view_count,
            d.upload_date,
            d.related_document_ids_json,
            c.section,
            snippet(chunks_fts, 0, '[[', ']]', '…', 48) AS snippet,
            bm25(chunks_fts) AS bm25_score
        FROM chunks_fts
        JOIN document_chunks c ON c.id = chunks_fts.chunk_id
        JOIN documents d ON d.id = c.document_id
        WHERE chunks_fts MATCH ?
        {filter_sql}
        LIMIT ?
    """
    params: List[object] = [fts_query, *filter_params, limit * 3]
    try:
        rows = conn.execute(sql, params).fetchall()
    except sqlite3.OperationalError:
        rows = []

    if not rows and per_token and len(per_token) > 1:
        relaxed = _fts_relaxed_query(per_token, query)
        if relaxed and relaxed != fts_query:
            relaxed_match = True
            try:
                rows = conn.execute(sql, [relaxed, *filter_params, limit * 3]).fetchall()
            except sqlite3.OperationalError:
                rows = []

    scored: List[SearchHit] = []
    for r in rows:
        raw_bm25 = float(r["bm25_score"])
        base = max(0.0, min(70.0, 70.0 / (1.0 + abs(raw_bm25))))
        reasons = ["+ Keyword match (FTS5)"]
        if relaxed_match:
            reasons.append("+ Relaxed match (any search word)")
        if synonym_groups:
            reasons.append(f"+ Synonym expansion ({', '.join(synonym_groups)})")

        status_boost, status_reasons = _status_boost(r["status"])
        reasons.extend(status_reasons)

        views = int(r["view_count"] or 0)
        if views >= 5:
            popularity = min(10.0, views / 10.0)
            base += popularity
            reasons.append("+ Frequently accessed")

        base += 5.0
        reasons.append("+ Recent upload boost")

        final_score = max(0.0, min(100.0, base + status_boost))

        related_ids = document_service._parse_id_list(r["related_document_ids_json"])
        related = document_service._related_briefs(conn, related_ids[:5])

        try:
            doc_status = DocumentStatus(r["status"])
        except ValueError:
            doc_status = DocumentStatus.ACTIVE

        source_uri = r["source_uri"]
        scored.append(
            SearchHit(
                chunk_id=r["chunk_id"],
                document_id=r["document_id"],
                document_title=r["document_title"],
                file_name=r["file_name"],
                page_number=r["page_number"],
                chunk_index=r["chunk_index"],
                snippet=clean_search_snippet(r["snippet"] or ""),
                score=round(final_score, 1),
                document_status=doc_status,
                ranking_reasons=reasons,
                related_documents=related,
                knowledge_path=build_knowledge_path(
                    source_type=r["source_type"],
                    source_uri=source_uri,
                    file_name=r["file_name"],
                    document_id=r["document_id"],
                    page_number=r["page_number"],
                    chunk_index=r["chunk_index"],
                    chunk_id=r["chunk_id"],
                    section=r["section"],
                ),
                source_link=r["source_link"],
                source_type=r["source_type"],
                confluence_page_id=parse_page_id_from_source_uri(source_uri),
            )
        )

    scored.sort(key=lambda h: h.score, reverse=True)
    hits = scored[:limit]
    if settings.hybrid_rerank_enabled:
        hits = rerank_hits(query, hits)

    live_hits, live_err = confluence_live_for_search(conn, query, hits)
    effective_results = len(hits) + len(live_hits)

    cur = conn.execute(
        "INSERT INTO search_history (query, results_count) VALUES (?, ?)",
        (query.strip(), effective_results),
    )
    log_event(
        conn,
        event_type="search.executed",
        resource_type="search",
        resource_id=str(cur.lastrowid),
        detail={
            "query": query.strip(),
            "local_results": len(hits),
            "confluence_live": len(live_hits),
            "confluence_live_error": live_err,
        },
    )
    return SearchResponse(
        search_id=cur.lastrowid,
        query=query,
        expanded_terms=expanded_terms,
        synonym_groups=synonym_groups,
        results_count=len(hits),
        results=hits,
        filters_applied=filters_applied,
        confluence_live=live_hits,
        confluence_live_error=live_err,
    )


def record_click(
    conn: sqlite3.Connection,
    query: str,
    chunk_id: int,
    click_position: int,
    search_id: Optional[int] = None,
) -> None:
    conn.execute(
        """
        INSERT INTO search_clicks (search_history_id, query, chunk_id, click_position)
        VALUES (?, ?, ?, ?)
        """,
        (search_id, query, chunk_id, click_position),
    )
