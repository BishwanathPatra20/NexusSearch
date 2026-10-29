import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.app.services import document_service


def create_job(conn: sqlite3.Connection, job_type: str, payload: Dict[str, Any]) -> int:
    cursor = conn.execute(
        """
        INSERT INTO ingestion_jobs (job_type, status, payload_json)
        VALUES (?, 'pending', ?)
        """,
        (job_type, json.dumps(payload)),
    )
    job_id = cursor.lastrowid
    assert job_id is not None
    return job_id


def update_job(
    conn: sqlite3.Connection,
    job_id: int,
    status: str,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
) -> None:
    conn.execute(
        """
        UPDATE ingestion_jobs
        SET status = ?, result_json = ?, error_message = ?, updated_at = datetime('now')
        WHERE id = ?
        """,
        (status, json.dumps(result) if result else None, error, job_id),
    )


def get_job(conn: sqlite3.Connection, job_id: int) -> Optional[sqlite3.Row]:
    return conn.execute("SELECT * FROM ingestion_jobs WHERE id = ?", (job_id,)).fetchone()


def list_jobs(conn: sqlite3.Connection, limit: int = 15) -> List[sqlite3.Row]:
    lim = max(1, min(int(limit), 50))
    return conn.execute(
        "SELECT * FROM ingestion_jobs ORDER BY id DESC LIMIT ?",
        (lim,),
    ).fetchall()


def process_folder_ingest_job(job_id: int) -> None:
    from backend.app.db.connection import get_connection

    with get_connection() as conn:
        row = get_job(conn, job_id)
        if row is None:
            return
        update_job(conn, job_id, "processing")
        payload = json.loads(row["payload_json"])
        folder = document_service.validate_folder_path(payload["folder_path"])
        tags: List[str] = payload.get("tags") or []
        recursive = bool(payload.get("recursive", True))

        indexed: List[Dict[str, Any]] = []
        errors: List[str] = []
        try:
            for file_path in document_service.collect_folder_files(folder, recursive):
                try:
                    doc, chunks = document_service.ingest_local_file(conn, file_path, tags=tags)
                    indexed.append(
                        {"document_id": doc.id, "file": str(file_path), "chunks": chunks}
                    )
                except Exception as exc:  # noqa: BLE001 — per-file failure should not abort job
                    errors.append(f"{file_path}: {exc}")
            update_job(
                conn,
                job_id,
                "completed",
                result={"indexed_count": len(indexed), "indexed": indexed, "errors": errors},
            )
        except Exception as exc:  # noqa: BLE001
            update_job(conn, job_id, "failed", error=str(exc))


def process_confluence_sync_job(job_id: int) -> None:
    from backend.app.db.connection import get_connection
    from backend.app.services.confluence_sync_service import sync_descendants, sync_space

    with get_connection() as conn:
        row = get_job(conn, job_id)
        if row is None:
            return
        update_job(conn, job_id, "processing")
        payload = json.loads(row["payload_json"])
        tags: List[str] = payload.get("tags") or []
        replace_existing = bool(payload.get("replace_existing", True))

        try:
            if payload.get("parent_page_id"):
                result = sync_descendants(
                    conn,
                    parent_page_id=str(payload["parent_page_id"]),
                    max_pages=int(payload.get("max_pages") or 100),
                    include_parent=True,
                    tags=tags,
                    replace_existing=replace_existing,
                )
                update_job(
                    conn,
                    job_id,
                    "completed",
                    result={
                        "mode": "descendants",
                        "indexed": result.indexed,
                        "requested": result.requested,
                        "skipped": result.skipped,
                        "errors": result.errors,
                    },
                )
            elif payload.get("space_key"):
                result = sync_space(
                    conn,
                    space_key=str(payload["space_key"]).strip(),
                    limit=int(payload.get("limit") or 100),
                    tags=tags,
                    replace_existing=replace_existing,
                )
                update_job(
                    conn,
                    job_id,
                    "completed",
                    result={
                        "mode": "space",
                        "space_key": result.space_key,
                        "pages_indexed": result.pages_indexed,
                        "pages_fetched": result.pages_fetched,
                        "skipped": result.skipped,
                        "errors": result.errors,
                    },
                )
            else:
                update_job(conn, job_id, "failed", error="Missing space_key or parent_page_id")
        except Exception as exc:  # noqa: BLE001
            update_job(conn, job_id, "failed", error=str(exc))
