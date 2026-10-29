from __future__ import annotations

from datetime import datetime
from pathlib import Path

from backend.app.config import settings


def reports_dir() -> Path:
    path = settings.agent_reports_dir
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_report(agent_name: str, execution_id: str, body: str) -> str:
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{agent_name}_{stamp}_{execution_id}.md"
    path = reports_dir() / filename
    path.write_text(body, encoding="utf-8")
    return str(path)
