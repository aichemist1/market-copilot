from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

import secrets
from fastapi import APIRouter, Depends, Header, HTTPException, status
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


class InviteCodeResponse(BaseModel):
    code: str
    status: str
    expires_at: datetime | None
    used_at: datetime | None
    created_at: datetime
    created_by_email: EmailStr | None
    used_by_email: EmailStr | None


class CreateInviteCodeRequest(BaseModel):
    expires_days: int = 14
    code: str | None = None


def _build_invite_code() -> str:
    return f"MC-{secrets.token_urlsafe(8).upper()}"


def _require_admin_request(
    x_user_profile: str | None = Header(default=None),
    x_user_email: str | None = Header(default=None),
) -> str:
    if x_user_profile != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="admin access required",
        )
    if not x_user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="admin email header is required",
        )
    return x_user_email.lower()


def _map_invite(invite: InviteCode, users_by_id: dict[UUID, User]) -> InviteCodeResponse:
    created_by = users_by_id.get(invite.created_by_user_id) if invite.created_by_user_id else None
    used_by = users_by_id.get(invite.used_by_user_id) if invite.used_by_user_id else None
    return InviteCodeResponse(
        code=invite.code,
        status=invite.status,
        expires_at=invite.expires_at,
        used_at=invite.used_at,
        created_at=invite.created_at,
        created_by_email=created_by.email if created_by else None,
        used_by_email=used_by.email if used_by else None,
    )


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


@router.get("/invite-codes", response_model=list[InviteCodeResponse])
def list_invite_codes(
    db: Session = Depends(get_db_session),
    admin_email: str = Depends(_require_admin_request),
) -> list[InviteCodeResponse]:
    del admin_email
    invites = db.execute(
        select(InviteCode).order_by(InviteCode.created_at.desc()).limit(50)
    ).scalars().all()
    user_ids = {
        user_id
        for invite in invites
        for user_id in (invite.created_by_user_id, invite.used_by_user_id)
        if user_id is not None
    }
    users_by_id = {
        user.id: user
        for user in db.execute(select(User).where(User.id.in_(user_ids))).scalars().all()
    } if user_ids else {}
    return [_map_invite(invite, users_by_id) for invite in invites]


@router.post("/invite-codes", response_model=InviteCodeResponse, status_code=status.HTTP_201_CREATED)
def create_invite_code(
    payload: CreateInviteCodeRequest,
    db: Session = Depends(get_db_session),
    admin_email: str = Depends(_require_admin_request),
) -> InviteCodeResponse:
    creator = db.execute(select(User).where(User.email == admin_email)).scalar_one_or_none()
    if creator is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="admin user was not found",
        )

    code = (payload.code or _build_invite_code()).strip().upper()
    existing = db.execute(select(InviteCode).where(InviteCode.code == code)).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="invite code already exists",
        )

    expires_at = None
    if payload.expires_days > 0:
        expires_at = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(days=payload.expires_days)

    invite = InviteCode(
        code=code,
        created_by_user_id=creator.id,
        status="active",
        expires_at=expires_at,
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)

    return _map_invite(invite, {creator.id: creator})


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
