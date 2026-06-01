from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from market_copilot.db.base import Base


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


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            f"profile IN {_sql_in(USER_PROFILES)}",
            name="profile_allowed",
        ),
        CheckConstraint(
            f"status IN {_sql_in(USER_STATUSES)}",
            name="status_allowed",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    profile: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active", server_default="active")


class InviteCode(Base):
    __tablename__ = "invite_codes"
    __table_args__ = (
        CheckConstraint(
            f"status IN {_sql_in(INVITE_STATUSES)}",
            name="status_allowed",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    used_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active", server_default="active")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"
    __table_args__ = (
        CheckConstraint(
            f"source_type IN {_sql_in(SOURCE_TYPES)}",
            name="source_type_allowed",
        ),
        CheckConstraint(
            f"run_type IN {_sql_in(RUN_TYPES)}",
            name="run_type_allowed",
        ),
        CheckConstraint(
            f"status IN {_sql_in(RUN_STATUSES)}",
            name="status_allowed",
        ),
        Index("ix_ingestion_runs_started_at", "started_at"),
        Index("ix_ingestion_runs_source_started_at", "source_type", "started_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    run_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    files_discovered_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    files_downloaded_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    records_normalized_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    records_published_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    error_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_locator: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class SourceDocument(Base):
    __tablename__ = "source_documents"
    __table_args__ = (
        CheckConstraint(
            f"source_type IN {_sql_in(SOURCE_TYPES)}",
            name="source_type_allowed",
        ),
        CheckConstraint(
            f"document_type IN {_sql_in(DOCUMENT_TYPES)}",
            name="document_type_allowed",
        ),
        CheckConstraint(
            f"extraction_status IN {_sql_in(EXTRACTION_STATUSES)}",
            name="extraction_status_allowed",
        ),
        Index("ix_source_documents_source_record", "source_type", "source_record_id"),
        Index("ix_source_documents_ingestion_run_id", "ingestion_run_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_record_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    storage_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    checksum: Mapped[str | None] = mapped_column(Text, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    extraction_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="not_started", server_default="not_started"
    )
    extracted_text_storage_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    ingestion_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ingestion_runs.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    ingestion_run: Mapped["IngestionRun | None"] = relationship()


class CongressionalFiling(Base, TimestampMixin):
    __tablename__ = "congressional_filings"
    __table_args__ = (
        UniqueConstraint("source_type", "source_record_id", name="uq_congressional_filings_source_record"),
        CheckConstraint(
            f"source_type IN {_sql_in(SOURCE_TYPES)}",
            name="source_type_allowed",
        ),
        CheckConstraint(
            f"publication_status IN {_sql_in(PUBLICATION_STATUSES)}",
            name="publication_status_allowed",
        ),
        CheckConstraint(
            f"domain_release_state IN {_sql_in(RELEASE_STATES)}",
            name="domain_release_state_allowed",
        ),
        Index("ix_congressional_filings_reporting_person", "reporting_person"),
        Index("ix_congressional_filings_filing_date", "filing_date"),
        Index("ix_congressional_filings_publication_status", "publication_status"),
        Index("ix_congressional_filings_domain_release_state", "domain_release_state"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_record_id: Mapped[str] = mapped_column(Text, nullable=False)
    filing_type: Mapped[str] = mapped_column(Text, nullable=False)
    reporting_status: Mapped[str | None] = mapped_column(Text, nullable=True)
    filing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    disclosure_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    filing_status: Mapped[str | None] = mapped_column(Text, nullable=True)
    reporting_person: Mapped[str] = mapped_column(Text, nullable=False)
    office: Mapped[str | None] = mapped_column(Text, nullable=True)
    district_or_state: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("source_documents.id"), nullable=True
    )
    source_document_url: Mapped[str] = mapped_column(Text, nullable=False)
    publication_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="published", server_default="published"
    )
    domain_release_state: Mapped[str] = mapped_column(
        String(32), nullable=False, default="published", server_default="published"
    )
    normalization_version: Mapped[str] = mapped_column(String(64), nullable=False)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    source_document: Mapped["SourceDocument | None"] = relationship()
    transactions: Mapped[list["CongressionalTransaction"]] = relationship(
        back_populates="filing",
        cascade="all, delete-orphan",
    )


class CongressionalTransaction(Base, TimestampMixin):
    __tablename__ = "congressional_transactions"
    __table_args__ = (
        UniqueConstraint("filing_id", "transaction_index", name="uq_congressional_transactions_filing_index"),
        CheckConstraint("transaction_index >= 0", name="transaction_index_non_negative"),
        CheckConstraint(
            f"publication_status IN {_sql_in(PUBLICATION_STATUSES)}",
            name="publication_status_allowed",
        ),
        Index("ix_congressional_transactions_ticker", "ticker"),
        Index("ix_congressional_transactions_issuer_name", "issuer_name"),
        Index("ix_congressional_transactions_transaction_date", "transaction_date"),
        Index("ix_congressional_transactions_transaction_type", "transaction_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("congressional_filings.id", ondelete="CASCADE"), nullable=False
    )
    transaction_index: Mapped[int] = mapped_column(Integer, nullable=False)
    issuer_name: Mapped[str] = mapped_column(Text, nullable=False)
    ticker: Mapped[str | None] = mapped_column(String(32), nullable=True)
    asset_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    transaction_type: Mapped[str] = mapped_column(String(64), nullable=False)
    transaction_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notification_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    amount_range: Mapped[str | None] = mapped_column(String(128), nullable=True)
    amount_range_min: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    amount_range_max: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    owner_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    subholding: Mapped[str | None] = mapped_column(Text, nullable=True)
    capital_gains_over_200: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    commentary: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_text_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    publication_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="published", server_default="published"
    )

    filing: Mapped["CongressionalFiling"] = relationship(back_populates="transactions")


class NormalizationJob(Base):
    __tablename__ = "normalization_jobs"
    __table_args__ = (
        CheckConstraint(
            f"source_type IN {_sql_in(SOURCE_TYPES)}",
            name="source_type_allowed",
        ),
        CheckConstraint(
            f"status IN {_sql_in(NORMALIZATION_JOB_STATUSES)}",
            name="status_allowed",
        ),
        Index("ix_normalization_jobs_source_document_id", "source_document_id"),
        Index("ix_normalization_jobs_status_started_at", "status", "started_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("source_documents.id"), nullable=False
    )
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    normalization_version: Mapped[str] = mapped_column(String(64), nullable=False)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    input_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    queued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    source_document: Mapped["SourceDocument"] = relationship()


class ValidationResult(Base):
    __tablename__ = "validation_results"
    __table_args__ = (
        CheckConstraint(
            f"source_type IN {_sql_in(SOURCE_TYPES)}",
            name="source_type_allowed",
        ),
        CheckConstraint(
            f"entity_type IN {_sql_in(VALIDATION_ENTITY_TYPES)}",
            name="entity_type_allowed",
        ),
        CheckConstraint(
            f"status IN {_sql_in(VALIDATION_STATUSES)}",
            name="status_allowed",
        ),
        Index("ix_validation_results_source_record_validated_at", "source_record_id", "validated_at"),
        Index("ix_validation_results_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_record_id: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    validation_version: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    errors_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    warnings_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    validated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
