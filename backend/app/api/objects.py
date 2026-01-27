import re
import uuid
import hashlib
from datetime import datetime, timezone
from typing import Optional
from tempfile import NamedTemporaryFile
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from ..db import get_db
from ..models import ObjectMeta
from ..minio_client import (
    put_bytes,
    get_object_stream,
    make_object_key,
    delete_object,
    settings,
)

objects_router = APIRouter(prefix="/objects", tags=["objects"])
CHUNK_SIZE = 1024 * 1024  # 1 MiB

# Temporary test user ID
TEST_USER_ID = "test-user-123"


def sanitize_filename(name: str) -> str:
    """Remove dangerous characters from filename."""
    if not name:
        return "unnamed"
    # Remove path separators, quotes, and control characters
    name = re.sub(r'[/\\"\'\x00-\x1f]', "", name)
    # Limit length
    return name[:255].strip() or "unnamed"


@objects_router.post("")
async def upload_object(
    folder: Optional[str] = Form(None),
    logical_name: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a file to storage.

    - **folder**: Virtual folder path (optional, e.g., "documents/invoices")
    - **logical_name**: Custom name (optional, defaults to uploaded filename)
    - **file**: The file to upload
    """
    object_uuid = uuid.uuid4()
    object_key = make_object_key(user_id=TEST_USER_ID, object_uuid=object_uuid)

    # Use NamedTemporaryFile for automatic cleanup
    with NamedTemporaryFile(delete=True) as tmp:
        h = hashlib.sha256()
        size = 0

        # Stream file to temp location while hashing
        while True:
            chunk = await file.read(CHUNK_SIZE)
            if not chunk:
                break
            tmp.write(chunk)
            h.update(chunk)
            size += len(chunk)

        # Reset file pointer to beginning for upload
        tmp.seek(0)

        # Upload to MinIO
        put_bytes(
            object_key=object_key,
            data=tmp,  # type: ignore
            length=size,
            content_type=file.content_type or "application/octet-stream",
            metadata={"original-name": file.filename or ""},
        )

    # Sanitize folder path
    folder_path = None
    if folder:
        folder_path = sanitize_filename(folder.strip("/"))

    current_name = sanitize_filename(logical_name or file.filename or "unnamed")

    # Store metadata in database
    row = ObjectMeta(
        object_id=object_uuid,
        user_id=TEST_USER_ID,
        bucket=settings.bucket,
        object_key=object_key,
        original_name=current_name,
        current_name=current_name,
        folder=folder_path,
        content_type=file.content_type,
        size_bytes=size,
        sha256_hex=h.hexdigest(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        "object_id": str(row.object_id),
        "user_id": row.user_id,
        "object_key": row.object_key,
        "name": row.current_name,
        "original_name": row.original_name,
        "folder": row.folder,
        "content_type": row.content_type,
        "size_bytes": row.size_bytes,
        "sha256": row.sha256_hex,
        "created_at": row.created_at.isoformat(),
    }


@objects_router.get("")
async def list_objects(
    folder: Optional[str] = Query(None, description="Filter by folder path"),
    search: Optional[str] = Query(None, description="Search by filename"),
    sort_by: str = Query(
        "created_at", description="Sort field: current_name, size_bytes, created_at"
    ),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    limit: int = Query(100, le=1000, description="Max results"),
    offset: int = Query(0, description="Pagination offset"),
    db: Session = Depends(get_db),
):
    """
    Browse user's storage with filtering, search, and pagination.

    - **folder**: Filter by folder (null = root, "documents" = documents folder)
    - **search**: Search filenames (case-insensitive partial match)
    - **sort_by**: Sort by current_name, size_bytes, or created_at
    - **sort_order**: asc (ascending) or desc (descending)
    - **limit**: Max number of results (default 100, max 1000)
    - **offset**: Pagination offset
    """
    # Base query - only test user's files
    query = db.query(ObjectMeta).filter(ObjectMeta.user_id == TEST_USER_ID)

    # Filter by folder
    if folder is not None:
        if folder == "":
            # Root folder (files with no folder)
            query = query.filter(ObjectMeta.folder.is_(None))
        else:
            # Specific folder
            query = query.filter(ObjectMeta.folder == sanitize_filename(folder))

    # Search by filename (search in current_name)
    if search:
        query = query.filter(ObjectMeta.current_name.ilike(f"%{search}%"))

    # Sorting
    sort_field = getattr(ObjectMeta, sort_by, ObjectMeta.created_at)
    if sort_order.lower() == "asc":
        query = query.order_by(asc(sort_field))
    else:
        query = query.order_by(desc(sort_field))

    # Get total count before pagination
    total_count = query.count()

    # Pagination
    results = query.offset(offset).limit(limit).all()

    # Format response
    items = [
        {
            "object_id": str(obj.object_id),
            "name": obj.current_name,
            "original_name": obj.original_name,
            "folder": obj.folder,
            "content_type": obj.content_type,
            "size_bytes": obj.size_bytes,
            "sha256": obj.sha256_hex,
            "created_at": obj.created_at.isoformat(),
        }
        for obj in results
    ]

    return {
        "items": items,
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total_count,
    }


@objects_router.get("/folders")
async def list_folders(
    db: Session = Depends(get_db),
):
    """
    Get list of unique folders for the current user.
    Useful for displaying folder navigation.
    """
    # Get distinct folder names
    folders = (
        db.query(ObjectMeta.folder)
        .filter(ObjectMeta.user_id == TEST_USER_ID)
        .filter(ObjectMeta.folder.isnot(None))
        .distinct()
        .all()
    )

    # Get file counts per folder
    folder_list = []
    for (folder_name,) in folders:
        count = (
            db.query(ObjectMeta)
            .filter(ObjectMeta.user_id == TEST_USER_ID)
            .filter(ObjectMeta.folder == folder_name)
            .count()
        )
        folder_list.append(
            {
                "name": folder_name,
                "file_count": count,
            }
        )

    # Get root folder count (files with no folder)
    root_count = (
        db.query(ObjectMeta)
        .filter(ObjectMeta.user_id == TEST_USER_ID)
        .filter(ObjectMeta.folder.is_(None))
        .count()
    )

    return {
        "folders": folder_list,
        "root_file_count": root_count,
    }


@objects_router.get("/stats")
async def get_storage_stats(
    db: Session = Depends(get_db),
):
    """
    Get storage statistics for the current user.
    """
    from sqlalchemy import func

    stats = (
        db.query(
            func.count(ObjectMeta.object_id).label("total_files"),
            func.sum(ObjectMeta.size_bytes).label("total_bytes"),
        )
        .filter(ObjectMeta.user_id == TEST_USER_ID)
        .first()
    )

    # Handle case when stats is None (no files)
    if stats is None:
        return {
            "total_files": 0,
            "total_bytes": 0,
            "total_mb": 0.0,
        }

    return {
        "total_files": stats.total_files or 0,
        "total_bytes": stats.total_bytes or 0,
        "total_mb": round((stats.total_bytes or 0) / (1024 * 1024), 2),
    }


@objects_router.get("/{object_id}")
def download_object(
    object_id: str,
    db: Session = Depends(get_db),
):
    """
    Download a file. Browser will automatically trigger download.
    """
    try:
        object_uuid = uuid.UUID(object_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid object_id format")

    row = db.get(ObjectMeta, object_uuid)
    if not row:
        raise HTTPException(status_code=404, detail="Object not found")

    # Get object stream from MinIO
    obj = get_object_stream(row.object_key) # type: ignore

    def iterator():
        try:
            for chunk in obj.stream(CHUNK_SIZE):
                yield chunk
        finally:
            obj.close()
            obj.release_conn()

    # Use current_name for download
    safe_filename = sanitize_filename(row.current_name) # type: ignore

    headers = {
        "Content-Disposition": f'attachment; filename="{safe_filename}"',
        "X-Content-SHA256": row.sha256_hex,  # Extra integrity check
    }

    return StreamingResponse(
        iterator(),
        media_type=row.content_type or "application/octet-stream", # type: ignore
        headers=headers,
    )


@objects_router.delete("/{object_id}")
async def delete_object_endpoint(
    object_id: str,
    db: Session = Depends(get_db),
):
    """
    Delete a file from storage and database.
    """
    try:
        object_uuid = uuid.UUID(object_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid object_id format")

    row = db.get(ObjectMeta, object_uuid)
    if not row:
        raise HTTPException(status_code=404, detail="Object not found")

    # Delete from MinIO
    try:
        delete_object(str(row.object_key))
    except Exception as e:
        # Log error but continue - metadata cleanup is important
        print(f"MinIO delete failed for {row.object_key}: {e}")

    # Delete from database
    db.delete(row)
    db.commit()

    return {
        "success": True,
        "object_id": object_id,
        "message": "Object deleted successfully",
    }


@objects_router.patch("/{object_id}")
async def update_object_metadata(
    object_id: str,
    name: Optional[str] = Form(None),
    folder: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    Update file metadata (rename or move to different folder).

    - **name**: New filename (updates current_name, not original_name)
    - **folder**: New folder path (empty string for root)
    """
    try:
        object_uuid = uuid.UUID(object_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid object_id format")

    row = db.get(ObjectMeta, object_uuid)
    if not row:
        raise HTTPException(status_code=404, detail="Object not found")

    # Update fields
    if name is not None:
        row.current_name = sanitize_filename(name)  # type: ignore

    if folder is not None:
        if folder.strip() == "":
            row.folder = None  # type: ignore  # Move to root
        else:
            row.folder = sanitize_filename(folder.strip("/"))  # type: ignore

    db.commit()
    db.refresh(row)

    return {
        "object_id": str(row.object_id),
        "name": row.current_name,
        "original_name": row.original_name,
        "folder": row.folder,
        "updated": True,
    }

