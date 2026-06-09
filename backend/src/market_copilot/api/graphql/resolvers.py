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


def _product_transaction_end_date() -> date:
    return date.today()


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
                (CongressionalTransaction.transaction_date >= PRODUCT_TRANSACTION_START_DATE)
                & (CongressionalTransaction.transaction_date <= _product_transaction_end_date())
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
                & (CongressionalTransaction.transaction_date <= _product_transaction_end_date())
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
                (CongressionalTransaction.transaction_date >= PRODUCT_TRANSACTION_START_DATE)
                & (CongressionalTransaction.transaction_date <= _product_transaction_end_date())
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
        .where(CongressionalTransaction.transaction_date <= _product_transaction_end_date())
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
    asset_type: str | None = None,
    transaction_date_from: date | None = None,
    transaction_date_to: date | None = None,
    limit: int = 25,
) -> list[dict]:
    date_from = transaction_date_from or PRODUCT_TRANSACTION_START_DATE
    resolved_asset_type = asset_type or "stock"

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
        .where(CongressionalTransaction.transaction_date <= _product_transaction_end_date())
        .where(CongressionalTransaction.ticker.is_not(None))
        .where(CongressionalTransaction.asset_type == resolved_asset_type)
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


def list_transaction_anomalies(
    session: Session,
    *,
    limit: int = 50,
) -> list[dict]:
    today = _product_transaction_end_date()
    stmt = (
        select(CongressionalTransaction, CongressionalFiling)
        .join(CongressionalTransaction.filing)
        .where(CongressionalTransaction.transaction_date.is_not(None))
        .where(CongressionalTransaction.transaction_date > today)
        .order_by(CongressionalTransaction.transaction_date.desc(), CongressionalTransaction.created_at.desc())
        .limit(limit)
    )

    rows = session.execute(stmt).all()
    return [
        {
            "source_record_id": filing.source_record_id,
            "reporting_person": filing.reporting_person,
            "district_or_state": filing.district_or_state,
            "filing_date": filing.filing_date,
            "transaction_index": transaction.transaction_index,
            "issuer_name": transaction.issuer_name,
            "ticker": transaction.ticker,
            "transaction_type": transaction.transaction_type,
            "transaction_date": transaction.transaction_date,
            "notification_date": transaction.notification_date,
            "amount_range": transaction.amount_range,
            "source_document_url": filing.source_document_url,
            "anomaly_code": "future_transaction_date",
            "anomaly_message": (
                f"Trade date {transaction.transaction_date.isoformat()} is after the current product date "
                f"{today.isoformat()} and requires admin review."
            ),
        }
        for transaction, filing in rows
    ]


def get_dashboard_metrics(
    session: Session,
    *,
    transaction_date_from: date | None = None,
    transaction_date_to: date | None = None,
) -> dict:
    date_from = transaction_date_from or PRODUCT_TRANSACTION_START_DATE
    today = _product_transaction_end_date()

    base_filters = [
        CongressionalFiling.publication_status == PUBLICATION_STATUS_PUBLISHED,
        CongressionalFiling.domain_release_state == DOMAIN_RELEASE_PUBLISHED,
        CongressionalTransaction.publication_status == PUBLICATION_STATUS_PUBLISHED,
        CongressionalTransaction.transaction_date.is_not(None),
        CongressionalTransaction.transaction_date >= date_from,
        CongressionalTransaction.transaction_date <= today,
    ]

    if transaction_date_to:
        base_filters.append(CongressionalTransaction.transaction_date <= transaction_date_to)

    disclosure_count = session.execute(
        select(func.count(CongressionalTransaction.id))
        .join(CongressionalTransaction.filing)
        .where(*base_filters)
    ).scalar_one()

    filer_count = session.execute(
        select(func.count(func.distinct(CongressionalFiling.reporting_person)))
        .join(CongressionalTransaction, CongressionalTransaction.filing_id == CongressionalFiling.id)
        .where(*base_filters)
    ).scalar_one()

    buy_count = session.execute(
        select(func.count(CongressionalTransaction.id))
        .join(CongressionalTransaction.filing)
        .where(*base_filters)
        .where(CongressionalTransaction.transaction_type == "purchase")
    ).scalar_one()

    sell_count = session.execute(
        select(func.count(CongressionalTransaction.id))
        .join(CongressionalTransaction.filing)
        .where(*base_filters)
        .where(CongressionalTransaction.transaction_type == "sale")
    ).scalar_one()

    return {
        "disclosure_count": int(disclosure_count or 0),
        "buy_count": int(buy_count or 0),
        "sell_count": int(sell_count or 0),
        "filer_count": int(filer_count or 0),
    }


def get_signal_metrics(
    session: Session,
    *,
    asset_type: str | None = None,
    transaction_date_from: date | None = None,
    transaction_date_to: date | None = None,
) -> dict:
    date_from = transaction_date_from or PRODUCT_TRANSACTION_START_DATE
    resolved_asset_type = asset_type or "stock"
    today = _product_transaction_end_date()

    base_filters = [
        CongressionalFiling.publication_status == PUBLICATION_STATUS_PUBLISHED,
        CongressionalFiling.domain_release_state == DOMAIN_RELEASE_PUBLISHED,
        CongressionalTransaction.publication_status == PUBLICATION_STATUS_PUBLISHED,
        CongressionalTransaction.transaction_date.is_not(None),
        CongressionalTransaction.transaction_date >= date_from,
        CongressionalTransaction.transaction_date <= today,
        CongressionalTransaction.ticker.is_not(None),
        CongressionalTransaction.asset_type == resolved_asset_type,
        CongressionalTransaction.transaction_type == "purchase",
    ]

    if transaction_date_to:
        base_filters.append(CongressionalTransaction.transaction_date <= transaction_date_to)

    active_ticker_count = session.execute(
        select(func.count(func.distinct(CongressionalTransaction.ticker)))
        .join(CongressionalTransaction.filing)
        .where(*base_filters)
    ).scalar_one()

    buy_disclosure_count = session.execute(
        select(func.count(CongressionalTransaction.id))
        .join(CongressionalTransaction.filing)
        .where(*base_filters)
    ).scalar_one()

    distinct_filer_count = session.execute(
        select(func.count(func.distinct(CongressionalFiling.reporting_person)))
        .join(CongressionalTransaction, CongressionalTransaction.filing_id == CongressionalFiling.id)
        .where(*base_filters)
    ).scalar_one()

    latest_filing_date = session.execute(
        select(func.max(CongressionalFiling.filing_date))
        .join(CongressionalTransaction, CongressionalTransaction.filing_id == CongressionalFiling.id)
        .where(*base_filters)
    ).scalar_one()

    return {
        "active_ticker_count": int(active_ticker_count or 0),
        "buy_disclosure_count": int(buy_disclosure_count or 0),
        "distinct_filer_count": int(distinct_filer_count or 0),
        "latest_filing_date": latest_filing_date,
    }
