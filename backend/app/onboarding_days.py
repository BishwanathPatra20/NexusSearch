"""Natural ordering for KT day labels (Day 1, Day 2, … Day 10)."""

import re
from typing import List, Optional, Tuple

# "Day 1", "day1", "week 2", etc.
_DAY_WORD_NUM = re.compile(r"(?:day|week)\s*#?\s*(\d+)", re.IGNORECASE)


def extract_day_number(text: Optional[str]) -> Optional[int]:
    if not text or not str(text).strip():
        return None
    raw = str(text).strip()
    m = _DAY_WORD_NUM.search(raw)
    if m:
        return int(m.group(1))
    if re.fullmatch(r"\d{1,2}", raw):
        return int(raw)
    if re.search(r"(?:day|week)", raw, re.IGNORECASE):
        m2 = re.search(r"\b(\d+)\b", raw)
        if m2:
            return int(m2.group(1))
    return None


def day_sort_key(label: Optional[str]) -> Tuple[int, int, str]:
    """Sort key: numbered days first (by number), then other labels, then blank."""
    if not label or not str(label).strip():
        return (2, 9999, "")
    text = str(label).strip()
    lower = text.lower()
    if lower in ("general", "other", "misc"):
        return (1, 9998, lower)
    n = extract_day_number(text)
    if n is not None:
        return (0, n, lower)
    return (1, 0, lower)


def item_sort_key(
    day_label: Optional[str],
    title: str,
    sheet_name: str = "",
    row_index: int = 0,
) -> Tuple[int, int, str, str, int]:
    """Order onboarding rows by day (label or title), then sheet row."""
    n = extract_day_number(day_label)
    if n is None:
        n = extract_day_number(title)
    if n is not None:
        return (0, n, (title or "").lower(), sheet_name.lower(), row_index)
    fallback = (day_label or title or "").strip().lower()
    return (1, 0, fallback, sheet_name.lower(), row_index)


def sort_day_labels(days: List[str]) -> List[str]:
    return sorted(days, key=day_sort_key)


def title_redundant_with_day(title: str, day_label: Optional[str]) -> bool:
    if not day_label:
        return False
    t = (title or "").strip().lower()
    d = day_label.strip().lower()
    if not t or not d:
        return False
    if t == d:
        return True
    if t.startswith(d + " ") or t.startswith(d + ":") or t.startswith(d + "-"):
        return True
    return False
