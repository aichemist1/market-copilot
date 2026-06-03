"""Add queue lifecycle fields to normalization jobs."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0003_job_queue_fields"
down_revision = "0002_source_locator"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("normalization_jobs")}

    if "queued_at" not in existing_columns:
        op.add_column(
            "normalization_jobs",
            sa.Column("queued_at", sa.DateTime(timezone=True), nullable=True),
        )
        op.execute("UPDATE normalization_jobs SET queued_at = started_at")
        op.alter_column("normalization_jobs", "queued_at", nullable=False)

    started_at_column = next(
        (column for column in inspector.get_columns("normalization_jobs") if column["name"] == "started_at"),
        None,
    )
    if started_at_column is not None and started_at_column.get("nullable") is False:
        op.alter_column("normalization_jobs", "started_at", nullable=True)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("normalization_jobs")}
    started_at_column = next(
        (column for column in inspector.get_columns("normalization_jobs") if column["name"] == "started_at"),
        None,
    )
    if started_at_column is not None and started_at_column.get("nullable") is True:
        op.alter_column("normalization_jobs", "started_at", nullable=False)
    if "queued_at" in existing_columns:
        op.drop_column("normalization_jobs", "queued_at")
