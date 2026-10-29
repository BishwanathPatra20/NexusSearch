"""Confluence URL helpers for Streamlit (mirrors backend parser)."""

from __future__ import annotations

import re
from typing import List, Optional
from urllib.parse import parse_qs, urlparse

_PAGE_ID_RE = re.compile(r"(?:pageId=|/pages/)(\d+)", re.IGNORECASE)
_SOURCE_URI_RE = re.compile(r"confluence://page/(\d+)", re.IGNORECASE)


def parse_page_id(url: Optional[str]) -> Optional[str]:
    if not url or not str(url).strip():
        return None
    text = str(url).strip()
    m_uri = _SOURCE_URI_RE.search(text)
    if m_uri:
        return m_uri.group(1)
    m = _PAGE_ID_RE.search(text)
    if m:
        return m.group(1)
    parsed = urlparse(text)
    qs = parse_qs(parsed.query)
    for key in ("pageId", "pageid"):
        if key in qs and qs[key]:
            return str(qs[key][0]).strip()
    return None


def parse_page_ids_bulk(text: str) -> List[str]:
    """Extract unique page IDs from newline/comma-separated IDs or URLs."""
    if not text.strip():
        return []
    seen: set[str] = set()
    ordered: List[str] = []
    for token in re.split(r"[\s,;]+", text.strip()):
        token = token.strip()
        if not token:
            continue
        pid = parse_page_id(token) if not token.isdigit() else token
        if pid and pid not in seen:
            seen.add(pid)
            ordered.append(pid)
    return ordered
