import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from backend.app.config import settings
from backend.app.onboarding_days import day_sort_key, item_sort_key, sort_day_labels
from backend.app.integrations.confluence_url import parse_page_id_from_url
from backend.app.schemas.onboarding import (
    OnboardingConfluenceSyncResult,
    OnboardingImportResult,
    OnboardingItem,
    OnboardingLinkHealthItem,
    OnboardingLinkHealthResponse,
    OnboardingListResponse,
    OnboardingMeta,
    SuggestedAskItem,
    SuggestedAsksResponse,
)
from backend.app.services import document_service

_URL_RE = re.compile(r"https?://[^\s\]\)\"'>]+", re.IGNORECASE)

_COLUMN_ALIASES: Dict[str, Tuple[str, ...]] = {
    "day_label": ("day", "day #", "day#", "timeline", "week", "phase", "sprint"),
    "title": (
        "topic",
        "task",
        "item",
        "activity",
        "module",
        "subject",
        "name",
        "title",
        "deliverable",
        "kt item",
        "onboarding step",
    ),
    "description": ("description", "notes", "details", "comments", "summary", "what to do"),
    "owner": ("owner", "poc", "contact", "assignee", "sme", "trainer", "lead"),
    "confluence_url": (
        "confluence",
        "confluence link",
        "confluence url",
        "wiki",
        "wiki link",
        "page",
        "confluence page",
        "documentation link",
    ),
    "ticket_url": (
        "jira",
        "ticket",
        "servicenow",
        "snow",
        "request",
        "access request",
        "ticket link",
        "raise ticket",
        "service catalog",
    ),
    "access_group": (
        "access",
        "group",
        "ad group",
        "global group",
        "entitlement",
        "role",
        "security group",
        "distribution list",
        "dl",
        "permissions",
    ),
    "category": ("category", "type", "area", "bucket", "theme"),
}


def _norm_header(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def _cell_str(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value).strip()


def _first_url(text: str) -> Optional[str]:
    if not text:
        return None
    m = _URL_RE.search(text)
    return m.group(0).rstrip(".,;") if m else None


def _map_columns(columns: List[str]) -> Dict[str, str]:
    normalized = {_norm_header(c): c for c in columns}
    mapped: Dict[str, str] = {}
    for field, aliases in _COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in normalized:
                mapped[field] = normalized[alias]
                break
    return mapped


def _infer_category(
    mapped: Dict[str, str],
    row: Dict[str, Any],
    confluence_url: Optional[str],
    ticket_url: Optional[str],
    access_group: Optional[str],
) -> str:
    if "category" in mapped:
        raw = _cell_str(row.get(mapped["category"]))
        if raw:
            lower = raw.lower()
            if "confluence" in lower or "wiki" in lower:
                return "confluence"
            if "ticket" in lower or "jira" in lower or "access" in lower:
                return "ticket" if "ticket" in lower or "jira" in lower else "access"
            if "access" in lower or "group" in lower:
                return "access"
            if "doc" in lower:
                return "document"
            return lower.replace(" ", "_")[:40] or "general"

    if access_group:
        return "access"
    if confluence_url:
        return "confluence"
    if ticket_url:
        return "ticket"
    title = _cell_str(row.get(mapped.get("title", ""), ""))
    lower = title.lower()
    if any(k in lower for k in ("confluence", "wiki", "kt page")):
        return "confluence"
    if any(k in lower for k in ("jira", "ticket", "servicenow", "snow", "request access")):
        return "ticket"
    if any(k in lower for k in ("ad group", "global group", "entitlement", "access")):
        return "access"
    return "general"


def _row_to_item(
    sheet_name: str,
    row_index: int,
    row: Dict[str, Any],
    mapped: Dict[str, str],
    source_file: str,
) -> Optional[OnboardingItem]:
    title_col = mapped.get("title")
    if not title_col:
        # Use first non-empty column as title
        for key, val in row.items():
            text = _cell_str(val)
            if text and _norm_header(key) not in ("nan",):
                title_col = key
                break
    if not title_col:
        return None

    title = _cell_str(row.get(title_col))
    if not title:
        return None

    description = _cell_str(row.get(mapped.get("description", ""), "")) if mapped.get("description") else ""
    owner = _cell_str(row.get(mapped.get("owner", ""), "")) if mapped.get("owner") else ""
    day_label = _cell_str(row.get(mapped.get("day_label", ""), "")) if mapped.get("day_label") else ""

    confluence_url = None
    ticket_url = None
    access_group = None

    if mapped.get("confluence_url"):
        confluence_url = _first_url(_cell_str(row.get(mapped["confluence_url"])))
    if mapped.get("ticket_url"):
        ticket_url = _first_url(_cell_str(row.get(mapped["ticket_url"])))
    if mapped.get("access_group"):
        access_group = _cell_str(row.get(mapped["access_group"]))

    # Scan all cells for URLs and group names we might have missed
    for key, val in row.items():
        text = _cell_str(val)
        if not text:
            continue
        url = _first_url(text)
        key_l = _norm_header(key)
        if url and not confluence_url and any(x in key_l for x in ("confluence", "wiki", "page", "doc")):
            confluence_url = url
        elif url and not ticket_url and any(x in key_l for x in ("jira", "ticket", "snow", "request", "catalog")):
            ticket_url = url
        elif url and not confluence_url and "atlassian" in url.lower():
            confluence_url = url
        elif url and not ticket_url:
            ticket_url = url
        if not access_group and any(x in key_l for x in ("group", "access", "entitlement", "role")):
            if not url:
                access_group = text

    if not description:
        extras: List[str] = []
        for key, val in row.items():
            if key in (title_col, *mapped.values()):
                continue
            text = _cell_str(val)
            if text and text not in (confluence_url or "", ticket_url or "", access_group or ""):
                extras.append(f"{key}: {text}")
        if extras:
            description = "\n".join(extras[:6])

    category = _infer_category(mapped, row, confluence_url, ticket_url, access_group)

    tags = ["onboarding", "kt"]
    if sheet_name:
        tags.append(sheet_name.lower().replace(" ", "-")[:40])
    if category:
        tags.append(category)

    return OnboardingItem(
        id=0,
        sheet_name=sheet_name,
        row_index=row_index,
        day_label=day_label or None,
        category=category,
        title=title,
        description=description or None,
        owner=owner or None,
        confluence_url=confluence_url,
        ticket_url=ticket_url,
        access_group=access_group,
        tags=tags,
        source_file=source_file,
        updated_at=datetime.utcnow(),
    )


def _parse_xlsx(path: Path) -> List[OnboardingItem]:
    xl = pd.ExcelFile(path)
    items: List[OnboardingItem] = []
    source_name = path.name
    for sheet in xl.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet, dtype=str)
        if df.empty:
            continue
        df = df.dropna(how="all")
        mapped = _map_columns([str(c) for c in df.columns])
        for idx, row in df.iterrows():
            row_dict = {str(k): row[k] for k in df.columns}
            item = _row_to_item(sheet, int(idx) + 2, row_dict, mapped, source_name)
            if item:
                items.append(item)
    return items


