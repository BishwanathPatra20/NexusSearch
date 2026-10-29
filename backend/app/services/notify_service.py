"""Office-safe notifications: local log + optional webhook (Slack/Teams-compatible JSON)."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

from backend.app.config import settings

logger = logging.getLogger("knowledgepilot.notify")


def _log_path() -> Path:
    path = settings.data_dir / "notifications.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def notify(title: str, message: str, level: str = "info", extra: Optional[Dict[str, Any]] = None) -> None:
    stamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    line = f"[{stamp}] {level.upper()} {title}: {message}"
    try:
        with _log_path().open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError as exc:
        logger.warning("Could not write notification log: %s", exc)

    url = (settings.notify_webhook_url or "").strip()
    if not url:
        return
    payload = {
        "text": f"*{title}*\n{message}",
        "title": title,
        "message": message,
        "level": level,
        "extra": extra or {},
    }
    try:
        httpx.post(url, json=payload, timeout=10.0)
    except Exception as exc:
        logger.warning("Webhook notify failed: %s", exc)
