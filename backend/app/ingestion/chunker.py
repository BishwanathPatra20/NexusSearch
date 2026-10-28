from dataclasses import dataclass
from typing import List, Optional

from backend.app.config import settings
from backend.app.ingestion.base import ParsedDocument, TextBlock


@dataclass
class ChunkDraft:
    page_number: int
    chunk_index: int
    content: str
    section: Optional[str] = None


def hybrid_chunk(parsed: ParsedDocument) -> List[ChunkDraft]:
    """One chunk per normal page; split oversized pages into subchunks."""
    chunks: List[ChunkDraft] = []
    max_len = settings.max_chars_per_chunk
    overlap = settings.chunk_overlap_chars

    for block in parsed.blocks:
        text = (block.text or "").strip()
        if not text:
            continue
        if len(text) <= max_len:
            chunks.append(
                ChunkDraft(
                    page_number=block.page_number,
                    chunk_index=0,
                    content=text,
                    section=block.section,
                )
            )
            continue
        sub_index = 0
        start = 0
        while start < len(text):
            end = min(start + max_len, len(text))
            piece = text[start:end].strip()
            if piece:
                chunks.append(
                    ChunkDraft(
                        page_number=block.page_number,
                        chunk_index=sub_index,
                        content=piece,
                        section=block.section,
                    )
                )
                sub_index += 1
            if end >= len(text):
                break
            start = max(end - overlap, start + 1)
    return chunks


def blocks_from_plain_text(text: str, page_number: int = 1) -> ParsedDocument:
    return ParsedDocument(blocks=[TextBlock(page_number=page_number, text=text)])
