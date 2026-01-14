# storage/minio_client.py
import os
import uuid
from dataclasses import dataclass
from typing import BinaryIO, Optional

from minio import Minio


@dataclass(frozen=True)
class MinioSettings:
    endpoint: str = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
    access_key: str = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
    secret_key: str = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
    bucket: str = os.environ.get("MINIO_BUCKET", "drive-objects")
    secure: bool = os.environ.get("MINIO_SECURE", "0") == "1"


settings = MinioSettings()

client = Minio(
    settings.endpoint,
    access_key=settings.access_key,
    secret_key=settings.secret_key,
    secure=settings.secure,
)  # Constructor signature is documented by MinIO.


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
    )  # put_object params (length, part_size, etc.) are documented.


def get_object_stream(object_key: str):
    """
    Returns a MinIO response object for streaming.
    Caller must close() and release_conn() when done.
    """
    ensure_bucket()
    return client.get_object(settings.bucket, object_key)
