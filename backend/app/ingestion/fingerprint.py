import hashlib
import re


def normalize_for_fingerprint(text: str, max_chars: int = 50_000) -> str:
    collapsed = re.sub(r"\s+", " ", (text or "").lower()).strip()
    return collapsed[:max_chars]


def content_fingerprint(text: str) -> str:
    normalized = normalize_for_fingerprint(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
