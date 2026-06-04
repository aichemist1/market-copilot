from __future__ import annotations

from datetime import date, datetime

import strawberry


@strawberry.type
class CongressionalTransactionType:
    id: strawberry.ID
    transaction_index: int
    issuer_name: str
    ticker: str | None
    asset_type: str | None
    transaction_type: str
    transaction_date: date | None
    notification_date: date | None
    amount_range: str | None
    owner_type: str | None
    subholding: str | None
    capital_gains_over_200: bool | None
    commentary: str | None
    raw_text_reference: str | None
    publication_status: str
    created_at: datetime
    updated_at: datetime


@strawberry.type
class CongressionalTransactionFeedItemType:
    id: strawberry.ID
    source_record_id: str
    reporting_person: str
    district_or_state: str | None
    source_document_url: str
    transaction_index: int
    issuer_name: str
    ticker: str | None
    asset_type: str | None
    transaction_type: str
    transaction_date: date | None
    notification_date: date | None
    amount_range: str | None
    owner_type: str | None
    subholding: str | None
    capital_gains_over_200: bool | None
    commentary: str | None
    raw_text_reference: str | None
    created_at: datetime
    updated_at: datetime


@strawberry.type
class CongressionalFilingType:
    id: strawberry.ID
    source_type: str
    source_record_id: str
    filing_type: str
    reporting_status: str | None
    filing_date: date | None
    disclosure_date: date | None
    filing_status: str | None
    reporting_person: str
    office: str | None
    district_or_state: str | None
    source_document_url: str
    publication_status: str
    domain_release_state: str
    normalization_version: str
    model_name: str
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    transactions: list[CongressionalTransactionType]


@strawberry.type
class IngestionRunType:
    id: strawberry.ID
    source_type: str
    run_type: str
    status: str
    started_at: datetime
    completed_at: datetime | None
    files_discovered_count: int
    files_downloaded_count: int
    records_normalized_count: int
    records_published_count: int
    error_summary: str | None
    created_at: datetime


@strawberry.type
class ValidationMessageType:
    code: str
    message: str
    path: str


@strawberry.type
class ValidationResultType:
    id: strawberry.ID
    source_type: str
    source_record_id: str
    entity_type: str
    entity_id: strawberry.ID | None
    validation_version: str
    status: str
    errors: list[ValidationMessageType]
    warnings: list[ValidationMessageType]
    validated_at: datetime
