"""Add source locator to ingestion runs."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0002_source_locator"
down_revision = "0001_phase1_core_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("ingestion_runs")}
    if "source_locator" not in existing_columns:
        op.add_column("ingestion_runs", sa.Column("source_locator", sa.Text(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("ingestion_runs")}
    if "source_locator" in existing_columns:
        op.drop_column("ingestion_runs", "source_locator")
