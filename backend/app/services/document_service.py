import json
import shutil
import sqlite3
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import List, Optional, Tuple

from backend.app.config import settings
from backend.app.constants import DocumentStatus
from backend.app.ingestion.chunker import hybrid_chunk
from backend.app.ingestion.fingerprint import content_fingerprint
from backend.app.ingestion.parsers import SUPPORTED_EXTENSIONS, parse_file
from backend.app.knowledge_path import build_knowledge_path
from backend.app.schemas.models import ChunkOut, DocumentSummary, RelatedDocumentBrief


def _parse_tags(tags_json: str) -> List[str]:
    try:
        data = json.loads(tags_json or "[]")
        if isinstance(data, list):
            return [str(t) for t in data]
    except json.JSONDecodeError:
        pass
    return []


def _parse_id_list(raw: str) -> List[int]:
    try:
        data = json.loads(raw or "[]")
        if isinstance(data, list):
            return [int(x) for x in data]
    except (json.JSONDecodeError, TypeError, ValueError):
        pass
    return []


def _status_from_row(value: Optional[str]) -> DocumentStatus:
    try:
        return DocumentStatus(value or DocumentStatus.ACTIVE.value)
    except ValueError:
        return DocumentStatus.ACTIVE


def _related_briefs(conn: sqlite3.Connection, ids: List[int]) -> List[RelatedDocumentBrief]:
    if not ids:
        return []
    placeholders = ",".join("?" for _ in ids)
    rows = conn.execute(
        f"SELECT id, title, file_name, status FROM documents WHERE id IN ({placeholders})",
        ids,
    ).fetchall()
    return [
        RelatedDocumentBrief(
            id=r["id"],
            title=r["title"],
            file_name=r["file_name"],
            status=_status_from_row(r["status"]),
        )
        for r in rows
    ]


def _duplicate_ids(conn: sqlite3.Connection, document_id: int, fingerprint: Optional[str]) -> List[int]:
    if not fingerprint:
        return []
    rows = conn.execute(
        """
        SELECT id FROM documents
        WHERE content_fingerprint = ? AND id != ?
        ORDER BY upload_date DESC
        LIMIT 5
        """,
        (fingerprint, document_id),
    ).fetchall()
    return [r["id"] for r in rows]


def _row_to_summary(conn: sqlite3.Connection, row: sqlite3.Row, chunk_count: Optional[int] = None) -> DocumentSummary:
    related_ids = _parse_id_list(row["related_document_ids_json"])
    fp = row["content_fingerprint"]
    return DocumentSummary(
        id=row["id"],
        title=row["title"],
        file_name=row["file_name"],
        file_type=row["file_type"],
        tags=_parse_tags(row["tags_json"]),
        source_type=row["source_type"],
        source_uri=row["source_uri"],
        upload_date=datetime.fromisoformat(row["upload_date"]),
        view_count=row["view_count"],
        chunk_count=chunk_count,
        status=_status_from_row(row["status"]),
        version_label=row["version_label"],
        related_document_ids=related_ids,
        related_documents=_related_briefs(conn, related_ids),
        duplicate_of_ids=_duplicate_ids(conn, row["id"], fp),
        source_link=row["source_link"] if "source_link" in row.keys() else None,
        knowledge_path=build_knowledge_path(
            source_type=row["source_type"],
            source_uri=row["source_uri"],
            file_name=row["file_name"],
            document_id=row["id"],
        ),
    )


def _insert_chunks(conn: sqlite3.Connection, document_id: int, drafts) -> str:
    combined: List[str] = []
    for draft in drafts:
        conn.execute(
            """
            INSERT INTO document_chunks (document_id, page_number, chunk_index, section, content)
            VALUES (?, ?, ?, ?, ?)
            """,
            (document_id, draft.page_number, draft.chunk_index, draft.section, draft.content),
        )
        combined.append(draft.content)
    return content_fingerprint("\n".join(combined))


def ingest_upload(
    conn: sqlite3.Connection,
    file_name: str,
    file_bytes: bytes,
    title: Optional[str] = None,
    tags: Optional[List[str]] = None,
    source_type: str = "upload",
    source_uri: Optional[str] = None,
    status: DocumentStatus = DocumentStatus.ACTIVE,
    version_label: Optional[str] = None,
) -> Tuple[DocumentSummary, int]:
    safe_name = Path(file_name).name
    ext = Path(safe_name).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported type {ext}. Allowed: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")

    doc_title = (title or Path(safe_name).stem).strip() or safe_name
    tags_json = json.dumps(tags or [])

    cursor = conn.execute(
        """
        INSERT INTO documents (
            title, file_name, file_type, tags_json, source_type, source_uri,
            status, version_label, related_document_ids_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, '[]')
        """,
        (
            doc_title,
            safe_name,
            ext.lstrip("."),
            tags_json,
            source_type,
            source_uri or safe_name,
            status.value,
            version_label,
        ),
    )
    document_id = cursor.lastrowid
    assert document_id is not None

    dest = settings.uploads_dir / f"{document_id}_{safe_name}"
    dest.write_bytes(file_bytes)

    parsed = parse_file(dest)
    drafts = hybrid_chunk(parsed)
    if not drafts:
        raise ValueError("No text could be extracted from this file.")

    fp = _insert_chunks(conn, document_id, drafts)
    updates: List[str] = ["content_fingerprint = ?"]
    params: List[object] = [fp]
    if parsed.source_link:
        updates.append("source_link = ?")
        params.append(parsed.source_link)
    if parsed.suggested_title and not title:
        updates.append("title = ?")
        params.append(parsed.suggested_title.strip())
    params.append(document_id)
    conn.execute(
        f"UPDATE documents SET {', '.join(updates)} WHERE id = ?",
        params,
    )

    row = conn.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
    return _row_to_summary(conn, row, chunk_count=len(drafts)), len(drafts)


