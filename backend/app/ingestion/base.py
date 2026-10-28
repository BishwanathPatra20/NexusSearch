from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TextBlock:
    """Normalized text unit from any parser before chunking."""

    page_number: int
    text: str
    section: Optional[str] = None


@dataclass
class ParsedDocument:
    blocks: List[TextBlock] = field(default_factory=list)
    # Populated from Confluence HTML exports when present (display-only; no live API).
    source_link: Optional[str] = None
    suggested_title: Optional[str] = None
