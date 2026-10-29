"""Ingest watcher — index new or modified files in configured folder(s)."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from backend.app.config import settings
from backend.app.services import document_service


def _watch_tags() -> List[str]:
    return [t.strip() for t in settings.watch_tags.split(",") if t.strip()]


def watch_paths() -> List[Path]:
    if settings.watch_folders:
        return [
            Path(p.strip()).expanduser().resolve()
            for p in settings.watch_folders.split(",")
            if p.strip()
        ]
    if settings.watch_folder:
        return [Path(settings.watch_folder).expanduser().resolve()]
    return []


def _indexed_by_uri(conn: sqlite3.Connection) -> Dict[str, str]:
    rows = conn.execute(
        "SELECT source_uri, upload_date FROM documents WHERE source_uri IS NOT NULL AND source_uri != ''"
    ).fetchall()
    return {str(r["source_uri"]): str(r["upload_date"]) for r in rows}


def _file_newer_than_index(path: Path, upload_date_iso: str) -> bool:
    try:
        uploaded = datetime.fromisoformat(upload_date_iso.replace("Z", ""))
    except ValueError:
        return True
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    return mtime > uploaded


def run(conn: sqlite3.Connection) -> Dict[str, Any]:
    if not settings.watch_enabled:
        return {
            "message": "Ingest watcher disabled (set KNOWLEDGEPILOT_WATCH_ENABLED=true).",
            "indexed": [],
            "reindexed": [],
            "skipped": 0,
        }
    paths = watch_paths()
    if not paths:
        return {
            "message": "No watch folder(s) configured (WATCH_FOLDER or WATCH_FOLDERS).",
            "indexed": [],
            "reindexed": [],
            "skipped": 0,
        }

    known = _indexed_by_uri(conn)
    tags = _watch_tags()
    indexed: List[Dict[str, Any]] = []
    reindexed: List[Dict[str, Any]] = []
    errors: List[str] = []
    skipped = 0

    for folder in paths:
        if not folder.is_dir():
            errors.append(f"Not a directory: {folder}")
            continue
        for file_path in document_service.collect_folder_files(folder, settings.watch_recursive):
            key = str(file_path)
            try:
                if key not in known:
                    doc, chunks = document_service.ingest_local_file(conn, file_path, tags=tags)
                    indexed.append(
                        {"document_id": doc.id, "file": file_path.name, "chunks": chunks, "folder": str(folder)}
                    )
                    known[key] = doc.upload_date.isoformat()
                    continue
                if _file_newer_than_index(file_path, known[key]):
                    document_service.delete_by_source_uri(conn, key)
                    doc, chunks = document_service.ingest_local_file(conn, file_path, tags=tags)
                    reindexed.append(
                        {"document_id": doc.id, "file": file_path.name, "chunks": chunks, "folder": str(folder)}
                    )
                    known[key] = doc.upload_date.isoformat()
                else:
                    skipped += 1
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{file_path.name}: {exc}")

    from backend.app.services.automation.report_util import write_report
    from backend.app.services.notify_service import notify

    total = len(indexed) + len(reindexed)
    if total > 0:
        notify(
            "Ingest watcher",
            f"{len(indexed)} new, {len(reindexed)} updated file(s) indexed.",
            level="info",
        )

    body = "\n".join(
        [
            "# Ingest watcher report",
            "",
            f"Folders: {', '.join(str(p) for p in paths)}",
            f"New: **{len(indexed)}** · Updated: **{len(reindexed)}** · Unchanged: **{skipped}**",
            "",
            "## Errors",
            *(errors or ["(none)"]),
        ]
    )
    report_path = write_report("ingest_watcher", "inline", body)
    return {
        "folders": [str(p) for p in paths],
        "indexed": indexed,
        "reindexed": reindexed,
        "indexed_count": len(indexed),
        "reindexed_count": len(reindexed),
        "skipped": skipped,
        "errors": errors,
        "report_path": report_path,
        "message": f"Ingest watcher: {len(indexed)} new, {len(reindexed)} updated.",
    }
