from __future__ import annotations

import argparse
import secrets
from datetime import datetime, timedelta, timezone

from market_copilot.db.models import InviteCode, User
from market_copilot.db.session import SessionLocal


def build_code() -> str:
    return f"MC-{secrets.token_urlsafe(8).upper()}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a Market Copilot invite code.")
    parser.add_argument("--code", help="Optional explicit invite code value.")
    parser.add_argument("--expires-days", type=int, default=14)
    parser.add_argument("--created-by-email")
    args = parser.parse_args()

    code = (args.code or build_code()).strip()
    expires_at = None
    if args.expires_days > 0:
        expires_at = datetime.now(timezone.utc) + timedelta(days=args.expires_days)

    with SessionLocal() as session:
        existing = session.query(InviteCode).filter(InviteCode.code == code).one_or_none()
        if existing is not None:
            raise SystemExit(f"invite code already exists: {code}")

        created_by_user_id = None
        if args.created_by_email:
            creator = (
                session.query(User)
                .filter(User.email == args.created_by_email.strip().lower())
                .one_or_none()
            )
            if creator is None:
                raise SystemExit(f"creator not found: {args.created_by_email}")
            created_by_user_id = creator.id

        invite = InviteCode(
            code=code,
            created_by_user_id=created_by_user_id,
            status="active",
            expires_at=expires_at,
        )
        session.add(invite)
        session.commit()

    print(code)


if __name__ == "__main__":
    main()
