from pathlib import Path

from backend.app.ingestion.base import ParsedDocument, TextBlock
from backend.app.ingestion.parsers.base_parser import BaseParser


class TextParser(BaseParser):
    extensions = frozenset({".txt"})

    def parse(self, path: Path) -> ParsedDocument:
        text = path.read_text(encoding="utf-8", errors="replace")
        return ParsedDocument(blocks=[TextBlock(page_number=1, text=text)])


def parse_txt(path: Path) -> ParsedDocument:
    return TextParser().parse(path)
