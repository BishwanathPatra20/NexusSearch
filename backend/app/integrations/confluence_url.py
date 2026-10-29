"""Parse Confluence page IDs from URLs and internal source URIs."""

from __future__ import annotations

import re
from typing import Optional
from urllib.parse import parse_qs, urlparse

_PAGE_ID_RE = re.compile(r"(?:pageId=|/pages/)(\d+)", re.IGNORECASE)
_SOURCE_URI_RE = re.compile(r"^confluence://page/(\d+)$", re.IGNORECASE)


def parse_page_id_from_url(url: Optional[str]) -> Optional[str]:
    if not url or not str(url).strip():
        return None
    text = str(url).strip()
    m = _PAGE_ID_RE.search(text)
    if m:
        return m.group(1)
    parsed = urlparse(text)
    qs = parse_qs(parsed.query)
    for key in ("pageId", "pageid"):
        if key in qs and qs[key]:
            return str(qs[key][0]).strip()
    return None


def parse_page_id_from_source_uri(source_uri: Optional[str]) -> Optional[str]:
    if not source_uri:
        return None
    m = _SOURCE_URI_RE.match(source_uri.strip())
    return m.group(1) if m else None


def extract_page_id_from_query(query: str) -> Optional[str]:
    """Detect a Confluence page id in a search query (bare id, URL, or pageId=)."""
    raw = (query or "").strip()
    if not raw:
        return None
    if raw.isdigit():
        return raw
    from_url = parse_page_id_from_url(raw)
    if from_url:
        return from_url
    return None
