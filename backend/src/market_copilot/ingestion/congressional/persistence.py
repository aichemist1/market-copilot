from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
import hashlib

from sqlalchemy.orm import Session

from market_copilot.db.models import IngestionRun, NormalizationJob, SourceDocument
from market_copilot.domain.congressional.constants import SOURCE_TYPE_CONGRESSIONAL_HOUSE_PTR
from market_copilot.ingestion.congressional.discovery import HousePtrDiscoveryRecord
from market_copilot.ingestion.congressional.storage import build_ptr_pdf_storage_key


def create_ingestion_run(
    session: Session,
    run_type: str = "manual",
    *,
    source_locator: str | None = None,
) -> IngestionRun:
    run = IngestionRun(
        source_type=SOURCE_TYPE_CONGRESSIONAL_HOUSE_PTR,
        run_type=run_type,
        status="running",
        started_at=datetime.now(timezone.utc),
        source_locator=source_locator,
    )
    session.add(run)
    session.flush()
    return run


def upsert_house_xml_document(
    session: Session,
    *,
    ingestion_run_id,
    source_url: str,
    storage_key: str,
    mime_type: str | None,
    file_size_bytes: int,
    checksum: str | None = None,
) -> SourceDocument:
    existing = (
        session.query(SourceDocument)
        .filter(
            SourceDocument.document_type == "house_xml",
            SourceDocument.storage_key == storage_key,
        )
        .one_or_none()
    )
    if existing is not None:
        existing.source_url = source_url
        existing.mime_type = mime_type
        existing.file_size_bytes = file_size_bytes
        existing.checksum = checksum
        existing.ingestion_run_id = ingestion_run_id
        session.flush()
        return existing

    document = SourceDocument(
        source_type=SOURCE_TYPE_CONGRESSIONAL_HOUSE_PTR,
        source_record_id=None,
        document_type="house_xml",
        source_url=source_url,
        storage_key=storage_key,
        checksum=checksum,
        mime_type=mime_type,
        file_size_bytes=file_size_bytes,
        extraction_status="completed",
        ingestion_run_id=ingestion_run_id,
    )
    session.add(document)
    session.flush()
    return document


def upsert_ptr_source_documents(
    session: Session,
    ingestion_run_id,
    records: Iterable[HousePtrDiscoveryRecord],
) -> list[SourceDocument]:
    persisted: list[SourceDocument] = []

    for record in records:
        if not record.pdf_url:
            continue

        existing = (
            session.query(SourceDocument)
            .filter(
                SourceDocument.source_type == record.source_type,
                SourceDocument.source_record_id == record.source_record_id,
                SourceDocument.document_type == "ptr_pdf",
            )
            .one_or_none()
        )

        if existing is not None:
            existing.source_url = record.pdf_url
            existing.ingestion_run_id = ingestion_run_id
            persisted.append(existing)
            continue

        storage_key = build_ptr_pdf_storage_key(record.source_record_id, record.pdf_url)
        document = SourceDocument(
            source_type=record.source_type,
            source_record_id=record.source_record_id,
            document_type="ptr_pdf",
            source_url=record.pdf_url,
            storage_key=storage_key,
            extraction_status="not_started",
            ingestion_run_id=ingestion_run_id,
        )
        session.add(document)
        persisted.append(document)

    session.flush()
    return persisted


def create_normalization_jobs_for_documents(
    session: Session,
    documents: Iterable[SourceDocument],
    *,
    normalization_version: str = "congressional_v1",
    model_name: str = "pending-model",
    prompt_version: str = "congressional_v1_prompt",
) -> list[NormalizationJob]:
    jobs: list[NormalizationJob] = []

    for document in documents:
        existing_active = (
            session.query(NormalizationJob)
            .filter(
                NormalizationJob.source_document_id == document.id,
                NormalizationJob.normalization_version == normalization_version,
                NormalizationJob.status.in_(("queued", "running")),
            )
            .one_or_none()
        )
        if existing_active is not None:
            jobs.append(existing_active)
            continue

        job = NormalizationJob(
            source_document_id=document.id,
            source_type=document.source_type,
            normalization_version=normalization_version,
            model_name=model_name,
            prompt_version=prompt_version,
            status="queued",
            input_reference=document.extracted_text_storage_key or document.storage_key,
            output_reference=None,
            error_message=None,
            queued_at=datetime.now(timezone.utc),
            started_at=None,
        )
        session.add(job)
        jobs.append(job)

    session.flush()
    return jobs


def update_downloaded_document_artifact(
    session: Session,
    *,
    document: SourceDocument,
    mime_type: str | None,
    file_size_bytes: int,
    checksum_bytes: bytes,
) -> SourceDocument:
    document.mime_type = mime_type
    document.file_size_bytes = file_size_bytes
    document.checksum = hashlib.sha256(checksum_bytes).hexdigest()
    session.add(document)
    session.flush()
    return document


def upsert_extracted_text_document(
    session: Session,
    *,
    ptr_pdf_document: SourceDocument,
    storage_key: str,
    text_content: str,
) -> SourceDocument:
    existing = (
        session.query(SourceDocument)
        .filter(SourceDocument.storage_key == storage_key)
        .one_or_none()
    )
    if existing is not None:
        existing.file_size_bytes = len(text_content.encode("utf-8"))
        existing.mime_type = "text/plain"
        existing.ingestion_run_id = ptr_pdf_document.ingestion_run_id
        ptr_pdf_document.extracted_text_storage_key = storage_key
        session.flush()
        return existing

    document = SourceDocument(
        source_type=ptr_pdf_document.source_type,
        source_record_id=ptr_pdf_document.source_record_id,
        document_type="extracted_text",
        source_url=None,
        storage_key=storage_key,
        mime_type="text/plain",
        file_size_bytes=len(text_content.encode("utf-8")),
        extraction_status="completed",
        ingestion_run_id=ptr_pdf_document.ingestion_run_id,
    )
    session.add(document)
    ptr_pdf_document.extracted_text_storage_key = storage_key
    session.flush()
    return document


def mark_ingestion_run_completed(
    session: Session,
    run: IngestionRun,
    *,
    files_discovered_count: int,
    files_downloaded_count: int = 0,
    records_normalized_count: int = 0,
    records_published_count: int = 0,
    error_summary: str | None = None,
) -> IngestionRun:
    run.files_discovered_count = files_discovered_count
    run.files_downloaded_count = files_downloaded_count
    run.records_normalized_count = records_normalized_count
    run.records_published_count = records_published_count
    run.error_summary = error_summary
    run.status = "completed_with_errors" if error_summary else "completed"
    run.completed_at = datetime.now(timezone.utc)
    session.add(run)
    session.flush()
    return run


def _build_pdf_storage_key(source_record_id: str, pdf_url: str) -> str:
    filename = pdf_url.rstrip("/").rsplit("/", 1)[-1]
    return f"raw/congressional/house/pdfs/{source_record_id}/{filename}"
