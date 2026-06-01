from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from market_copilot.db.models import CongressionalFiling, CongressionalTransaction, SourceDocument, ValidationResult
from market_copilot.domain.congressional.constants import (
    DOMAIN_RELEASE_PUBLISHED,
    PUBLICATION_STATUS_FAILED_VALIDATION,
    PUBLICATION_STATUS_PUBLISHED,
)
from market_copilot.domain.congressional.normalization import CongressionalNormalizationPayload
from market_copilot.domain.congressional.validation import ValidationOutcome


def upsert_congressional_payload(
    session: Session,
    payload: CongressionalNormalizationPayload,
    *,
    source_document_id=None,
    publish_on_success: bool = True,
) -> CongressionalFiling:
    filing_data = payload.filing
    resolved_source_document_id = source_document_id or _resolve_source_document_id(
        session,
        source_type=filing_data.source_type,
        source_record_id=filing_data.source_record_id,
        source_document_url=filing_data.source_document_url,
    )
    filing = (
        session.query(CongressionalFiling)
        .filter(
            CongressionalFiling.source_type == filing_data.source_type,
            CongressionalFiling.source_record_id == filing_data.source_record_id,
        )
        .one_or_none()
    )

    publication_status = (
        PUBLICATION_STATUS_PUBLISHED if publish_on_success else PUBLICATION_STATUS_FAILED_VALIDATION
    )

    if filing is None:
        filing = CongressionalFiling(
            source_type=filing_data.source_type,
            source_record_id=filing_data.source_record_id,
            filing_type=filing_data.filing_type,
            reporting_status=filing_data.reporting_status,
            filing_date=filing_data.filing_date,
            disclosure_date=filing_data.disclosure_date,
            filing_status=filing_data.filing_status,
            reporting_person=filing_data.reporting_person,
            office=filing_data.office,
            district_or_state=filing_data.district_or_state,
            source_document_id=resolved_source_document_id,
            source_document_url=filing_data.source_document_url,
            publication_status=publication_status,
            domain_release_state=DOMAIN_RELEASE_PUBLISHED,
            normalization_version=payload.normalization_metadata.normalization_version,
            model_name=payload.normalization_metadata.model_name,
        )
        session.add(filing)
        session.flush()
    else:
        filing.filing_type = filing_data.filing_type
        filing.reporting_status = filing_data.reporting_status
        filing.filing_date = filing_data.filing_date
        filing.disclosure_date = filing_data.disclosure_date
        filing.filing_status = filing_data.filing_status
        filing.reporting_person = filing_data.reporting_person
        filing.office = filing_data.office
        filing.district_or_state = filing_data.district_or_state
        filing.source_document_id = resolved_source_document_id
        filing.source_document_url = filing_data.source_document_url
        filing.publication_status = publication_status
        filing.normalization_version = payload.normalization_metadata.normalization_version
        filing.model_name = payload.normalization_metadata.model_name

    existing_by_index = {txn.transaction_index: txn for txn in filing.transactions}
    incoming_indices = set()

    for normalized_txn in payload.transactions:
        incoming_indices.add(normalized_txn.transaction_index)
        transaction = existing_by_index.get(normalized_txn.transaction_index)
        amount_min, amount_max = _parse_amount_range(normalized_txn.amount_range)

        if transaction is None:
            transaction = CongressionalTransaction(
                filing_id=filing.id,
                transaction_index=normalized_txn.transaction_index,
                issuer_name=normalized_txn.issuer_name,
                ticker=normalized_txn.ticker,
                asset_type=normalized_txn.asset_type,
                transaction_type=normalized_txn.transaction_type,
                transaction_date=normalized_txn.transaction_date,
                notification_date=normalized_txn.notification_date,
                amount_range=normalized_txn.amount_range,
                amount_range_min=amount_min,
                amount_range_max=amount_max,
                owner_type=normalized_txn.owner_type,
                subholding=normalized_txn.subholding,
                capital_gains_over_200=normalized_txn.capital_gains_over_200,
                commentary=normalized_txn.commentary,
                raw_text_reference=normalized_txn.raw_text_reference,
                publication_status=publication_status,
            )
            session.add(transaction)
        else:
            transaction.issuer_name = normalized_txn.issuer_name
            transaction.ticker = normalized_txn.ticker
            transaction.asset_type = normalized_txn.asset_type
            transaction.transaction_type = normalized_txn.transaction_type
            transaction.transaction_date = normalized_txn.transaction_date
            transaction.notification_date = normalized_txn.notification_date
            transaction.amount_range = normalized_txn.amount_range
            transaction.amount_range_min = amount_min
            transaction.amount_range_max = amount_max
            transaction.owner_type = normalized_txn.owner_type
            transaction.subholding = normalized_txn.subholding
            transaction.capital_gains_over_200 = normalized_txn.capital_gains_over_200
            transaction.commentary = normalized_txn.commentary
            transaction.raw_text_reference = normalized_txn.raw_text_reference
            transaction.publication_status = publication_status

    for transaction_index, transaction in existing_by_index.items():
        if transaction_index not in incoming_indices:
            session.delete(transaction)

    session.flush()
    return filing


def record_validation_result(
    session: Session,
    *,
    source_type: str,
    source_record_id: str,
    entity_type: str,
    entity_id,
    validation_version: str,
    outcome: ValidationOutcome,
) -> ValidationResult:
    result = ValidationResult(
        source_type=source_type,
        source_record_id=source_record_id,
        entity_type=entity_type,
        entity_id=entity_id,
        validation_version=validation_version,
        status=outcome.status,
        errors_json=[message.__dict__ for message in outcome.errors],
        warnings_json=[message.__dict__ for message in outcome.warnings],
        validated_at=__import__("datetime").datetime.utcnow(),
    )
    session.add(result)
    session.flush()
    return result


def _parse_amount_range(amount_range: str | None) -> tuple[Decimal | None, Decimal | None]:
    if not amount_range or "-" not in amount_range:
        return None, None

    left, right = amount_range.split("-", 1)
    return _parse_money_value(left), _parse_money_value(right)


def _parse_money_value(raw_value: str) -> Decimal | None:
    cleaned = raw_value.replace("$", "").replace(",", "").strip()
    if not cleaned:
        return None
    try:
        return Decimal(cleaned)
    except Exception:
        return None


def _resolve_source_document_id(
    session: Session,
    *,
    source_type: str,
    source_record_id: str,
    source_document_url: str,
):
    document = (
        session.query(SourceDocument)
        .filter(
            SourceDocument.source_type == source_type,
            SourceDocument.source_record_id == source_record_id,
            SourceDocument.source_url == source_document_url,
        )
        .one_or_none()
    )
    return document.id if document is not None else None
