"""Hybrid-lite rerank: FTS/BM25 scores + title/snippet lexical overlap (no external ML)."""

from __future__ import annotations

import re
from typing import List, Set

from backend.app.schemas.models import SearchHit

_TOKEN = re.compile(r"[a-z0-9]{2,}", re.IGNORECASE)


def _terms(query: str) -> Set[str]:
    return {t.lower() for t in _TOKEN.findall(query or "")}


def rerank_hits(query: str, hits: List[SearchHit]) -> List[SearchHit]:
    """Boost hits whose title/snippet overlap query terms (Haystack-style rerank, local-only)."""
    if not hits or not query.strip():
        return hits
    terms = _terms(query)
    if not terms:
        return hits

    rescored: List[SearchHit] = []
    for hit in hits:
        title_terms = _terms(hit.document_title)
        snippet_terms = _terms(hit.snippet)
        title_overlap = len(terms & title_terms) / max(len(terms), 1)
        snippet_overlap = len(terms & snippet_terms) / max(len(terms), 1)
        boost = (title_overlap * 12.0) + (snippet_overlap * 6.0)
        if title_overlap >= 0.5:
            boost += 8.0
        new_score = min(100.0, hit.score + boost)
        reasons = list(hit.ranking_reasons)
        if boost >= 4.0:
            reasons.append("+ Hybrid rerank (title/snippet overlap)")
        rescored.append(
            hit.model_copy(
                update={"score": round(new_score, 1), "ranking_reasons": reasons}
            )
        )
    rescored.sort(key=lambda h: h.score, reverse=True)
    return rescored
