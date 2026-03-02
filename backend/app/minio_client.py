import os
import uuid
from dataclasses import dataclass
from typing import BinaryIO, Optional
from minio import Minio


@dataclass(frozen=True)
class MinioSettings:
    access_key: str = os.environ.get("MINIO_ROOT_USER", "minioadmin")
    secret_key: str = os.environ.get("MINIO_ROOT_PASSWORD", "minioadmin")
    bucket: str = os.environ.get("MINIO_BUCKET", "drive-files")
    secure: bool = os.environ.get("MINIO_SECURE", "false").lower == "true"
    port: str = os.environ.get("MINIO_API_PORT", "9000")
    host: str = os.environ.get("MINIO_HOST", "minio")
    endpoint = f"{host}:{port}"


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


def make_file_key(user_id: uuid.UUID | str, file_uuid: Optional[uuid.UUID] = None) -> str:
    """
    Returns an S3-style file key like: "{user_id}/{uuid}".
    """
    u = file_uuid or uuid.uuid4()
    return f"{user_id}/{u}"


def put_bytes(
    file_key: str,
    data: BinaryIO,
    *,
    length: int,
    content_type: str = "application/octet-stream",
    part_size: int = 10 * 1024 * 1024,
    metadata: Optional[dict] = None,
) -> None:
    """
    Upload bytes as an file.
    - If you don't know length, pass length=-1 and keep a valid part_size
      (MinIO supports multipart uploads this way).
    """
    ensure_bucket()
    client.put_object(
        settings.bucket,
        file_key,
        data,
        length=length,
        part_size=part_size if length == -1 else 0,
        content_type=content_type,
        metadata=metadata,
    )


def get_file_stream(file_key: str):
    """
    Returns a MinIO response file for streaming.
    Caller must close() and release_conn() when done.
    """
    ensure_bucket()
    return client.get_object(settings.bucket, file_key)


def delete_file(file_key: str) -> None:
    """
    Delete an file from MinIO storage.
    
    Args:
        file_key: The S3-style file key to delete (e.g., "user_id/uuid")
    
    Raises:
        Exception: If the file doesn't exist or deletion fails
    """
    ensure_bucket()
    client.remove_object(settings.bucket, file_key)