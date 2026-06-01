"""Add queue lifecycle fields to normalization jobs."""

from alembic import op
import sqlalchemy as sa


revision = "0003_job_queue_fields"
down_revision = "0002_source_locator"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "normalization_jobs",
        sa.Column("queued_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute("UPDATE normalization_jobs SET queued_at = started_at")
    op.alter_column("normalization_jobs", "queued_at", nullable=False)
    op.alter_column("normalization_jobs", "started_at", nullable=True)


def downgrade() -> None:
    op.alter_column("normalization_jobs", "started_at", nullable=False)
    op.drop_column("normalization_jobs", "queued_at")