def _ensure_table(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS onboarding_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sheet_name TEXT NOT NULL,
            row_index INTEGER NOT NULL,
            day_label TEXT,
            category TEXT NOT NULL DEFAULT 'general',
            title TEXT NOT NULL,
            description TEXT,
            owner TEXT,
            confluence_url TEXT,
            ticket_url TEXT,
            access_group TEXT,
            tags_json TEXT NOT NULL DEFAULT '[]',
            raw_json TEXT,
            source_file TEXT,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_onboarding_category ON onboarding_items(category)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_onboarding_day ON onboarding_items(day_label)"
    )


def import_xlsx(conn, path: Path) -> OnboardingImportResult:
    _ensure_table(conn)
    if not path.is_file():
        raise FileNotFoundError(f"Onboarding spreadsheet not found: {path}")

    parsed = _parse_xlsx(path)
    conn.execute("DELETE FROM onboarding_items")
    now = datetime.utcnow().isoformat()
    for item in parsed:
        conn.execute(
            """
            INSERT INTO onboarding_items (
                sheet_name, row_index, day_label, category, title, description,
                owner, confluence_url, ticket_url, access_group, tags_json,
                source_file, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.sheet_name,
                item.row_index,
                item.day_label,
                item.category,
                item.title,
                item.description,
                item.owner,
                item.confluence_url,
                item.ticket_url,
                item.access_group,
                json.dumps(item.tags),
                item.source_file,
                now,
            ),
        )

    doc_id = _sync_search_corpus(conn, path, parsed)
    return OnboardingImportResult(
        source_file=path.name,
        sheets_processed=len({i.sheet_name for i in parsed}) if parsed else 0,
        rows_imported=len(parsed),
        search_document_id=doc_id,
        message=(
            f"Imported {len(parsed)} onboarding row(s) from {path.name}. "
            "Use the New hire guide page to browse; Search indexes the generated guide."
        ),
    )


def _sync_search_corpus(conn, path: Path, items: List[OnboardingItem]) -> Optional[int]:
    if not items:
        return None

    settings.onboarding_dir.mkdir(parents=True, exist_ok=True)
    md_path = settings.onboarding_dir / "onboarding_search_corpus.md"
    lines = [
        "# Personalization KT — 10-day onboarding guide",
        "",
        f"Source: `{path.name}` (imported for NexusSearch navigation and search).",
        "",
        "Use this document to find Confluence pages, access groups, tickets, and day-by-day tasks.",
        "",
    ]
    by_day: Dict[str, List[OnboardingItem]] = {}
    for item in items:
        key = item.day_label or "General"
        by_day.setdefault(key, []).append(item)

    for day in sort_day_labels(list(by_day.keys())):
        lines.append(f"## {day}")
        lines.append("")
        for item in by_day[day]:
            lines.append(f"### {item.title}")
            if item.category:
                lines.append(f"- Category: {item.category}")
            if item.owner:
                lines.append(f"- Owner: {item.owner}")
            if item.access_group:
                lines.append(f"- Access / global group: {item.access_group}")
            if item.confluence_url:
                lines.append(f"- Confluence: {item.confluence_url}")
            if item.ticket_url:
                lines.append(f"- Ticket / request: {item.ticket_url}")
            if item.description:
                lines.append("")
                lines.append(item.description)
            lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    data = md_path.read_bytes()
    existing = conn.execute(
        "SELECT id FROM documents WHERE file_name = ? ORDER BY id DESC LIMIT 1",
        (md_path.name,),
    ).fetchone()
    if existing:
        conn.execute("DELETE FROM document_chunks WHERE document_id = ?", (existing["id"],))
        conn.execute("DELETE FROM documents WHERE id = ?", (existing["id"],))

    summary, _ = document_service.ingest_upload(
        conn,
        md_path.name,
        data,
        title="Personalization KT onboarding (10-day)",
        tags=["onboarding", "kt", "personalization", "new-hire"],
        source_type="onboarding",
        source_uri=str(path),
    )
    return summary.id


def _row_to_schema(row) -> OnboardingItem:
    tags = json.loads(row["tags_json"] or "[]")
    return OnboardingItem(
        id=row["id"],
        sheet_name=row["sheet_name"],
        row_index=row["row_index"],
        day_label=row["day_label"],
        category=row["category"],
        title=row["title"],
        description=row["description"],
        owner=row["owner"],
        confluence_url=row["confluence_url"],
        ticket_url=row["ticket_url"],
        access_group=row["access_group"],
        tags=tags,
        source_file=row["source_file"],
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def list_items(
    conn,
    q: Optional[str] = None,
    category: Optional[str] = None,
    day: Optional[str] = None,
    limit: int = 500,
) -> OnboardingListResponse:
    _ensure_table(conn)
    clauses = ["1=1"]
    params: List[Any] = []
    if category:
        clauses.append("category = ?")
        params.append(category)
    if day:
        clauses.append("day_label = ?")
        params.append(day)
    if q:
        clauses.append(
            "(title LIKE ? OR description LIKE ? OR access_group LIKE ? OR owner LIKE ?)"
        )
        like = f"%{q.strip()}%"
        params.extend([like, like, like, like])

    where = " AND ".join(clauses)
    rows = conn.execute(
        f"""
        SELECT * FROM onboarding_items
        WHERE {where}
        ORDER BY
            CASE WHEN day_label IS NULL OR day_label = '' THEN 1 ELSE 0 END,
            day_label,
            sheet_name,
            row_index
        LIMIT ?
        """,
        (*params, limit),
    ).fetchall()
    items = [_row_to_schema(r) for r in rows]
    items.sort(
        key=lambda i: item_sort_key(i.day_label, i.title, i.sheet_name, i.row_index)
    )
    total = conn.execute(
        f"SELECT COUNT(*) AS c FROM onboarding_items WHERE {where}",
        params,
    ).fetchone()["c"]
    cats = [
        r["category"]
        for r in conn.execute(
            "SELECT DISTINCT category FROM onboarding_items ORDER BY category"
        ).fetchall()
    ]
    raw_days = [
        r["day_label"]
        for r in conn.execute(
            """
            SELECT DISTINCT day_label FROM onboarding_items
            WHERE day_label IS NOT NULL AND day_label != ''
            """
        ).fetchall()
    ]
    days = sort_day_labels(raw_days)
    meta = conn.execute(
        "SELECT source_file, MAX(updated_at) AS updated_at FROM onboarding_items"
    ).fetchone()
    last = None
    if meta and meta["updated_at"]:
        last = datetime.fromisoformat(meta["updated_at"])
    return OnboardingListResponse(
        total=total,
        items=items,
        categories=cats,
        days=days,
        source_file=meta["source_file"] if meta else None,
        last_import_at=last,
    )


def get_meta(conn) -> OnboardingMeta:
    _ensure_table(conn)
    total = conn.execute("SELECT COUNT(*) AS c FROM onboarding_items").fetchone()["c"]
    meta_row = conn.execute(
        "SELECT source_file, MAX(updated_at) AS updated_at FROM onboarding_items"
    ).fetchone()
    cats = [
        r["category"]
        for r in conn.execute(
            "SELECT DISTINCT category FROM onboarding_items ORDER BY category"
        ).fetchall()
    ]
    raw_days = [
        r["day_label"]
        for r in conn.execute(
            """
            SELECT DISTINCT day_label FROM onboarding_items
            WHERE day_label IS NOT NULL AND day_label != ''
            """
        ).fetchall()
    ]
    days = sort_day_labels(raw_days)
    last = None
    if meta_row and meta_row["updated_at"]:
        last = datetime.fromisoformat(meta_row["updated_at"])
    return OnboardingMeta(
        total=total,
        source_file=meta_row["source_file"] if meta_row else None,
        last_import_at=last,
        categories=cats,
        days=days,
    )


def default_xlsx_path() -> Path:
    return settings.onboarding_dir / settings.onboarding_xlsx_filename


def suggested_asks(conn, limit: int = 12) -> SuggestedAsksResponse:
    _ensure_table(conn)
    rows = conn.execute(
        """
        SELECT title, category, access_group, description
        FROM onboarding_items
        ORDER BY row_index ASC
        LIMIT ?
        """,
        (limit * 3,),
    ).fetchall()
    items: List[SuggestedAskItem] = []
    seen: set[str] = set()
    for row in rows:
        title = str(row["title"] or "").strip()
        if not title:
            continue
        group = (row["access_group"] or "").strip()
        category = (row["category"] or "").strip() or None
        if group:
            q = f"How do I get access to {group}?"
        elif category == "confluence":
            q = f"Where is the Confluence page for {title}?"
        elif category == "ticket":
            q = f"How do I raise a ticket for {title}?"
        else:
            q = f"What should I know about {title}?"
        key = q.lower()
        if key in seen:
            continue
        seen.add(key)
        items.append(SuggestedAskItem(question=q, source_title=title, category=category))
        if len(items) >= limit:
            break
    if not items:
        items = [
            SuggestedAskItem(question="How do I get Databricks access?", category="access"),
            SuggestedAskItem(question="What is the P360 integration guide?", category="confluence"),
            SuggestedAskItem(question="How does governed ask and review work?", category="general"),
        ]
    return SuggestedAsksResponse(items=items)


def collect_confluence_page_ids(conn) -> List[str]:
    _ensure_table(conn)
    rows = conn.execute(
        """
        SELECT confluence_url FROM onboarding_items
        WHERE confluence_url IS NOT NULL AND trim(confluence_url) != ''
        """
    ).fetchall()
    ids: List[str] = []
    seen: set[str] = set()
    for row in rows:
        page_id = parse_page_id_from_url(row["confluence_url"])
        if page_id and page_id not in seen:
            seen.add(page_id)
            ids.append(page_id)
    return ids


def link_health(conn) -> OnboardingLinkHealthResponse:
    _ensure_table(conn)
    rows = conn.execute(
        """
        SELECT id, title, confluence_url FROM onboarding_items
        WHERE confluence_url IS NOT NULL AND trim(confluence_url) != ''
        ORDER BY id
        """
    ).fetchall()
    items: List[OnboardingLinkHealthItem] = []
    parseable = 0
    for row in rows:
        url = row["confluence_url"]
        page_id = parse_page_id_from_url(url)
        issue = None
        if not page_id:
            issue = "Could not parse page ID from URL"
        else:
            parseable += 1
        items.append(
            OnboardingLinkHealthItem(
                onboarding_id=int(row["id"]),
                title=row["title"],
                confluence_url=url,
                page_id=page_id,
                issue=issue,
            )
        )
    return OnboardingLinkHealthResponse(
        total_with_url=len(items),
        parseable=parseable,
        items=items,
    )


def sync_guide_confluence_pages(
    conn,
    tags: Optional[List[str]] = None,
) -> OnboardingConfluenceSyncResult:
    from backend.app.services.confluence_sync_service import sync_pages

    page_ids = collect_confluence_page_ids(conn)
    if not page_ids:
        return OnboardingConfluenceSyncResult(
            requested=0,
            indexed=0,
            message="No Confluence URLs with parseable page IDs in the guide.",
        )
    tag_list = tags or ["confluence", "onboarding"]
    result = sync_pages(conn, page_ids=page_ids, tags=tag_list, replace_existing=True)
    return OnboardingConfluenceSyncResult(
        requested=result.requested,
        indexed=result.indexed,
        errors=list(result.errors or []),
        message=f"Indexed {result.indexed} / {result.requested} pages from the new hire guide.",
    )
