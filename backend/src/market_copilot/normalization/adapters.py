from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from openai import OpenAI

from market_copilot.domain.congressional.canonicalization import canonicalize_congressional_payload
from market_copilot.db.models import NormalizationJob, SourceDocument
from market_copilot.domain.congressional.constants import (
    ASSET_TYPE_UNKNOWN,
    SOURCE_TYPE_CONGRESSIONAL_HOUSE_PTR,
    TRANSACTION_TYPE_UNKNOWN,
)
from market_copilot.domain.congressional.normalization import CongressionalNormalizationPayload
from market_copilot.domain.congressional.raw_normalization import RawCongressionalNormalizationPayload
from market_copilot.settings import Settings


@dataclass(frozen=True)
class NormalizationRequest:
    job: NormalizationJob
    source_document: SourceDocument
    extracted_text: str


class NormalizationAdapter(Protocol):
    def normalize(self, request: NormalizationRequest) -> CongressionalNormalizationPayload:
        ...


class DevelopmentStubNormalizationAdapter:
    """Development adapter that preserves pipeline shape without a live LLM call.

    This adapter is intentionally isolated behind the adapter boundary so a real
    LLM-backed normalizer can replace it without altering the ingestion flow.
    """

    def normalize(self, request: NormalizationRequest) -> CongressionalNormalizationPayload:
        source_document = request.source_document
        return CongressionalNormalizationPayload.model_validate(
            {
                "filing": {
                    "source_type": SOURCE_TYPE_CONGRESSIONAL_HOUSE_PTR,
                    "source_record_id": source_document.source_record_id or "unknown",
                    "filing_type": "Periodic Transaction Report",
                    "reporting_person": "Pending LLM Normalization",
                    "source_document_url": source_document.source_url or "",
                    "raw_text_reference": source_document.extracted_text_storage_key
                    or source_document.storage_key,
                },
                "transactions": [
                    {
                        "transaction_index": 0,
                        "issuer_name": "Unknown Issuer",
                        "asset_type": ASSET_TYPE_UNKNOWN,
                        "transaction_type": TRANSACTION_TYPE_UNKNOWN,
                        "commentary": "Development stub output awaiting live model integration.",
                        "raw_text_reference": source_document.extracted_text_storage_key
                        or source_document.storage_key,
                    }
                ],
                "normalization_metadata": {
                    "normalization_version": request.job.normalization_version,
                    "model_name": request.job.model_name,
                    "warnings": ["development_stub_normalization_adapter"],
                },
            }
        )


class OpenAINormalizationAdapter:
    """OpenAI-backed adapter using Structured Outputs with the Responses API."""

    def __init__(self, *, api_key: str, model: str) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def normalize(self, request: NormalizationRequest) -> CongressionalNormalizationPayload:
        response = self._client.responses.parse(
            model=self._model,
            input=[
                {
                    "role": "system",
                    "content": _build_system_prompt(),
                },
                {
                    "role": "user",
                    "content": _build_user_prompt(request),
                },
            ],
            text_format=RawCongressionalNormalizationPayload,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise RuntimeError("OpenAI normalization returned no parsed structured output")
        return canonicalize_congressional_payload(parsed, extracted_text=request.extracted_text)


def build_normalization_adapter(settings: Settings) -> NormalizationAdapter:
    provider = settings.normalization_provider.strip().lower()
    if provider == "stub":
        return DevelopmentStubNormalizationAdapter()
    if provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("MARKET_COPILOT_OPENAI_API_KEY is required for normalization_provider=openai")
        return OpenAINormalizationAdapter(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )
    raise RuntimeError(f"Unsupported normalization provider: {settings.normalization_provider}")


def _build_system_prompt() -> str:
    return (
        "You normalize House congressional Periodic Transaction Report content into a "
        "structured schema. Use only evidence from the supplied extracted text. "
        "Do not invent missing values. Preserve nulls when information is absent or unclear. "
        "Always capture filing-level metadata when present, including reporting status, filing status, "
        "and the digitally signed filing date. "
        "Use these canonical normalization rules: source_type must represent the House PTR source; "
        "map transaction types like P to purchase and S to sale; map owner abbreviations like SP to spouse, "
        "JT to joint, and DC to dependent_child; map asset abbreviations like GS to government_security and "
        "ST to stock when supported by the source. "
        "For each transaction, preserve a row-level raw_text_reference like row-1, row-2 when possible. "
        "When a field is ambiguous, prefer null over overconfident inference. "
        "Return the structured object only."
    )


def _build_user_prompt(request: NormalizationRequest) -> str:
    source_document = request.source_document
    return (
        "Normalize the following congressional PTR content.\n\n"
        f"Source record id: {source_document.source_record_id or 'unknown'}\n"
        f"Source URL: {source_document.source_url or 'unknown'}\n"
        f"Normalization version: {request.job.normalization_version}\n\n"
        "Extracted text:\n"
        f"{request.extracted_text}"
    )
