from __future__ import annotations

import sqlite3
from typing import List, Optional, Tuple

from backend.app.integrations.confluence_client import (
    ConfluenceApiError,
    ConfluenceClient,
    ConfluenceConfigError,
    confluence_configured,
)
from backend.app.schemas.confluence import (
    ConfluencePageSyncResult,
    ConfluencePagesSyncResult,
    ConfluenceSpaceOut,
    ConfluenceSpaceValidate,
    ConfluenceStatus,
    ConfluenceSyncResult,
)
from backend.app.schemas.models import ConfluenceCorpusStats
from backend.app.services import document_service


def assert_sync_allowed() -> None:
    from backend.app.config import settings

    if not settings.confluence_sync_enabled:
        raise ConfluenceConfigError(
            "Confluence sync is disabled (KNOWLEDGEPILOT_CONFLUENCE_SYNC_ENABLED=false). "
            "Status and browse APIs remain available."
        )


def get_corpus_stats(conn: sqlite3.Connection) -> ConfluenceCorpusStats:
    row = conn.execute(
        """
        SELECT COUNT(*) AS c, MAX(upload_date) AS last_at
        FROM documents
        WHERE source_type = 'confluence'
        """
    ).fetchone()
    last = row["last_at"]
    return ConfluenceCorpusStats(
        pages_indexed=int(row["c"] or 0),
        last_synced_at=str(last) if last else None,
    )


def get_status() -> ConfluenceStatus:
    from backend.app.config import settings

    if not settings.confluence_enabled:
        return ConfluenceStatus(
            enabled=False,
            configured=False,
            message="Confluence API disabled. Set KNOWLEDGEPILOT_CONFLUENCE_ENABLED=true to enable.",
        )
    configured = confluence_configured()
    if not configured:
        return ConfluenceStatus(
            enabled=True,
            configured=False,
            base_url=settings.confluence_base_url,
            message="Missing base URL, email, or API token in environment / .env",
        )
    try:
        client = ConfluenceClient()
        user = client.ping()
        return ConfluenceStatus(
            enabled=True,
            configured=True,
            base_url=client.base_url,
            reachable=True,
            user_display_name=user.get("displayName") or user.get("username"),
            message="Connected to Confluence.",
        )
    except (ConfluenceConfigError, ConfluenceApiError) as exc:
        return ConfluenceStatus(
            enabled=True,
            configured=True,
            base_url=settings.confluence_base_url,
            reachable=False,
            message=str(exc),
        )


def validate_space(space_key: str) -> ConfluenceSpaceValidate:
    client = ConfluenceClient()
    data = client.get_space(space_key)
    return ConfluenceSpaceValidate(
        key=str(data.get("key", space_key)),
        name=str(data.get("name", space_key)),
        type=data.get("type"),
        found=True,
    )


def sync_page(
    conn,
    page_id: str,
    tags: Optional[List[str]] = None,
    replace_existing: bool = True,
) -> ConfluencePageSyncResult:
    assert_sync_allowed()
    client = ConfluenceClient()
    page = client.get_page(page_id)
    pid = str(page.get("id", page_id))
    title = str(page.get("title") or f"Page {pid}")
    storage = client.page_storage_html(page)
    if not storage.strip():
        return ConfluencePageSyncResult(
            page_id=pid,
            title=title,
            space_key=(page.get("space") or {}).get("key"),
            indexed=False,
            message="Page has no extractable body text.",
        )
    web_url = client.page_web_url(page)
    space_key = (page.get("space") or {}).get("key")
    tag_list = list(tags or []) + ["confluence"]
    if space_key:
        tag_list.append(f"space:{space_key}")
    uri = _source_uri(pid)
    if replace_existing:
        document_service.delete_by_source_uri(conn, uri)
    _ingest_confluence_page(
        conn,
        page_id=pid,
        title=title,
        storage_html=storage,
        source_uri=uri,
        source_link=web_url,
        tags=tag_list,
    )
    return ConfluencePageSyncResult(
        page_id=pid,
        title=title,
        space_key=space_key,
        indexed=True,
        message=f"Indexed page '{title}'.",
    )


