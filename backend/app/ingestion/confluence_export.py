"""Helpers for Confluence *export* HTML (offline ingest). No API calls."""

import re
from typing import Optional
from bs4 import BeautifulSoup

_HTTP_URL = re.compile(r"^https?://", re.I)


def extract_confluence_source_link(soup: BeautifulSoup, file_text: str) -> Optional[str]:
    """Best-effort wiki URL from a Confluence HTML export."""
    for tag in soup.find_all("link", rel=True):
        rel = tag.get("rel")
        if rel and "canonical" in (rel if isinstance(rel, list) else [rel]):
            href = (tag.get("href") or "").strip()
            if _HTTP_URL.match(href):
                return href

    for meta in soup.find_all("meta"):
        prop = (meta.get("property") or meta.get("name") or "").lower()
        if prop in {"og:url", "twitter:url", "ajs-page-url"}:
            content = (meta.get("content") or "").strip()
            if _HTTP_URL.match(content):
                return content

    base = soup.find("base", href=True)
    base_href = (base.get("href") or "").strip() if base else ""
    if base_href and _HTTP_URL.match(base_href):
        return base_href.rstrip("/")

    # Confluence export comments sometimes embed the page URL.
    for match in re.finditer(r"https?://[^\s\"'<>]+/wiki/[^\s\"'<>]+", file_text):
        url = match.group(0).rstrip(").,;")
        if "/pages/" in url or "/display/" in url:
            return url

    return None


def extract_confluence_page_title(soup: BeautifulSoup) -> Optional[str]:
    for meta in soup.find_all("meta"):
        name = (meta.get("name") or "").lower()
        if name in {"ajs-page-title", "confluence-page-title"}:
            title = (meta.get("content") or "").strip()
            if title:
                return title
    h1 = soup.find("h1")
    if h1:
        text = h1.get_text(" ", strip=True)
        if text:
            return text
    title_tag = soup.find("title")
    if title_tag:
        text = title_tag.get_text(" ", strip=True)
        if text:
            return text.split(" - ")[0].strip() or None
    return None