def ingest_local_file(
    conn: sqlite3.Connection,
    file_path: Path,
    tags: Optional[List[str]] = None,
) -> Tuple[DocumentSummary, int]:
    if not file_path.is_file():
        raise ValueError(f"Not a file: {file_path}")
    data = file_path.read_bytes()
    return ingest_upload(
        conn,
        file_path.name,
        data,
        title=file_path.stem,
        tags=tags,
        source_type="folder",
        source_uri=str(file_path),
    )


def list_documents(
    conn: sqlite3.Connection,
    source_type: Optional[str] = None,
) -> List[DocumentSummary]:
    sql = """
        SELECT d.*, COUNT(c.id) AS chunk_count
        FROM documents d
        LEFT JOIN document_chunks c ON c.document_id = d.id
    """
    params: List[object] = []
    if source_type:
        sql += " WHERE d.source_type = ?"
        params.append(source_type.strip().lower())
    sql += " GROUP BY d.id ORDER BY d.upload_date DESC"
    rows = conn.execute(sql, params).fetchall()
    return [_row_to_summary(conn, r, chunk_count=r["chunk_count"]) for r in rows]


def get_document(conn: sqlite3.Connection, document_id: int, increment_view: bool = False) -> DocumentSummary:
    if increment_view:
        conn.execute(
            "UPDATE documents SET view_count = view_count + 1 WHERE id = ?",
            (document_id,),
        )
    row = conn.execute(
        """
        SELECT d.*, COUNT(c.id) AS chunk_count
        FROM documents d
        LEFT JOIN document_chunks c ON c.document_id = d.id
        WHERE d.id = ?
        GROUP BY d.id
        """,
        (document_id,),
    ).fetchone()
    if row is None:
        raise KeyError("Document not found")
    return _row_to_summary(conn, row, chunk_count=row["chunk_count"])


def update_document(
    conn: sqlite3.Connection,
    document_id: int,
    title: Optional[str] = None,
    tags: Optional[List[str]] = None,
    status: Optional[DocumentStatus] = None,
    version_label: Optional[str] = None,
    related_document_ids: Optional[List[int]] = None,
) -> DocumentSummary:
    row = conn.execute("SELECT id FROM documents WHERE id = ?", (document_id,)).fetchone()
    if row is None:
        raise KeyError("Document not found")

    if title is not None:
        conn.execute("UPDATE documents SET title = ? WHERE id = ?", (title.strip(), document_id))
    if tags is not None:
        conn.execute(
            "UPDATE documents SET tags_json = ? WHERE id = ?",
            (json.dumps(tags), document_id),
        )
    if status is not None:
        conn.execute("UPDATE documents SET status = ? WHERE id = ?", (status.value, document_id))
    if version_label is not None:
        conn.execute(
            "UPDATE documents SET version_label = ? WHERE id = ?",
            (version_label, document_id),
        )
    if related_document_ids is not None:
        unique_ids = sorted({int(i) for i in related_document_ids if int(i) != document_id})
        conn.execute(
            "UPDATE documents SET related_document_ids_json = ? WHERE id = ?",
            (json.dumps(unique_ids), document_id),
        )
    return get_document(conn, document_id, increment_view=False)


def list_chunks(conn: sqlite3.Connection, document_id: int) -> List[ChunkOut]:
    rows = conn.execute(
        """
        SELECT id, document_id, page_number, chunk_index, section, content
        FROM document_chunks
        WHERE document_id = ?
        ORDER BY page_number, chunk_index
        """,
        (document_id,),
    ).fetchall()
    return [
        ChunkOut(
            id=r["id"],
            document_id=r["document_id"],
            page_number=r["page_number"],
            chunk_index=r["chunk_index"],
            section=r["section"],
            content=r["content"],
        )
        for r in rows
    ]


def delete_by_source_uri(conn: sqlite3.Connection, source_uri: str) -> bool:
    row = conn.execute("SELECT id FROM documents WHERE source_uri = ?", (source_uri,)).fetchone()
    if row is None:
        return False
    delete_document(conn, int(row["id"]))
    return True


def delete_document(conn: sqlite3.Connection, document_id: int) -> None:
    row = conn.execute("SELECT file_name FROM documents WHERE id = ?", (document_id,)).fetchone()
    if row is None:
        raise KeyError("Document not found")
    conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
    for path in settings.uploads_dir.glob(f"{document_id}_*"):
        path.unlink(missing_ok=True)


def collect_folder_files(folder: Path, recursive: bool) -> List[Path]:
    pattern = "**/*" if recursive else "*"
    files: List[Path] = []
    for path in folder.glob(pattern):
        if not path.is_file():
            continue
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > settings.folder_ingest_max_file_mb:
            continue
        files.append(path)
        if len(files) >= settings.folder_ingest_max_files:
            break
    return sorted(files)


def validate_folder_path(folder_path: str) -> Path:
    path = Path(folder_path).expanduser().resolve(strict=False)
    if not path.exists() or not path.is_dir():
        raise ValueError("Folder path does not exist or is not a directory")
    if ".." in Path(folder_path).parts:
        raise ValueError("Invalid folder path")
    return path


def title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()
