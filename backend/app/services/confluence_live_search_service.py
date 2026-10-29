"""Live Confluence lookup during Search (PAT) for pages not in the local index."""

from __future__ import annotations

import re
import sqlite3
from typing import List, Optional, Set

from bs4 import BeautifulSoup

from backend.app.config import settings
from backend.app.integrations.confluence_client import (
    ConfluenceApiError,
    ConfluenceClient,
    ConfluenceConfigError,
    confluence_configured,
)
from backend.app.integrations.confluence_url import extract_page_id_from_query
from backend.app.schemas.models import ConfluenceLiveHit, SearchHit


def _cql_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _storage_to_snippet(storage_html: str, max_len: int = 420) -> str:
    if not storage_html.strip():
        return "No extractable body text on this page."
    soup = BeautifulSoup(storage_html, "html.parser")
    text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def _source_uri(page_id: str) -> str:
    return f"confluence://page/{page_id}"


def is_page_indexed_locally(conn: sqlite3.Connection, page_id: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM documents WHERE source_uri = ? LIMIT 1",
        (_source_uri(page_id),),
    ).fetchone()
    return row is not None


def _local_confluence_page_ids(hits: List[SearchHit]) -> Set[str]:
    ids: Set[str] = set()
    for hit in hits:
        if hit.confluence_page_id:
            ids.add(str(hit.confluence_page_id))
    return ids


def _page_to_live_hit(
    conn: sqlite3.Connection,
    client: ConfluenceClient,
    page: dict,
) -> Optional[ConfluenceLiveHit]:
    page_id = str(page.get("id", "")).strip()
    if not page_id:
        return None
    title = str(page.get("title") or f"Page {page_id}")
    storage = client.page_storage_html(page)
    snippet = _storage_to_snippet(storage)
    space_key = (page.get("space") or {}).get("key")
    return ConfluenceLiveHit(
        page_id=page_id,
        title=title,
        snippet=snippet,
        web_url=client.page_web_url(page),
        space_key=space_key,
        indexed_locally=is_page_indexed_locally(conn, page_id),
    )


def fetch_live_by_page_id(
    conn: sqlite3.Connection,
    client: ConfluenceClient,
    page_id: str,
) -> Optional[ConfluenceLiveHit]:
    page = client.get_page(page_id)
    return _page_to_live_hit(conn, client, page)


def search_live_by_title(
    conn: sqlite3.Connection,
    client: ConfluenceClient,
    query: str,
    *,
    limit: int = 5,
    skip_page_ids: Optional[Set[str]] = None,
) -> List[ConfluenceLiveHit]:
    q = query.strip()
    if len(q) < 2:
        return []
    escaped = _cql_escape(q)
    # Server/DC often ranks siteSearch better than strict title ~ for natural-language titles.
    cql_queries = [
        f'siteSearch ~ "{escaped}" AND type=page',
        f'type=page AND title ~ "{escaped}"',
        f'type=page AND text ~ "{escaped}"',
    ]
    skip = skip_page_ids or set()
    out: List[ConfluenceLiveHit] = []
    seen: Set[str] = set()

    for cql in cql_queries:
        if len(out) >= limit:
            break
        try:
            data = client.search_cql(cql, limit=limit * 2)
        except ConfluenceApiError:
            continue
        for page in data.get("results") or []:
            page_id = str(page.get("id", "")).strip()
            if not page_id or page_id in skip or page_id in seen:
                continue
            if is_page_indexed_locally(conn, page_id):
                continue
            hit = _page_to_live_hit(conn, client, page)
            if not hit:
                continue
            if not hit.snippet or hit.snippet.startswith("No extractable"):
                try:
                    full = client.get_page(page_id)
                    hit = _page_to_live_hit(conn, client, full)
                except ConfluenceApiError:
                    pass
            if hit:
                out.append(hit)
                seen.add(page_id)
            if len(out) >= limit:
                break
    return out


def confluence_live_for_search(
    conn: sqlite3.Connection,
    query: str,
    local_hits: List[SearchHit],
) -> tuple[List[ConfluenceLiveHit], Optional[str]]:
    if not settings.confluence_live_search_enabled:
        return [], None
    if not confluence_configured():
        return [], None

    try:
        client = ConfluenceClient()
    except ConfluenceConfigError as exc:
        return [], str(exc)

    live: List[ConfluenceLiveHit] = []
    seen: Set[str] = set()
    skip = _local_confluence_page_ids(local_hits)

    page_id = extract_page_id_from_query(query)
    if page_id and page_id not in skip:
        try:
            hit = fetch_live_by_page_id(conn, client, page_id)
            if hit:
                live.append(hit)
                seen.add(hit.page_id)
        except ConfluenceApiError as exc:
            return live, str(exc)

    title_query = query.strip()
    if page_id and title_query.isdigit():
        title_query = ""

    if title_query and len(title_query) >= 2:
        try:
            for hit in search_live_by_title(
                conn,
                client,
                title_query,
                limit=5,
                skip_page_ids=seen | skip,
            ):
                if hit.page_id in seen:
                    continue
                live.append(hit)
                seen.add(hit.page_id)
        except ConfluenceApiError as exc:
            if not live:
                return [], str(exc)
            return live, str(exc)

    return live, None
