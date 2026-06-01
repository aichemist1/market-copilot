from market_copilot.db.base import Base
from market_copilot.db.session import engine
from market_copilot.db import models  # noqa: F401


def create_all_tables() -> None:
    """Create all database tables directly from metadata.

    This is useful for local exploration. Alembic remains the authoritative
    migration path for managed environments.
    """

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_all_tables()
