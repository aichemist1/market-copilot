from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from market_copilot.db.models import NormalizationJob, SourceDocument
from market_copilot.domain.congressional.normalization import CongressionalNormalizationPayload
from market_copilot.normalization.adapters import (
    NormalizationAdapter,
    NormalizationRequest,
    build_normalization_adapter,
)
from market_copilot.settings import Settings, get_settings
from market_copilot.ingestion.congressional.storage import (
    build_artifact_store,
    build_normalization_output_storage_key,
)


def mark_normalization_job_running(session: Session, job: NormalizationJob) -> NormalizationJob:
    job.status = "running"
    job.started_at = datetime.now(UTC)
    session.add(job)
    session.flush()
    return job


def mark_normalization_job_completed(
    session: Session,
    job: NormalizationJob,
    *,
    output_reference: str,
) -> NormalizationJob:
    job.status = "completed"
    job.output_reference = output_reference
    job.completed_at = datetime.now(UTC)
    session.add(job)
    session.flush()
    return job


def mark_normalization_job_failed(
    session: Session,
    job: NormalizationJob,
    *,
    error_message: str,
) -> NormalizationJob:
    job.status = "failed"
    job.error_message = error_message
    job.completed_at = datetime.now(UTC)
    session.add(job)
    session.flush()
    return job


def persist_normalization_output_artifact(
    session: Session,
    *,
    source_document: SourceDocument,
    settings: Settings,
    artifact_root: str | None,
    payload_json: bytes,
) -> SourceDocument:
    storage_key = build_normalization_output_storage_key(
        source_document.source_record_id or "unknown",
        str(source_document.id),
    )
    artifact_store = build_artifact_store(
        settings,
        artifact_root_override=artifact_root,
    )
    artifact_store.write_bytes(storage_key, payload_json)

    existing = (
        session.query(SourceDocument)
        .filter(SourceDocument.storage_key == storage_key)
        .one_or_none()
    )
    if existing is not None:
        existing.file_size_bytes = len(payload_json)
        existing.mime_type = "application/json"
        session.flush()
        return existing

    document = SourceDocument(
        source_type=source_document.source_type,
        source_record_id=source_document.source_record_id,
        document_type="normalization_output",
        source_url=None,
        storage_key=storage_key,
        mime_type="application/json",
        file_size_bytes=len(payload_json),
        extraction_status="completed",
        ingestion_run_id=source_document.ingestion_run_id,
    )
    session.add(document)
    session.flush()
    return document


def run_normalization_for_job(
    session: Session,
    *,
    job: NormalizationJob,
    artifact_root: str | None,
    adapter: NormalizationAdapter | None = None,
    extracted_text: str,
) -> CongressionalNormalizationPayload:
    source_document = session.query(SourceDocument).filter(SourceDocument.id == job.source_document_id).one()
    mark_normalization_job_running(session, job)
    settings = get_settings()
    normalizer = adapter or build_normalization_adapter(settings)
    payload = normalizer.normalize(
        NormalizationRequest(
            job=job,
            source_document=source_document,
            extracted_text=extracted_text,
        )
    )

    payload_json = payload.model_dump_json(indent=2).encode("utf-8")
    output_document = persist_normalization_output_artifact(
        session,
        source_document=source_document,
        settings=settings,
        artifact_root=artifact_root,
        payload_json=payload_json,
    )
    mark_normalization_job_completed(session, job, output_reference=output_document.storage_key)
    return payload