def sync_pages(
    conn,
    page_ids: List[str],
    tags: Optional[List[str]] = None,
    replace_existing: bool = True,
) -> ConfluencePagesSyncResult:
    assert_sync_allowed()
    seen: set[str] = set()
    ordered: List[str] = []
    for raw in page_ids:
        pid = str(raw).strip()
        if pid and pid not in seen:
            seen.add(pid)
            ordered.append(pid)

    results: List[ConfluencePageSyncResult] = []
    errors: List[str] = []
    indexed = 0
    skipped = 0
    for pid in ordered:
        try:
            result = sync_page(conn, pid, tags=tags, replace_existing=replace_existing)
            results.append(result)
            if result.indexed:
                indexed += 1
            else:
                skipped += 1
        except (ConfluenceApiError, ConfluenceConfigError) as exc:
            errors.append(f"{pid}: {exc}")
            skipped += 1
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{pid}: {exc}")
            skipped += 1

    return ConfluencePagesSyncResult(
        requested=len(ordered),
        indexed=indexed,
        skipped=skipped,
        results=results,
        errors=errors,
    )


def sync_descendants(
    conn,
    parent_page_id: str,
    max_pages: int = 50,
    include_parent: bool = True,
    tags: Optional[List[str]] = None,
    replace_existing: bool = True,
) -> ConfluencePagesSyncResult:
    assert_sync_allowed()
    client = ConfluenceClient()
    ids = client.collect_descendant_page_ids(
        parent_page_id,
        max_pages=max_pages,
        include_root=include_parent,
    )
    return sync_pages(conn, ids, tags=tags, replace_existing=replace_existing)


def list_spaces(limit: int = 500) -> List[ConfluenceSpaceOut]:
    client = ConfluenceClient()
    spaces = client.list_spaces(limit=limit)
    return [
        ConfluenceSpaceOut(key=s.get("key", ""), name=s.get("name", ""), type=s.get("type"))
        for s in spaces
        if s.get("key")
    ]


def _source_uri(page_id: str) -> str:
    return f"confluence://page/{page_id}"


def sync_space(
    conn,
    space_key: str,
    limit: int = 25,
    tags: Optional[List[str]] = None,
    replace_existing: bool = True,
) -> ConfluenceSyncResult:
    assert_sync_allowed()
    client = ConfluenceClient()
    data = client.list_pages(space_key=space_key, limit=limit)
    pages = list(data.get("results") or [])
    tag_list = list(tags or []) + ["confluence", f"space:{space_key}"]

    indexed = 0
    skipped = 0
    errors: List[str] = []

    for page in pages:
        page_id = str(page.get("id", ""))
        title = str(page.get("title") or f"Page {page_id}")
        if not page_id:
            skipped += 1
            continue
        storage = client.page_storage_html(page)
        if not storage.strip():
            skipped += 1
            errors.append(f"{title}: empty body")
            continue
        web_url = client.page_web_url(page)
        uri = _source_uri(page_id)
        try:
            if replace_existing:
                document_service.delete_by_source_uri(conn, uri)
            _ingest_confluence_page(
                conn,
                page_id=page_id,
                title=title,
                storage_html=storage,
                source_uri=uri,
                source_link=web_url,
                tags=tag_list,
            )
            indexed += 1
        except Exception as exc:
            errors.append(f"{title}: {exc}")

    return ConfluenceSyncResult(
        space_key=space_key,
        pages_fetched=len(pages),
        pages_indexed=indexed,
        skipped=skipped,
        errors=errors,
    )


def _ingest_confluence_page(
    conn,
    *,
    page_id: str,
    title: str,
    storage_html: str,
    source_uri: str,
    source_link: Optional[str],
    tags: List[str],
) -> Tuple[int, int]:
    wrapped = f"<html><body>{storage_html}</body></html>"
    safe_name = f"confluence-{page_id}.html"
    doc, chunk_count = document_service.ingest_upload(
        conn,
        safe_name,
        wrapped.encode("utf-8"),
        title=title,
        tags=tags,
        source_type="confluence",
        source_uri=source_uri,
    )
    if source_link and not doc.source_link:
        conn.execute(
            "UPDATE documents SET source_link = ? WHERE id = ?",
            (source_link, doc.id),
        )
    return doc.id, chunk_count
