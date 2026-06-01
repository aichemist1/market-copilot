from __future__ import annotations

import hashlib

from sqlalchemy.orm import Session

from market_copilot.db.models import NormalizationJob
from market_copilot.ingestion.congressional.fetch import DownloadedArtifact, download_artifact
from market_copilot.ingestion.congressional.extraction import extract_text_from_pdf_bytes
from market_copilot.ingestion.congressional.normalization import (
    mark_normalization_job_failed,
    run_normalization_for_job,
)
from market_copilot.ingestion.congressional.storage import (
    build_artifact_store,
    build_extracted_text_storage_key,
    build_xml_storage_key,
)
from market_copilot.ingestion.congressional.discovery import parse_house_ptr_records
from market_copilot.ingestion.congressional.persistence import (
    create_normalization_jobs_for_documents,
    create_ingestion_run,
    upsert_house_xml_document,
    mark_ingestion_run_completed,
    update_downloaded_document_artifact,
    upsert_extracted_text_document,
    upsert_ptr_source_documents,
)
from market_copilot.services.congressional import persist_normalized_congressional_payload
from market_copilot.settings import get_settings


def ingest_house_ptr_xml(session: Session, xml_text: str) -> dict[str, int]:
    """Parse a House XML payload and persist discovered PTR source documents."""

    run = create_ingestion_run(session=session, run_type="manual")
    records = parse_house_ptr_records(xml_text)
    documents = upsert_ptr_source_documents(
        session=session,
        ingestion_run_id=run.id,
        records=records,
    )
    jobs = create_normalization_jobs_for_documents(session=session, documents=documents)
    mark_ingestion_run_completed(
        session=session,
        run=run,
        files_discovered_count=len(records),
        files_downloaded_count=0,
        records_normalized_count=len(jobs),
        records_published_count=0,
    )
    session.commit()
    return {
        "records_discovered": len(records),
        "source_documents_upserted": len(documents),
        "normalization_jobs_queued": len(jobs),
    }


def ingest_house_ptr_xml_artifact(
    session: Session,
    artifact: DownloadedArtifact,
    *,
    artifact_root: str | None,
    run_type: str = "manual",
) -> dict[str, int | str]:
    settings = get_settings()
    artifact_store = build_artifact_store(
        settings,
        artifact_root_override=artifact_root,
    )
    run = create_ingestion_run(
        session=session,
        run_type=run_type,
        source_locator=artifact.source_url,
    )

    storage_key = build_xml_storage_key()
    artifact_store.write_bytes(storage_key, artifact.content)
    xml_document = upsert_house_xml_document(
        session=session,
        ingestion_run_id=run.id,
        source_url=artifact.source_url,
        storage_key=storage_key,
        mime_type=artifact.mime_type,
        file_size_bytes=len(artifact.content),
        checksum=hashlib.sha256(artifact.content).hexdigest(),
    )

    xml_text = artifact.content.decode("utf-8")
    records = parse_house_ptr_records(xml_text)
    documents = upsert_ptr_source_documents(
        session=session,
        ingestion_run_id=run.id,
        records=records,
    )
    jobs = create_normalization_jobs_for_documents(session=session, documents=documents)
    mark_ingestion_run_completed(
        session=session,
        run=run,
        files_discovered_count=len(records),
        files_downloaded_count=1,
        records_normalized_count=len(jobs),
        records_published_count=0,
    )
    session.commit()
    return {
        "ingestion_run_id": str(run.id),
        "xml_document_id": str(xml_document.id),
        "records_discovered": len(records),
        "source_documents_upserted": len(documents),
        "normalization_jobs_queued": len(jobs),
        "xml_storage_key": storage_key,
    }


def fetch_and_ingest_house_ptr_xml(
    session: Session,
    *,
    source_url: str | None = None,
    artifact_root: str | None,
    run_type: str = "scheduled",
) -> dict[str, int | str]:
    settings = get_settings()
    artifact = download_artifact(source_url or settings.house_xml_source_url)
    return ingest_house_ptr_xml_artifact(
        session=session,
        artifact=artifact,
        artifact_root=artifact_root,
        run_type=run_type,
    )


def run_normalization_cycle(
    session: Session,
    *,
    artifact_root: str | None,
) -> dict[str, str]:
    queued_job = (
        session.query(NormalizationJob)
        .filter_by(status="queued")
        .order_by(NormalizationJob.created_at.asc())
        .first()
    )
    if queued_job is None:
        return {"status": "no_queued_jobs"}

    job_id = queued_job.id
    try:
        settings = get_settings()
        artifact_store = build_artifact_store(
            settings,
            artifact_root_override=artifact_root,
        )
        ptr_pdf_document = (
            session.query(NormalizationJob)
            .filter(NormalizationJob.id == job_id)
            .one()
            .source_document
        )
        downloaded_pdf = download_artifact(ptr_pdf_document.source_url or "")
        pdf_bytes = downloaded_pdf.content
        artifact_store.write_bytes(ptr_pdf_document.storage_key, pdf_bytes)
        update_downloaded_document_artifact(
            session,
            document=ptr_pdf_document,
            mime_type=downloaded_pdf.mime_type,
            file_size_bytes=len(pdf_bytes),
            checksum_bytes=pdf_bytes,
        )

        extracted_text = extract_text_from_pdf_bytes(pdf_bytes)
        extracted_text_storage_key = build_extracted_text_storage_key(
            ptr_pdf_document.source_record_id or "unknown",
            str(ptr_pdf_document.id),
        )
        artifact_store.write_bytes(
            extracted_text_storage_key,
            extracted_text.encode("utf-8"),
        )
        upsert_extracted_text_document(
            session,
            ptr_pdf_document=ptr_pdf_document,
            storage_key=extracted_text_storage_key,
            text_content=extracted_text,
        )

        payload = run_normalization_for_job(
            session,
            job=queued_job,
            artifact_root=artifact_root,
            extracted_text=extracted_text,
        )
        persist_normalized_congressional_payload(
            session,
            payload,
            source_document_id=ptr_pdf_document.id,
        )
        return {
            "status": "completed",
            "source_record_id": payload.filing.source_record_id,
            "output_reference": queued_job.output_reference or "",
        }
    except Exception as exc:
        session.rollback()
        failed_job = session.query(NormalizationJob).filter(NormalizationJob.id == job_id).one_or_none()
        if failed_job is not None:
            mark_normalization_job_failed(
                session,
                failed_job,
                error_message=str(exc),
            )
            session.commit()
        return {
            "status": "failed",
            "error": str(exc),
        }


def run_stub_normalization_cycle(
    session: Session,
    *,
    artifact_root: str,
) -> dict[str, str]:
    """Backward-compatible alias for local development flow."""
    return run_normalization_cycle(session=session, artifact_root=artifact_root)
