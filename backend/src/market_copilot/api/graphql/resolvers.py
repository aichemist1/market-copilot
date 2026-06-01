from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from market_copilot.db.models import CongressionalFiling, IngestionRun, ValidationResult
from market_copilot.domain.congressional.constants import (
    DOMAIN_RELEASE_PUBLISHED,
    PUBLICATION_STATUS_PUBLISHED,
)


def list_congressional_filings(
    session: Session,
    *,
    ticker: str | None = None,
    reporting_person: str | None = None,
    limit: int = 50,
) -> list[CongressionalFiling]:
    stmt = (
        select(CongressionalFiling)
        .options(selectinload(CongressionalFiling.transactions))
        .where(CongressionalFiling.publication_status == PUBLICATION_STATUS_PUBLISHED)
        .where(CongressionalFiling.domain_release_state == DOMAIN_RELEASE_PUBLISHED)
        .order_by(CongressionalFiling.filing_date.desc(), CongressionalFiling.created_at.desc())
        .limit(limit)
    )

    if reporting_person:
        stmt = stmt.where(CongressionalFiling.reporting_person.ilike(f"%{reporting_person}%"))

    if ticker:
        stmt = stmt.where(CongressionalFiling.transactions.any(ticker=ticker.upper()))

    return list(session.execute(stmt).scalars().unique())


def get_congressional_filing_by_source_record_id(
    session: Session,
    *,
    source_record_id: str,
) -> CongressionalFiling | None:
    stmt = (
        select(CongressionalFiling)
        .options(selectinload(CongressionalFiling.transactions))
        .where(CongressionalFiling.source_record_id == source_record_id)
        .where(CongressionalFiling.publication_status == PUBLICATION_STATUS_PUBLISHED)
        .where(CongressionalFiling.domain_release_state == DOMAIN_RELEASE_PUBLISHED)
    )
    return session.execute(stmt).scalars().unique().one_or_none()


def list_recent_ingestion_runs(session: Session, *, limit: int = 20) -> list[IngestionRun]:
    stmt = select(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(limit)
    return list(session.execute(stmt).scalars())


def list_recent_validation_results(
    session: Session,
    *,
    status: str | None = None,
    limit: int = 50,
) -> list[ValidationResult]:
    stmt = select(ValidationResult).order_by(ValidationResult.validated_at.desc()).limit(limit)
    if status:
        stmt = stmt.where(ValidationResult.status == status)
    return list(session.execute(stmt).scalars())
