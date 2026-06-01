from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RawCongressionalFilingNormalized(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_type: str
    source_record_id: str
    filing_type: str
    reporting_status: Optional[str] = None
    filing_date: Optional[date] = None
    disclosure_date: Optional[date] = None
    filing_status: Optional[str] = None
    reporting_person: str
    office: Optional[str] = None
    district_or_state: Optional[str] = None
    source_document_url: str
    raw_text_reference: Optional[str] = None


class RawCongressionalTransactionNormalized(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction_index: int = Field(ge=0)
    issuer_name: str
    ticker: Optional[str] = None
    asset_type: Optional[str] = None
    transaction_type: str
    transaction_date: Optional[date] = None
    notification_date: Optional[date] = None
    amount_range: Optional[str] = None
    owner_type: Optional[str] = None
    subholding: Optional[str] = None
    capital_gains_over_200: Optional[bool] = None
    commentary: Optional[str] = None
    raw_text_reference: Optional[str] = None


class RawCongressionalNormalizationMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    normalization_version: str
    model_name: str
    warnings: list[str] = Field(default_factory=list)


class RawCongressionalNormalizationPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filing: RawCongressionalFilingNormalized
    transactions: list[RawCongressionalTransactionNormalized]
    normalization_metadata: RawCongressionalNormalizationMetadata
