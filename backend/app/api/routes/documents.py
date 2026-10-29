import json
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile

from backend.app.db.connection import get_connection
from backend.app.schemas.models import (
    ChunkOut,
    DocumentSummary,
    DocumentUpdate,
    FolderIngestRequest,
    FolderIngestResponse,
    UploadResponse,
)
from backend.app.services import document_service
from backend.app.services.job_service import create_job, process_folder_ingest_job

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    tags_json: Optional[str] = Form("[]"),
) -> UploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    try:
        tags = json.loads(tags_json or "[]")
        if not isinstance(tags, list):
            raise ValueError("tags must be a JSON array")
        tags = [str(t) for t in tags]
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid tags_json: {exc}") from exc

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        with get_connection() as conn:
            doc, chunk_count = document_service.ingest_upload(
                conn, file.filename, content, title=title, tags=tags
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return UploadResponse(document=doc, chunks_created=chunk_count)


@router.post("/ingest-folder", response_model=FolderIngestResponse)
def ingest_folder(
    body: FolderIngestRequest,
    background_tasks: BackgroundTasks,
) -> FolderIngestResponse:
    try:
        document_service.validate_folder_path(body.folder_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    with get_connection() as conn:
        job_id = create_job(
            conn,
            "folder_ingest",
            {
                "folder_path": body.folder_path,
                "tags": body.tags,
                "recursive": body.recursive,
            },
        )

    if body.async_job:
        background_tasks.add_task(process_folder_ingest_job, job_id)
        return FolderIngestResponse(
            job_id=job_id,
            message="Folder ingestion queued (local background worker).",
        )

    process_folder_ingest_job(job_id)
    return FolderIngestResponse(job_id=job_id, message="Folder ingestion completed.")


@router.get("", response_model=List[DocumentSummary])
def list_documents(source_type: Optional[str] = None) -> List[DocumentSummary]:
    with get_connection() as conn:
        return document_service.list_documents(conn, source_type=source_type)


@router.get("/{document_id}", response_model=DocumentSummary)
def get_document(document_id: int, track_view: bool = True) -> DocumentSummary:
    try:
        with get_connection() as conn:
            return document_service.get_document(conn, document_id, increment_view=track_view)
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")


@router.patch("/{document_id}", response_model=DocumentSummary)
def patch_document(document_id: int, body: DocumentUpdate) -> DocumentSummary:
    try:
        with get_connection() as conn:
            return document_service.update_document(
                conn,
                document_id,
                title=body.title,
                tags=body.tags,
                status=body.status,
                version_label=body.version_label,
                related_document_ids=body.related_document_ids,
            )
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")


@router.get("/{document_id}/chunks", response_model=List[ChunkOut])
def get_chunks(document_id: int) -> List[ChunkOut]:
    try:
        with get_connection() as conn:
            document_service.get_document(conn, document_id, increment_view=False)
            return document_service.list_chunks(conn, document_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: int) -> None:
    try:
        with get_connection() as conn:
            document_service.delete_document(conn, document_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")
