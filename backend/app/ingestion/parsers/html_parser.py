from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup

from backend.app.ingestion.base import ParsedDocument, TextBlock
from backend.app.ingestion.confluence_export import (
    extract_confluence_page_title,
    extract_confluence_source_link,
)
from backend.app.ingestion.parsers.base_parser import BaseParser


def parse_html_string(
    raw: str,
    source_link: Optional[str] = None,
    title: Optional[str] = None,
) -> ParsedDocument:
    """Parse HTML/XHTML (Confluence export or API storage format)."""
    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    blocks: list[TextBlock] = []
    page = 1
    for heading in soup.find_all(["h1", "h2", "h3", "h4"]):
        section = heading.get_text(" ", strip=True)
        parts: list[str] = []
        for sib in heading.next_siblings:
            if getattr(sib, "name", None) in {"h1", "h2", "h3", "h4"}:
                break
            chunk = sib.get_text("\n", strip=True) if hasattr(sib, "get_text") else str(sib).strip()
            if chunk:
                parts.append(chunk)
        body = "\n".join(parts).strip()
        if section or body:
            blocks.append(TextBlock(page_number=page, text=body or section, section=section))
            page += 1

    if not blocks:
        plain = soup.get_text("\n", strip=True)
        blocks.append(TextBlock(page_number=1, text=plain, section=None))

    link = source_link or extract_confluence_source_link(soup, raw)
    suggested_title = title or extract_confluence_page_title(soup)
    return ParsedDocument(
        blocks=blocks,
        source_link=link,
        suggested_title=suggested_title,
    )


class HtmlParser(BaseParser):
    extensions = frozenset({".html", ".htm"})

    def parse(self, path: Path) -> ParsedDocument:
        raw = path.read_text(encoding="utf-8", errors="replace")
        return parse_html_string(raw)
