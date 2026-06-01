from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from market_copilot.domain.congressional.constants import (
    CANONICAL_ASSET_TYPES,
    CANONICAL_OWNER_TYPES,
    CANONICAL_TRANSACTION_TYPES,
    SOURCE_TYPE_CONGRESSIONAL_HOUSE_PTR,
)


class CongressionalFilingNormalized(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_type: str = SOURCE_TYPE_CONGRESSIONAL_HOUSE_PTR
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

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, value: str) -> str:
        if value != SOURCE_TYPE_CONGRESSIONAL_HOUSE_PTR:
            raise ValueError(f"source_type must be {SOURCE_TYPE_CONGRESSIONAL_HOUSE_PTR}")
        return value


class CongressionalTransactionNormalized(BaseModel):
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

    @field_validator("transaction_type")
    @classmethod
    def validate_transaction_type(cls, value: str) -> str:
        if value not in CANONICAL_TRANSACTION_TYPES:
            raise ValueError(f"transaction_type must be one of {sorted(CANONICAL_TRANSACTION_TYPES)}")
        return value

    @field_validator("asset_type")
    @classmethod
    def validate_asset_type(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in CANONICAL_ASSET_TYPES:
            raise ValueError(f"asset_type must be one of {sorted(CANONICAL_ASSET_TYPES)}")
        return value

    @field_validator("owner_type")
    @classmethod
    def validate_owner_type(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in CANONICAL_OWNER_TYPES:
            raise ValueError(f"owner_type must be one of {sorted(CANONICAL_OWNER_TYPES)}")
        return value


class CongressionalNormalizationMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    normalization_version: str
    model_name: str
    warnings: list[str] = Field(default_factory=list)


class CongressionalNormalizationPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filing: CongressionalFilingNormalized
    transactions: list[CongressionalTransactionNormalized]
    normalization_metadata: CongressionalNormalizationMetadata

    @field_validator("transactions")
    @classmethod
    def validate_transactions(cls, value: list[CongressionalTransactionNormalized]) -> list[CongressionalTransactionNormalized]:
        if not value:
            raise ValueError("transactions must contain at least one normalized transaction")
        return value
