import os
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import (
    Column,
    String,
    BigInteger,
    DateTime,
    Text,
    ForeignKey,
    Index,
    Boolean,
)
from sqlalchemy.dialects.postgresql import UUID
from .db import Base


class User(Base):
    """
    User account with authentication and storage quota tracking.
    """

    __tablename__ = os.environ.get("POSTGRES_USERS_TB", "users")

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    last_login = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    storage_used = Column(BigInteger, nullable=False, default=0)
    storage_quota = Column(BigInteger, nullable=False, default=10737418240)  # 10GB


class ObjectMeta(Base):
    """
    Minimal metadata row for one stored object in MinIO.
    """

    __tablename__ = os.environ.get("POSTGRES_META_TB", "objects")

    object_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{User.__tablename__}.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    bucket = Column(Text, nullable=False)
    folder = Column(String(255), nullable=True, index=True)
    object_key = Column(Text, nullable=False)
    original_name = Column(Text, nullable=False)
    current_name = Column(Text, nullable=False)
    content_type = Column(String(255), nullable=True)
    size_bytes = Column(BigInteger, nullable=False)
    sha256_hex = Column(String(64), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Composite index for common query pattern
    __table_args__ = (Index("idx_objects_user_folder", "user_id", "folder"),)


class RefreshToken(Base):
    """
    Refresh tokens for JWT authentication.
    """

    __tablename__ = os.environ.get("POSTGRES_REFRESH_TOKENS_TB", "refresh_tokens")

    token_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            f'{os.environ.get("POSTGRES_USERS_TB", "users")}.user_id',
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    token_hash = Column(
        String(64), nullable=False, unique=True, index=True
    )  # SHA-256 is 64 chars
    expires_at = Column(
        DateTime(timezone=True), nullable=False, index=True
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    revoked = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        Index("ix_refresh_tokens_user_active", "user_id", "revoked"),  # Composite index
    )


# Pydantic Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    user_id: uuid.UUID
    email: str
    name: str
    created_at: datetime
    storage_used: int
    storage_quota: int

    class Config:
        from_attributes = True
