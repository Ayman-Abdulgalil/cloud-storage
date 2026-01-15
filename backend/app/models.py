import uuid
from datetime import datetime

from sqlalchemy import Column, String, BigInteger, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID

from .db import Base


class ObjectMeta(Base):
    """
    Minimal metadata row for one stored object in MinIO.
    """
    __tablename__ = "objects"

    # Use Postgres UUID type; generate UUID in Python by default.
    object_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Who owns it (placeholder until AAA); store as text for now.
    user_id = Column(Text, nullable=True)

    # Where the bytes live in object storage
    bucket = Column(Text, nullable=False)
    object_key = Column(Text, nullable=False)  # e.g., "{user_id}/{uuid}" or just "{uuid}"

    # Display / HTTP metadata
    original_name = Column(Text, nullable=False)
    content_type = Column(String, nullable=True)

    # Integrity + size
    size_bytes = Column(BigInteger, nullable=False)
    sha256_hex = Column(String(64), nullable=False)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
