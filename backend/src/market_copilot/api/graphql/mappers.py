from __future__ import annotations

from market_copilot.api.graphql.types import (
    CongressionalFilingType,
    CongressionalTransactionType,
    IngestionRunType,
    ValidationMessageType,
    ValidationResultType,
)
from market_copilot.db.models import (
    CongressionalFiling,
    CongressionalTransaction,
    IngestionRun,
    ValidationResult,
)


def map_transaction(transaction: CongressionalTransaction) -> CongressionalTransactionType:
    return CongressionalTransactionType(
        id=str(transaction.id),
        transaction_index=transaction.transaction_index,
        issuer_name=transaction.issuer_name,
        ticker=transaction.ticker,
        asset_type=transaction.asset_type,
        transaction_type=transaction.transaction_type,
        transaction_date=transaction.transaction_date,
        notification_date=transaction.notification_date,
        amount_range=transaction.amount_range,
        owner_type=transaction.owner_type,
        subholding=transaction.subholding,
        capital_gains_over_200=transaction.capital_gains_over_200,
        commentary=transaction.commentary,
        raw_text_reference=transaction.raw_text_reference,
        publication_status=transaction.publication_status,
        created_at=transaction.created_at,
        updated_at=transaction.updated_at,
    )


def map_filing(filing: CongressionalFiling) -> CongressionalFilingType:
    return CongressionalFilingType(
        id=str(filing.id),
        source_type=filing.source_type,
        source_record_id=filing.source_record_id,
        filing_type=filing.filing_type,
        reporting_status=filing.reporting_status,
        filing_date=filing.filing_date,
        disclosure_date=filing.disclosure_date,
        filing_status=filing.filing_status,
        reporting_person=filing.reporting_person,
        office=filing.office,
        district_or_state=filing.district_or_state,
        source_document_url=filing.source_document_url,
        publication_status=filing.publication_status,
        domain_release_state=filing.domain_release_state,
        normalization_version=filing.normalization_version,
        model_name=filing.model_name,
        published_at=filing.published_at,
        created_at=filing.created_at,
        updated_at=filing.updated_at,
        transactions=[map_transaction(transaction) for transaction in filing.transactions],
    )


def map_ingestion_run(run: IngestionRun) -> IngestionRunType:
    return IngestionRunType(
        id=str(run.id),
        source_type=run.source_type,
        run_type=run.run_type,
        status=run.status,
        started_at=run.started_at,
        completed_at=run.completed_at,
        files_discovered_count=run.files_discovered_count,
        files_downloaded_count=run.files_downloaded_count,
        records_normalized_count=run.records_normalized_count,
        records_published_count=run.records_published_count,
        error_summary=run.error_summary,
        created_at=run.created_at,
    )


def map_validation_result(result: ValidationResult) -> ValidationResultType:
    return ValidationResultType(
        id=str(result.id),
        source_type=result.source_type,
        source_record_id=result.source_record_id,
        entity_type=result.entity_type,
        entity_id=str(result.entity_id) if result.entity_id else None,
        validation_version=result.validation_version,
        status=result.status,
        errors=[ValidationMessageType(**item) for item in result.errors_json],
        warnings=[ValidationMessageType(**item) for item in result.warnings_json],
        validated_at=result.validated_at,
    )
