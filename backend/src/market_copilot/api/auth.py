from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from market_copilot.api.dependencies import get_db_session
from market_copilot.auth.security import verify_password
from market_copilot.db.models import User


router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


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
