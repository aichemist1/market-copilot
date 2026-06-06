from __future__ import annotations

from datetime import date

from sqlalchemy import case, desc, func, select
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


def list_ticker_signals(
    session: Session,
    *,
    transaction_date_from: date | None = None,
    transaction_date_to: date | None = None,
    limit: int = 25,
) -> list[dict]:
    date_from = transaction_date_from or PRODUCT_TRANSACTION_START_DATE

    buy_count = func.sum(
        case((CongressionalTransaction.transaction_type == "purchase", 1), else_=0)
    ).label("buy_count")
    sell_count = func.sum(
        case((CongressionalTransaction.transaction_type == "sale", 1), else_=0)
    ).label("sell_count")
    filer_count = func.count(func.distinct(CongressionalFiling.reporting_person)).label("filer_count")
    latest_transaction_date = func.max(CongressionalTransaction.transaction_date).label(
        "latest_transaction_date"
    )
    latest_filing_date = func.max(CongressionalFiling.filing_date).label("latest_filing_date")
    issuer_name = func.min(CongressionalTransaction.issuer_name).label("issuer_name")

    stmt = (
        select(
            CongressionalTransaction.ticker.label("ticker"),
            issuer_name,
            buy_count,
            sell_count,
            filer_count,
            latest_transaction_date,
            latest_filing_date,
        )
        .join(CongressionalTransaction.filing)
        .where(CongressionalFiling.publication_status == PUBLICATION_STATUS_PUBLISHED)
        .where(CongressionalFiling.domain_release_state == DOMAIN_RELEASE_PUBLISHED)
        .where(CongressionalTransaction.publication_status == PUBLICATION_STATUS_PUBLISHED)
        .where(CongressionalTransaction.transaction_date.is_not(None))
        .where(CongressionalTransaction.transaction_date >= date_from)
        .where(CongressionalTransaction.ticker.is_not(None))
        .where(CongressionalTransaction.asset_type == "stock")
        .group_by(CongressionalTransaction.ticker)
        .having(buy_count > 0)
        .order_by(desc(buy_count), desc(filer_count), desc(latest_transaction_date))
        .limit(limit)
    )

    if transaction_date_to:
        stmt = stmt.where(CongressionalTransaction.transaction_date <= transaction_date_to)

    rows = session.execute(stmt).mappings().all()
    return [
        {
            "rank": index + 1,
            "ticker": row["ticker"],
            "issuer_name": row["issuer_name"],
            "buy_count": int(row["buy_count"] or 0),
            "sell_count": int(row["sell_count"] or 0),
            "filer_count": int(row["filer_count"] or 0),
            "latest_transaction_date": row["latest_transaction_date"],
            "latest_filing_date": row["latest_filing_date"],
        }
        for index, row in enumerate(rows)
    ]
