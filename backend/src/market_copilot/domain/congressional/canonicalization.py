from __future__ import annotations

from datetime import date

from market_copilot.domain.congressional.constants import (
    ASSET_TYPE_BOND,
    ASSET_TYPE_ETF,
    ASSET_TYPE_GOVERNMENT_SECURITY,
    ASSET_TYPE_MUTUAL_FUND,
    ASSET_TYPE_OPTION,
    ASSET_TYPE_OTHER,
    ASSET_TYPE_STOCK,
    OWNER_TYPE_DEPENDENT_CHILD,
    OWNER_TYPE_JOINT,
    OWNER_TYPE_OTHER,
    OWNER_TYPE_SELF,
    OWNER_TYPE_SPOUSE,
    SOURCE_TYPE_CONGRESSIONAL_HOUSE_PTR,
    TRANSACTION_TYPE_EXCHANGE,
    TRANSACTION_TYPE_OTHER,
    TRANSACTION_TYPE_PURCHASE,
    TRANSACTION_TYPE_SALE,
    TRANSACTION_TYPE_UNKNOWN,
)
from market_copilot.domain.congressional.normalization import (
    CongressionalFilingNormalized,
    CongressionalNormalizationMetadata,
    CongressionalNormalizationPayload,
    CongressionalTransactionNormalized,
)
from market_copilot.domain.congressional.raw_normalization import (
    RawCongressionalNormalizationPayload,
)
from market_copilot.domain.congressional.source_fallbacks import (
    RowFallback,
    extract_filing_fallbacks,
    extract_row_fallbacks,
)


SOURCE_TYPE_MAP = {
    "congressional_house_ptr": SOURCE_TYPE_CONGRESSIONAL_HOUSE_PTR,
    "house_ptr": SOURCE_TYPE_CONGRESSIONAL_HOUSE_PTR,
    "house ptr": SOURCE_TYPE_CONGRESSIONAL_HOUSE_PTR,
    "periodic_transaction_report": SOURCE_TYPE_CONGRESSIONAL_HOUSE_PTR,
}

TRANSACTION_TYPE_MAP = {
    "p": TRANSACTION_TYPE_PURCHASE,
    "purchase": TRANSACTION_TYPE_PURCHASE,
    "buy": TRANSACTION_TYPE_PURCHASE,
    "s": TRANSACTION_TYPE_SALE,
    "sale": TRANSACTION_TYPE_SALE,
    "sell": TRANSACTION_TYPE_SALE,
    "s (partial)": TRANSACTION_TYPE_SALE,
    "partial sale": TRANSACTION_TYPE_SALE,
    "exchange": TRANSACTION_TYPE_EXCHANGE,
    "e": TRANSACTION_TYPE_EXCHANGE,
}

ASSET_TYPE_MAP = {
    "st": ASSET_TYPE_STOCK,
    "stock": ASSET_TYPE_STOCK,
    "cs": ASSET_TYPE_BOND,
    "corporate securities": ASSET_TYPE_BOND,
    "gs": ASSET_TYPE_GOVERNMENT_SECURITY,
    "government security": ASSET_TYPE_GOVERNMENT_SECURITY,
    "treasury": ASSET_TYPE_GOVERNMENT_SECURITY,
    "mf": ASSET_TYPE_MUTUAL_FUND,
    "mutual fund": ASSET_TYPE_MUTUAL_FUND,
    "etf": ASSET_TYPE_ETF,
    "op": ASSET_TYPE_OPTION,
    "opt": ASSET_TYPE_OPTION,
    "option": ASSET_TYPE_OPTION,
    "bond": ASSET_TYPE_BOND,
    "bd": ASSET_TYPE_BOND,
}

OWNER_TYPE_MAP = {
    "self": OWNER_TYPE_SELF,
    "sp": OWNER_TYPE_SPOUSE,
    "spouse": OWNER_TYPE_SPOUSE,
    "dc": OWNER_TYPE_DEPENDENT_CHILD,
    "dependent child": OWNER_TYPE_DEPENDENT_CHILD,
    "jt": OWNER_TYPE_JOINT,
    "joint": OWNER_TYPE_JOINT,
}


