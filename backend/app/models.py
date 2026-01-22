import os
import uuid
from datetime import datetime

from sqlalchemy import Column, String, BigInteger, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID

from .db import Base


class ObjectMeta(Base):
    """
    Minimal metadata row for one stored object in MinIO.
    """
    __tablename__ = os.environ.get("POSTGRES_META_TB", "objects")
    
    object_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Text, nullable=True)
    bucket = Column(Text, nullable=False)
    folder = Column(String(255), nullable=True, index=True)
    object_key = Column(Text, nullable=False)
    
    original_name = Column(Text, nullable=False)
    current_name = Column(Text, nullable=False)
    
    content_type = Column(String, nullable=True)
    size_bytes = Column(BigInteger, nullable=False)
    sha256_hex = Column(String(64), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)