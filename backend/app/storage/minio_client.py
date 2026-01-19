import os
import uuid
from dataclasses import dataclass
from typing import BinaryIO, Optional
from minio import Minio


@dataclass(frozen=True)
class MinioSettings:
    endpoint: str = os.environ.get("MINIO_ENDPOINT", "minio_storage:9000")
    access_key: str = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
    secret_key: str = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
    bucket: str = os.environ.get("MINIO_BUCKET", "drive-objects")
    secure: bool = os.environ.get("MINIO_SECURE", "false").lower == "true"


settings = MinioSettings()

client = Minio(
    endpoint=settings.endpoint,
    access_key=settings.access_key,
    secret_key=settings.secret_key,
    secure=settings.secure,
)


def ensure_bucket() -> None:
    if not client.bucket_exists(settings.bucket):
        client.make_bucket(settings.bucket)


def make_object_key(user_id: str, object_uuid: Optional[uuid.UUID] = None) -> str:
    """
    Returns an S3-style object key like: "{user_id}/{uuid}".
    """
    u = object_uuid or uuid.uuid4()
    return f"{user_id}/{u}"


def put_bytes(
    object_key: str,
    data: BinaryIO,
    *,
    length: int,
    content_type: str = "application/octet-stream",
    part_size: int = 10 * 1024 * 1024,
    metadata: Optional[dict] = None,
) -> None:
    """
    Upload bytes as an object.
    - If you don't know length, pass length=-1 and keep a valid part_size
      (MinIO supports multipart uploads this way).
    """
    ensure_bucket()
    client.put_object(
        settings.bucket,
        object_key,
        data,
        length=length,
        part_size=part_size if length == -1 else 0,
        content_type=content_type,
        metadata=metadata,
    )


def get_object_stream(object_key: str):
    """
    Returns a MinIO response object for streaming.
    Caller must close() and release_conn() when done.
    """
    ensure_bucket()
    return client.get_object(settings.bucket, object_key)


def delete_object(object_key: str) -> None:
    """
    Delete an object from MinIO storage.
    
    Args:
        object_key: The S3-style object key to delete (e.g., "user_id/uuid")
    
    Raises:
        Exception: If the object doesn't exist or deletion fails
    """
    ensure_bucket()
    client.remove_object(settings.bucket, object_key)