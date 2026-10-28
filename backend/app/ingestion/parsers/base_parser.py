from abc import ABC, abstractmethod
from pathlib import Path

from backend.app.ingestion.base import ParsedDocument


class BaseParser(ABC):
    """Plugin interface for document parsers (office-safe, local files only)."""

    extensions: frozenset[str]

    @abstractmethod
    def parse(self, path: Path) -> ParsedDocument:
        raise NotImplementedError

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() in self.extensions
