import json
import re
from functools import lru_cache
from typing import Dict, List, Set, Tuple

from backend.app.config import settings

_TOKEN = re.compile(r"[^\w]+", re.UNICODE)


@lru_cache(maxsize=1)
def _canonical_map() -> Dict[str, Set[str]]:
    path = settings.synonyms_path
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    out: Dict[str, Set[str]] = {}
    for key, syns in data.items():
        canonical = str(key).lower().strip()
        members = {canonical}
        for s in syns or []:
            members.add(str(s).lower().strip())
        out[canonical] = members
    return out


def reload_synonyms_cache() -> None:
    _canonical_map.cache_clear()


def expand_query(raw: str) -> Tuple[List[str], List[str], List[List[str]]]:
    """
    Returns flat expanded terms, canonical group keys that fired, and per-token OR groups.
    """
    tokens = [t for t in _TOKEN.split(raw.strip()) if len(t) >= 2]
    if not tokens and raw.strip():
        tokens = [raw.strip()]

    per_token: List[List[str]] = []
    flat: Set[str] = set()
    groups_hit: List[str] = []

    for token in tokens:
        lower = token.lower()
        members = {lower}
        for key, group in _canonical_map().items():
            if lower in group:
                members = set(group)
                if key not in groups_hit:
                    groups_hit.append(key)
                break
        per_token.append(sorted(members))
        flat.update(members)

    return sorted(flat), groups_hit, per_token


def build_fts_query_from_expansion(per_token: List[List[str]]) -> str:
    if not per_token:
        return ""
    clauses: List[str] = []
    for terms in per_token:
        if len(terms) == 1:
            clauses.append(f'"{terms[0]}"')
        else:
            inner = " OR ".join(f'"{t}"' for t in terms)
            clauses.append(f"({inner})")
    return " AND ".join(clauses)


def build_fts_query_or_from_expansion(per_token: List[List[str]]) -> str:
    """Any token group may match (fallback when strict AND returns nothing)."""
    if not per_token:
        return ""
    clauses: List[str] = []
    for terms in per_token:
        if len(terms) == 1:
            clauses.append(f'"{terms[0]}"')
        else:
            inner = " OR ".join(f'"{t}"' for t in terms)
            clauses.append(f"({inner})")
    return " OR ".join(clauses)
