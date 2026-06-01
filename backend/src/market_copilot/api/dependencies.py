from __future__ import annotations

from collections.abc import Generator

from market_copilot.db.session import SessionLocal


def get_db_session() -> Generator:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
