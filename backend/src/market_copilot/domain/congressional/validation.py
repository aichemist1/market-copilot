from __future__ import annotations

import re
from dataclasses import dataclass, field

from market_copilot.domain.congressional.normalization import (
    CongressionalNormalizationPayload,
    CongressionalTransactionNormalized,
)


AMOUNT_RANGE_PATTERN = re.compile(
    r"^\$?\s?\d[\d,]*(\.\d{1,2})?\s?-\s?\$?\s?\d[\d,]*(\.\d{1,2})?$"
)


@dataclass
class ValidationMessage:
    code: str
    message: str
    path: str


@dataclass
class ValidationOutcome:
    status: str
    errors: list[ValidationMessage] = field(default_factory=list)
    warnings: list[ValidationMessage] = field(default_factory=list)


def validate_congressional_payload(
    payload: CongressionalNormalizationPayload,
) -> ValidationOutcome:
    errors: list[ValidationMessage] = []
    warnings: list[ValidationMessage] = []

    filing = payload.filing
    if not filing.source_record_id.strip():
        errors.append(
            ValidationMessage(
                code="filing.source_record_id.required",
                message="source_record_id is required",
                path="filing.source_record_id",
            )
        )

    if not filing.reporting_person.strip():
        errors.append(
            ValidationMessage(
                code="filing.reporting_person.required",
                message="reporting_person is required",
                path="filing.reporting_person",
            )
        )

    seen_indices: set[int] = set()
    for transaction in payload.transactions:
        _validate_transaction(transaction, errors, warnings, seen_indices)

    status = "passed" if not errors and not warnings else "passed_with_warnings"
    if errors:
        status = "failed"

    return ValidationOutcome(status=status, errors=errors, warnings=warnings)


def _validate_transaction(
    transaction: CongressionalTransactionNormalized,
    errors: list[ValidationMessage],
    warnings: list[ValidationMessage],
    seen_indices: set[int],
) -> None:
    path_prefix = f"transactions[{transaction.transaction_index}]"

    if transaction.transaction_index in seen_indices:
        errors.append(
            ValidationMessage(
                code="transaction.transaction_index.duplicate",
                message="transaction_index must be unique within a filing",
                path=f"{path_prefix}.transaction_index",
            )
        )
    seen_indices.add(transaction.transaction_index)

    if not transaction.issuer_name.strip():
        errors.append(
            ValidationMessage(
                code="transaction.issuer_name.required",
                message="issuer_name is required",
                path=f"{path_prefix}.issuer_name",
            )
        )

    if transaction.amount_range and not AMOUNT_RANGE_PATTERN.match(transaction.amount_range):
        warnings.append(
            ValidationMessage(
                code="transaction.amount_range.non_canonical",
                message="amount_range is present but not in canonical range format",
                path=f"{path_prefix}.amount_range",
            )
        )

    if transaction.ticker and len(transaction.ticker.strip()) > 16:
        warnings.append(
            ValidationMessage(
                code="transaction.ticker.unusual_length",
                message="ticker length is unusual and may require review",
                path=f"{path_prefix}.ticker",
            )
        )
