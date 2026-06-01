"""Create Phase 1 congressional core schema."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0001_phase1_core_schema"
down_revision = None
branch_labels = None
depends_on = None


SOURCE_TYPES = ("congressional_house_ptr",)
USER_PROFILES = ("basic", "premium", "admin")
USER_STATUSES = ("active", "disabled", "pending_invite")
INVITE_STATUSES = ("active", "used", "expired", "disabled")
RUN_TYPES = ("scheduled", "manual", "recovery")
RUN_STATUSES = ("running", "completed", "completed_with_errors", "failed")
DOCUMENT_TYPES = (
    "house_xml",
    "ptr_pdf",
    "extracted_text",
    "normalization_input",
    "normalization_output",
)
EXTRACTION_STATUSES = ("not_started", "completed", "failed", "skipped")
PUBLICATION_STATUSES = ("draft", "published", "failed_validation", "archived")
RELEASE_STATES = ("development", "admin_preview", "published", "disabled")
NORMALIZATION_JOB_STATUSES = ("queued", "running", "completed", "failed")
VALIDATION_ENTITY_TYPES = ("filing", "transaction_batch")
VALIDATION_STATUSES = ("passed", "failed", "passed_with_warnings")


def _sql_in(values: tuple[str, ...]) -> str:
    quoted = ", ".join(f"'{value}'" for value in values)
    return f"({quoted})"


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("profile", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(f"profile IN {_sql_in(USER_PROFILES)}", name="ck_users_profile_allowed"),
        sa.CheckConstraint(f"status IN {_sql_in(USER_STATUSES)}", name="ck_users_status_allowed"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    op.create_table(
        "invite_codes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("used_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(f"status IN {_sql_in(INVITE_STATUSES)}", name="ck_invite_codes_status_allowed"),
        sa.UniqueConstraint("code", name="uq_invite_codes_code"),
    )

    op.create_table(
        "ingestion_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("run_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("files_discovered_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("files_downloaded_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_normalized_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_published_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_summary", sa.Text(), nullable=True),
        sa.Column("source_locator", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(f"source_type IN {_sql_in(SOURCE_TYPES)}", name="ck_ingestion_runs_source_type_allowed"),
        sa.CheckConstraint(f"run_type IN {_sql_in(RUN_TYPES)}", name="ck_ingestion_runs_run_type_allowed"),
        sa.CheckConstraint(f"status IN {_sql_in(RUN_STATUSES)}", name="ck_ingestion_runs_status_allowed"),
    )
    op.create_index("ix_ingestion_runs_started_at", "ingestion_runs", ["started_at"])
    op.create_index("ix_ingestion_runs_source_started_at", "ingestion_runs", ["source_type", "started_at"])

    op.create_table(
        "source_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("source_record_id", sa.Text(), nullable=True),
        sa.Column("document_type", sa.String(length=64), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("storage_key", sa.Text(), nullable=False),
        sa.Column("checksum", sa.Text(), nullable=True),
        sa.Column("mime_type", sa.String(length=255), nullable=True),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("extraction_status", sa.String(length=32), nullable=False, server_default="not_started"),
        sa.Column("extracted_text_storage_key", sa.Text(), nullable=True),
        sa.Column("ingestion_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ingestion_runs.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(f"source_type IN {_sql_in(SOURCE_TYPES)}", name="ck_source_documents_source_type_allowed"),
        sa.CheckConstraint(f"document_type IN {_sql_in(DOCUMENT_TYPES)}", name="ck_source_documents_document_type_allowed"),
        sa.CheckConstraint(
            f"extraction_status IN {_sql_in(EXTRACTION_STATUSES)}",
            name="ck_source_documents_extraction_status_allowed",
        ),
        sa.UniqueConstraint("storage_key", name="uq_source_documents_storage_key"),
    )
    op.create_index("ix_source_documents_source_record", "source_documents", ["source_type", "source_record_id"])
    op.create_index("ix_source_documents_ingestion_run_id", "source_documents", ["ingestion_run_id"])

    op.create_table(
        "congressional_filings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("source_record_id", sa.Text(), nullable=False),
        sa.Column("filing_type", sa.Text(), nullable=False),
        sa.Column("reporting_status", sa.Text(), nullable=True),
        sa.Column("filing_date", sa.Date(), nullable=True),
        sa.Column("disclosure_date", sa.Date(), nullable=True),
        sa.Column("filing_status", sa.Text(), nullable=True),
        sa.Column("reporting_person", sa.Text(), nullable=False),
        sa.Column("office", sa.Text(), nullable=True),
        sa.Column("district_or_state", sa.Text(), nullable=True),
        sa.Column("source_document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("source_documents.id"), nullable=True),
        sa.Column("source_document_url", sa.Text(), nullable=False),
        sa.Column("publication_status", sa.String(length=32), nullable=False, server_default="published"),
        sa.Column("domain_release_state", sa.String(length=32), nullable=False, server_default="published"),
        sa.Column("normalization_version", sa.String(length=64), nullable=False),
        sa.Column("model_name", sa.String(length=128), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(f"source_type IN {_sql_in(SOURCE_TYPES)}", name="ck_congressional_filings_source_type_allowed"),
        sa.CheckConstraint(
            f"publication_status IN {_sql_in(PUBLICATION_STATUSES)}",
            name="ck_congressional_filings_publication_status_allowed",
        ),
        sa.CheckConstraint(
            f"domain_release_state IN {_sql_in(RELEASE_STATES)}",
            name="ck_congressional_filings_domain_release_state_allowed",
        ),
        sa.UniqueConstraint("source_type", "source_record_id", name="uq_congressional_filings_source_record"),
    )
    op.create_index("ix_congressional_filings_reporting_person", "congressional_filings", ["reporting_person"])
    op.create_index("ix_congressional_filings_filing_date", "congressional_filings", ["filing_date"])
    op.create_index(
        "ix_congressional_filings_publication_status",
        "congressional_filings",
        ["publication_status"],
    )
    op.create_index(
        "ix_congressional_filings_domain_release_state",
        "congressional_filings",
        ["domain_release_state"],
    )

    op.create_table(
        "congressional_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "filing_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("congressional_filings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("transaction_index", sa.Integer(), nullable=False),
        sa.Column("issuer_name", sa.Text(), nullable=False),
        sa.Column("ticker", sa.String(length=32), nullable=True),
        sa.Column("asset_type", sa.String(length=64), nullable=True),
        sa.Column("transaction_type", sa.String(length=64), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=True),
        sa.Column("notification_date", sa.Date(), nullable=True),
        sa.Column("amount_range", sa.String(length=128), nullable=True),
        sa.Column("amount_range_min", sa.Numeric(18, 2), nullable=True),
        sa.Column("amount_range_max", sa.Numeric(18, 2), nullable=True),
        sa.Column("owner_type", sa.String(length=64), nullable=True),
        sa.Column("subholding", sa.Text(), nullable=True),
        sa.Column("capital_gains_over_200", sa.Boolean(), nullable=True),
        sa.Column("commentary", sa.Text(), nullable=True),
        sa.Column("raw_text_reference", sa.Text(), nullable=True),
        sa.Column("publication_status", sa.String(length=32), nullable=False, server_default="published"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("transaction_index >= 0", name="ck_congressional_transactions_transaction_index_non_negative"),
        sa.CheckConstraint(
            f"publication_status IN {_sql_in(PUBLICATION_STATUSES)}",
            name="ck_congressional_transactions_publication_status_allowed",
        ),
        sa.UniqueConstraint("filing_id", "transaction_index", name="uq_congressional_transactions_filing_index"),
    )
    op.create_index("ix_congressional_transactions_ticker", "congressional_transactions", ["ticker"])
    op.create_index("ix_congressional_transactions_issuer_name", "congressional_transactions", ["issuer_name"])
    op.create_index(
        "ix_congressional_transactions_transaction_date",
        "congressional_transactions",
        ["transaction_date"],
    )
    op.create_index(
        "ix_congressional_transactions_transaction_type",
        "congressional_transactions",
        ["transaction_type"],
    )

    op.create_table(
        "normalization_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "source_document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("source_documents.id"),
            nullable=False,
        ),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("normalization_version", sa.String(length=64), nullable=False),
        sa.Column("model_name", sa.String(length=128), nullable=False),
        sa.Column("prompt_version", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("input_reference", sa.Text(), nullable=True),
        sa.Column("output_reference", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("queued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(f"source_type IN {_sql_in(SOURCE_TYPES)}", name="ck_normalization_jobs_source_type_allowed"),
        sa.CheckConstraint(
            f"status IN {_sql_in(NORMALIZATION_JOB_STATUSES)}",
            name="ck_normalization_jobs_status_allowed",
        ),
    )
    op.create_index("ix_normalization_jobs_source_document_id", "normalization_jobs", ["source_document_id"])
    op.create_index("ix_normalization_jobs_status_started_at", "normalization_jobs", ["status", "started_at"])

    op.create_table(
        "validation_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("source_record_id", sa.Text(), nullable=False),
        sa.Column("entity_type", sa.String(length=32), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("validation_version", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("errors_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("warnings_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(f"source_type IN {_sql_in(SOURCE_TYPES)}", name="ck_validation_results_source_type_allowed"),
        sa.CheckConstraint(
            f"entity_type IN {_sql_in(VALIDATION_ENTITY_TYPES)}",
            name="ck_validation_results_entity_type_allowed",
        ),
        sa.CheckConstraint(
            f"status IN {_sql_in(VALIDATION_STATUSES)}",
            name="ck_validation_results_status_allowed",
        ),
    )
    op.create_index(
        "ix_validation_results_source_record_validated_at",
        "validation_results",
        ["source_record_id", "validated_at"],
    )
    op.create_index("ix_validation_results_status", "validation_results", ["status"])


def downgrade() -> None:
    op.drop_index("ix_validation_results_status", table_name="validation_results")
    op.drop_index("ix_validation_results_source_record_validated_at", table_name="validation_results")
    op.drop_table("validation_results")

    op.drop_index("ix_normalization_jobs_status_started_at", table_name="normalization_jobs")
    op.drop_index("ix_normalization_jobs_source_document_id", table_name="normalization_jobs")
    op.drop_table("normalization_jobs")

    op.drop_index("ix_congressional_transactions_transaction_type", table_name="congressional_transactions")
    op.drop_index("ix_congressional_transactions_transaction_date", table_name="congressional_transactions")
    op.drop_index("ix_congressional_transactions_issuer_name", table_name="congressional_transactions")
    op.drop_index("ix_congressional_transactions_ticker", table_name="congressional_transactions")
    op.drop_table("congressional_transactions")

    op.drop_index("ix_congressional_filings_domain_release_state", table_name="congressional_filings")
    op.drop_index("ix_congressional_filings_publication_status", table_name="congressional_filings")
    op.drop_index("ix_congressional_filings_filing_date", table_name="congressional_filings")
    op.drop_index("ix_congressional_filings_reporting_person", table_name="congressional_filings")
    op.drop_table("congressional_filings")

    op.drop_index("ix_source_documents_ingestion_run_id", table_name="source_documents")
    op.drop_index("ix_source_documents_source_record", table_name="source_documents")
    op.drop_table("source_documents")

    op.drop_index("ix_ingestion_runs_source_started_at", table_name="ingestion_runs")
    op.drop_index("ix_ingestion_runs_started_at", table_name="ingestion_runs")
    op.drop_table("ingestion_runs")

    op.drop_table("invite_codes")
    op.drop_table("users")
