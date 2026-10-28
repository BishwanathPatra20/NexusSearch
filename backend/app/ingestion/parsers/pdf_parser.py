from pathlib import Path

import pdfplumber

from backend.app.ingestion.base import ParsedDocument, TextBlock
from backend.app.ingestion.parsers.base_parser import BaseParser


class PdfParser(BaseParser):
    extensions = frozenset({".pdf"})

    def parse(self, path: Path) -> ParsedDocument:
        blocks: list[TextBlock] = []
        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                blocks.append(TextBlock(page_number=i, text=text))
        return ParsedDocument(blocks=blocks)


def parse_pdf(path: Path) -> ParsedDocument:
    return PdfParser().parse(path)
