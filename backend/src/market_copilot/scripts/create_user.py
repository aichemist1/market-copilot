from __future__ import annotations

import argparse

from market_copilot.auth.security import hash_password
from market_copilot.db.models import USER_PROFILES, User
from market_copilot.db.session import SessionLocal


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a Market Copilot user.")
    parser.add_argument("email")
    parser.add_argument("password")
    parser.add_argument("--profile", default="basic", choices=USER_PROFILES)
    args = parser.parse_args()

    normalized_email = args.email.strip().lower()

    with SessionLocal() as session:
        existing = session.query(User).filter(User.email == normalized_email).one_or_none()
        if existing is not None:
            raise SystemExit(f"user already exists: {normalized_email}")

        user = User(
            email=normalized_email,
            password_hash=hash_password(args.password),
            profile=args.profile,
            status="active",
        )
        session.add(user)
        session.commit()

    print(f"created {args.profile} user {normalized_email}")


if __name__ == "__main__":
    main()
