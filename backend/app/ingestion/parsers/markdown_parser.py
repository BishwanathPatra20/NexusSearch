import re
from pathlib import Path

from backend.app.ingestion.base import ParsedDocument, TextBlock
from backend.app.ingestion.parsers.base_parser import BaseParser


class MarkdownParser(BaseParser):
    extensions = frozenset({".md", ".markdown"})

    def parse(self, path: Path) -> ParsedDocument:
        text = path.read_text(encoding="utf-8", errors="replace")
        blocks: list[TextBlock] = []
        current_section = None
        buffer: list[str] = []
        page = 1

        def flush() -> None:
            nonlocal page
            body = "\n".join(buffer).strip()
            if body:
                blocks.append(
                    TextBlock(page_number=page, text=body, section=current_section)
                )
                page += 1
            buffer.clear()

        for line in text.splitlines():
            if re.match(r"^#{1,6}\s+", line):
                flush()
                current_section = line.lstrip("#").strip()
            else:
                buffer.append(line)
        flush()

        if not blocks:
            blocks.append(TextBlock(page_number=1, text=text, section=None))
        return ParsedDocument(blocks=blocks)