def canonicalize_congressional_payload(
    raw_payload: RawCongressionalNormalizationPayload,
    extracted_text: str | None = None,
) -> CongressionalNormalizationPayload:
    filing = raw_payload.filing
    filing_fallbacks = extract_filing_fallbacks(extracted_text or "")
    row_fallbacks = {row.index: row for row in extract_row_fallbacks(extracted_text or "")}
    normalized_filing = CongressionalFilingNormalized(
        source_type=_canonicalize_source_type(filing.source_type),
        source_record_id=filing.source_record_id,
        filing_type=_canonicalize_filing_type(filing.filing_type, filing_fallbacks.filing_type),
        reporting_status=filing.reporting_status or filing_fallbacks.reporting_status,
        filing_date=filing.filing_date or _to_date(filing_fallbacks.filing_date_iso),
        disclosure_date=filing.disclosure_date,
        filing_status=filing.filing_status or filing_fallbacks.filing_status,
        reporting_person=filing.reporting_person or filing_fallbacks.reporting_person or "Unknown",
        office=filing.office,
        district_or_state=filing.district_or_state or filing_fallbacks.district_or_state,
        source_document_url=filing.source_document_url,
        raw_text_reference=filing.raw_text_reference or "filing-header",
    )

    normalized_transactions = [
        CongressionalTransactionNormalized(
            transaction_index=transaction.transaction_index,
            issuer_name=_canonicalize_issuer_name(transaction.issuer_name),
            ticker=_canonicalize_ticker(transaction.ticker),
            asset_type=_canonicalize_asset_type(
                transaction.asset_type,
                issuer_name=transaction.issuer_name,
                row_fallback=row_fallbacks.get(transaction.transaction_index),
            ),
            transaction_type=_canonicalize_transaction_type(transaction.transaction_type),
            transaction_date=transaction.transaction_date,
            notification_date=transaction.notification_date,
            amount_range=transaction.amount_range,
            owner_type=_canonicalize_owner_type(
                transaction.owner_type,
                row_fallback=row_fallbacks.get(transaction.transaction_index),
            ),
            subholding=transaction.subholding,
            capital_gains_over_200=transaction.capital_gains_over_200,
            commentary=transaction.commentary,
            raw_text_reference=transaction.raw_text_reference or row_fallbacks.get(transaction.transaction_index, RowFallback(transaction.transaction_index)).raw_row_reference,
        )
        for transaction in raw_payload.transactions
    ]

    metadata = raw_payload.normalization_metadata
    normalized_metadata = CongressionalNormalizationMetadata(
        normalization_version=metadata.normalization_version,
        model_name=metadata.model_name,
        warnings=metadata.warnings,
    )

    return CongressionalNormalizationPayload(
        filing=normalized_filing,
        transactions=normalized_transactions,
        normalization_metadata=normalized_metadata,
    )


def _canonicalize_source_type(raw_value: str) -> str:
    value = raw_value.strip().lower().replace("-", "_")
    return SOURCE_TYPE_MAP.get(value, SOURCE_TYPE_CONGRESSIONAL_HOUSE_PTR)


def _canonicalize_filing_type(raw_value: str | None, fallback_value: str | None) -> str:
    value = (raw_value or fallback_value or "").strip()
    if value:
        return value
    return "Periodic Transaction Report"


def _canonicalize_transaction_type(raw_value: str) -> str:
    value = raw_value.strip().lower()
    return TRANSACTION_TYPE_MAP.get(value, TRANSACTION_TYPE_OTHER if value else TRANSACTION_TYPE_UNKNOWN)


def _canonicalize_asset_type(
    raw_value: str | None,
    *,
    issuer_name: str,
    row_fallback: RowFallback | None,
) -> str | None:
    candidate = raw_value
    if row_fallback and row_fallback.asset_code:
        candidate = row_fallback.asset_code
    if candidate is not None:
        value = candidate.strip().lower().replace("[", "").replace("]", "")
        mapped = ASSET_TYPE_MAP.get(value)
        if mapped is not None:
            return mapped

    issuer_value = issuer_name.lower()
    if "treasury" in issuer_value:
        return ASSET_TYPE_GOVERNMENT_SECURITY
    return ASSET_TYPE_OTHER if candidate or issuer_name else None


def _canonicalize_owner_type(
    raw_value: str | None,
    *,
    row_fallback: RowFallback | None,
) -> str | None:
    candidate = raw_value
    if row_fallback and row_fallback.owner_code:
        candidate = row_fallback.owner_code
    if candidate is None:
        return None
    value = candidate.strip().lower()
    return OWNER_TYPE_MAP.get(value, OWNER_TYPE_OTHER if value else None)


def _canonicalize_issuer_name(raw_value: str) -> str:
    value = raw_value.strip()
    value = value.lstrip("/").strip()
    return value


def _canonicalize_ticker(raw_value: str | None) -> str | None:
    if raw_value is None:
        return None
    value = raw_value.strip().upper()
    return value or None


def _to_date(raw_value: str | None) -> date | None:
    if raw_value is None:
        return None
    return date.fromisoformat(raw_value)
