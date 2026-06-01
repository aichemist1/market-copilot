from __future__ import annotations

from sqlalchemy.orm import Session

from market_copilot.domain.congressional.constants import (
    PUBLICATION_STATUS_FAILED_VALIDATION,
    PUBLICATION_STATUS_PUBLISHED,
)
from market_copilot.domain.congressional.normalization import CongressionalNormalizationPayload
from market_copilot.domain.congressional.validation import validate_congressional_payload
from market_copilot.repositories.congressional import (
    record_validation_result,
    upsert_congressional_payload,
)


VALIDATION_VERSION = "congressional_v1"


def persist_normalized_congressional_payload(
    session: Session,
    payload: CongressionalNormalizationPayload,
    *,
    source_document_id=None,
) -> dict[str, str]:
    outcome = validate_congressional_payload(payload)
    publish_on_success = outcome.status != "failed"

    filing = upsert_congressional_payload(
        session,
        payload,
        source_document_id=source_document_id,
        publish_on_success=publish_on_success,
    )

    if filing.publication_status not in (
        PUBLICATION_STATUS_PUBLISHED,
        PUBLICATION_STATUS_FAILED_VALIDATION,
    ):
        filing.publication_status = (
            PUBLICATION_STATUS_PUBLISHED if publish_on_success else PUBLICATION_STATUS_FAILED_VALIDATION
        )

    record_validation_result(
        session,
        source_type=payload.filing.source_type,
        source_record_id=payload.filing.source_record_id,
        entity_type="filing",
        entity_id=filing.id,
        validation_version=VALIDATION_VERSION,
        outcome=outcome,
    )
    session.commit()

    return {
        "source_record_id": payload.filing.source_record_id,
        "validation_status": outcome.status,
        "publication_status": filing.publication_status,
    }
