"""Normalize search snippets (strip Confluence storage HTML noise)."""

from __future__ import annotations

import html
import re

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def clean_search_snippet(raw: str, max_len: int = 320) -> str:
    if not raw:
        return ""
    text = raw.replace("[[", "").replace("]]", "")
    text = html.unescape(text)
    text = _TAG_RE.sub(" ", text)
    text = _WS_RE.sub(" ", text).strip()
    if len(text) > max_len:
        return text[: max_len - 1] + "…"
    return text
