from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from market_copilot.db.models import CongressionalFiling, CongressionalTransaction, IngestionRun, ValidationResult
from market_copilot.domain.congressional.constants import (
    DOMAIN_RELEASE_PUBLISHED,
    PUBLICATION_STATUS_PUBLISHED,
)


PRODUCT_TRANSACTION_START_DATE = date(2026, 1, 1)


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
        .where(
            CongressionalFiling.transactions.any(
                CongressionalTransaction.transaction_date >= PRODUCT_TRANSACTION_START_DATE
            )
        )
        .order_by(CongressionalFiling.filing_date.desc(), CongressionalFiling.created_at.desc())
        .limit(limit)
    )

    if reporting_person:
        stmt = stmt.where(CongressionalFiling.reporting_person.ilike(f"%{reporting_person}%"))

    if ticker:
        stmt = stmt.where(
            CongressionalFiling.transactions.any(
                (CongressionalTransaction.ticker == ticker.upper())
                & (CongressionalTransaction.transaction_date >= PRODUCT_TRANSACTION_START_DATE)
            )
        )

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
        .where(
            CongressionalFiling.transactions.any(
                CongressionalTransaction.transaction_date >= PRODUCT_TRANSACTION_START_DATE
            )
        )
    )
    return session.execute(stmt).scalars().unique().one_or_none()


def list_congressional_transactions(
    session: Session,
    *,
    ticker: str | None = None,
    reporting_person: str | None = None,
    transaction_type: str | None = None,
    asset_type: str | None = None,
    transaction_date_from: date | None = None,
    transaction_date_to: date | None = None,
    limit: int = 50,
) -> list[CongressionalTransaction]:
    date_from = transaction_date_from or PRODUCT_TRANSACTION_START_DATE

    stmt = (
        select(CongressionalTransaction)
        .options(joinedload(CongressionalTransaction.filing))
        .join(CongressionalTransaction.filing)
        .where(CongressionalFiling.publication_status == PUBLICATION_STATUS_PUBLISHED)
        .where(CongressionalFiling.domain_release_state == DOMAIN_RELEASE_PUBLISHED)
        .where(CongressionalTransaction.publication_status == PUBLICATION_STATUS_PUBLISHED)
        .where(CongressionalTransaction.transaction_date.is_not(None))
        .where(CongressionalTransaction.transaction_date >= date_from)
        .order_by(CongressionalTransaction.transaction_date.desc(), CongressionalTransaction.created_at.desc())
        .limit(limit)
    )

    if transaction_date_to:
        stmt = stmt.where(CongressionalTransaction.transaction_date <= transaction_date_to)
    if reporting_person:
        stmt = stmt.where(CongressionalFiling.reporting_person.ilike(f"%{reporting_person}%"))
    if ticker:
        stmt = stmt.where(CongressionalTransaction.ticker == ticker.upper())
    if transaction_type:
        stmt = stmt.where(CongressionalTransaction.transaction_type == transaction_type)
    if asset_type:
        stmt = stmt.where(CongressionalTransaction.asset_type == asset_type)

    return list(session.execute(stmt).scalars().unique())


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
