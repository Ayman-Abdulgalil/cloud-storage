from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..db import get_db
from ..models import (
    User,
    RefreshToken,
    UserRegister,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
)
from .auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from .dependencies import CurrentUser

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserRegister, db: Annotated[Session, Depends(get_db)]):
    """
    Register a new user account.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        name=user_data.name,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Annotated[Session, Depends(get_db)]):
    """
    Login and receive access and refresh tokens.
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, str(user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Update last login
    user.last_login = datetime.now(timezone.utc)  # type: ignore

    # Create tokens
    access_token = create_access_token(str(user.user_id), str(user.email))
    refresh_token, refresh_expires = create_refresh_token(str(user.user_id))

    # Store refresh token in database
    refresh_token_record = RefreshToken(
        user_id=user.user_id,
        token_hash=hash_token(refresh_token),
        expires_at=refresh_expires,
    )
    db.add(refresh_token_record)
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    token_data: RefreshTokenRequest, db: Annotated[Session, Depends(get_db)]
):
    """
    Refresh an access token using a refresh token.
    """
    # Decode refresh token
    payload = decode_token(token_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    # Check if token exists in database and is not revoked
    token_hash = hash_token(token_data.refresh_token)
    stored_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == token_hash, RefreshToken.revoked.is_(False))
        .first()
    )

    if stored_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found or revoked",
        )

    # Check if token is expired
    if stored_token.expires_at < datetime.now(timezone.utc):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired"
        )

    # Get user
    user = db.query(User).filter(User.user_id == stored_token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    # Create new tokens
    access_token = create_access_token(str(user.user_id), str(user.email))
    new_refresh_token, refresh_expires = create_refresh_token(str(user.user_id))

    # Revoke old refresh token and create new one
    stored_token.revoked = True  # type: ignore
    new_refresh_token_record = RefreshToken(
        user_id=user.user_id,
        token_hash=hash_token(new_refresh_token),
        expires_at=refresh_expires,
    )
    db.add(new_refresh_token_record)
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    token_data: RefreshTokenRequest,
    current_user: CurrentUser, 
    db: Annotated[Session, Depends(get_db)]
):
    """
    Logout by revoking refresh token(s).
    """
    if token_data and token_data.refresh_token:
        # Revoke specific token
        token_hash = hash_token(token_data.refresh_token)
        db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.user_id == current_user.user_id
        ).update({"revoked": True})
    else:
        # Revoke all tokens
        db.query(RefreshToken).filter(
            RefreshToken.user_id == current_user.user_id,
            RefreshToken.revoked.is_(False)
        ).update({"revoked": True})
    
    db.commit()
    return None

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser):
    """
    Get current authenticated user information.
    """
    return current_user
