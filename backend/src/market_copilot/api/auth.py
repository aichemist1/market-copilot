from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from market_copilot.api.dependencies import get_db_session
from market_copilot.auth.security import hash_password, verify_password
from market_copilot.db.models import InviteCode, User


router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    invite_code: str


class AuthenticatedUserResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    profile: str


@router.post("/login", response_model=AuthenticatedUserResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db_session)) -> AuthenticatedUserResponse:
    user = db.execute(select(User).where(User.email == payload.email.lower())).scalar_one_or_none()
    if user is None or user.status != "active" or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid credentials",
        )

    return AuthenticatedUserResponse(
        user_id=user.id,
        email=user.email,
        profile=user.profile,
    )


@router.post("/register", response_model=AuthenticatedUserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db_session)) -> AuthenticatedUserResponse:
    normalized_email = payload.email.lower()
    existing_user = db.execute(select(User).where(User.email == normalized_email)).scalar_one_or_none()
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email is already registered",
        )

    invite = db.execute(
        select(InviteCode).where(InviteCode.code == payload.invite_code.strip())
    ).scalar_one_or_none()
    if invite is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="invite code was not found",
        )

    now = datetime.now(timezone.utc)
    if invite.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invite code is not active",
        )
    if invite.expires_at is not None and invite.expires_at <= now:
        invite.status = "expired"
        db.add(invite)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invite code has expired",
        )

    user = User(
        email=normalized_email,
        password_hash=hash_password(payload.password),
        profile="basic",
        status="active",
    )
    db.add(user)
    db.flush()

    invite.used_by_user_id = user.id
    invite.used_at = now
    invite.status = "used"
    db.add(invite)
    db.commit()

    return AuthenticatedUserResponse(
        user_id=user.id,
        email=user.email,
        profile=user.profile,
    )
