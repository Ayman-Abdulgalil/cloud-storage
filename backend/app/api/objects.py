# api/objects.py
import os
import uuid
import hashlib
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ObjectMeta
from ..storage.minio_client import put_bytes, get_object_stream, make_object_key, settings

router = APIRouter(prefix="/objects", tags=["objects"])

CHUNK_SIZE = 1024 * 1024  # 1 MiB


@router.post("")
async def upload_object(
    file: UploadFile = File(...),
    # Temporary until AAA: accept user_id as form data.
    user_id: str = Form(...),
    logical_name: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    object_uuid = uuid.uuid4()
    object_key = make_object_key(user_id=user_id, object_uuid=object_uuid)

    # We want sha256 + size + still upload as an object.
    # Minimal approach: spool to /tmp so we know the exact length for put_object.
    tmp_path = f"/tmp/{object_uuid}.upload"
    h = hashlib.sha256()
    size = 0

    with open(tmp_path, "wb") as out:
        while True:
            chunk = await file.read(CHUNK_SIZE)
            if not chunk:
                break
            out.write(chunk)
            h.update(chunk)
            size += len(chunk)

    with open(tmp_path, "rb") as data:
        put_bytes(
            object_key=object_key,
            data=data,
            length=size,
            content_type=file.content_type or "application/octet-stream",
            metadata={"original-name": file.filename or ""},
        )

    try:
        os.remove(tmp_path)
    except OSError:
        pass

    row = ObjectMeta(
        object_id=object_uuid,
        user_id=user_id,
        bucket=settings.bucket,
        object_key=object_key,
        original_name=logical_name or (file.filename or "unnamed"),
        content_type=file.content_type,
        size_bytes=size,
        sha256_hex=h.hexdigest(),
        created_at=datetime.utcnow(),
    )
    db.add(row)
    db.commit()

    return {
        "object_id": str(row.object_id),
        "user_id": row.user_id,
        "object_key": row.object_key,
        "name": row.original_name,
        "content_type": row.content_type,
        "size_bytes": row.size_bytes,
        "sha256": row.sha256_hex,
    }


@router.get("/{object_id}")
def download_object(object_id: str, db: Session = Depends(get_db)):
    try:
        object_uuid = uuid.UUID(object_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid object_id")

    row = db.get(ObjectMeta, object_uuid)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")

    obj = get_object_stream(row.object_key)

    # StreamingResponse supports streaming iterators/generators.
    def iterator():
        try:
            for chunk in obj.stream(CHUNK_SIZE):
                yield chunk
        finally:
            obj.close()
            obj.release_conn()

    headers = {"Content-Disposition": f'attachment; filename="{row.original_name}"'}
    return StreamingResponse(
        iterator(),
        media_type=row.content_type or "application/octet-stream",
        headers=headers,
    )
