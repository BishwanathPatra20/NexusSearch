from pathlib import Path
from typing import Dict, List

from backend.app.ingestion.base import ParsedDocument
from backend.app.ingestion.parsers.base_parser import BaseParser
from backend.app.ingestion.parsers.docx_parser import DocxParser
from backend.app.ingestion.parsers.html_parser import HtmlParser
from backend.app.ingestion.parsers.markdown_parser import MarkdownParser
from backend.app.ingestion.parsers.pdf_parser import PdfParser
from backend.app.ingestion.parsers.text_parser import TextParser

_PARSER_INSTANCES: List[BaseParser] = [
    PdfParser(),
    DocxParser(),
    TextParser(),
    MarkdownParser(),
    HtmlParser(),
]

PARSERS_BY_EXT: Dict[str, BaseParser] = {}
for parser in _PARSER_INSTANCES:
    for ext in parser.extensions:
        PARSERS_BY_EXT[ext] = parser

SUPPORTED_EXTENSIONS = frozenset(PARSERS_BY_EXT.keys())


def get_parser(path: Path) -> BaseParser:
    ext = path.suffix.lower()
    parser = PARSERS_BY_EXT.get(ext)
    if parser is None:
        raise ValueError(f"Unsupported file type: {ext}")
    return parser


def parse_file(path: Path) -> ParsedDocument:
    return get_parser(path).parse(path)
