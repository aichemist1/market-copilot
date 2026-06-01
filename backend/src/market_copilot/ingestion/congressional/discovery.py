from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import PurePosixPath
from typing import Iterable
from xml.etree import ElementTree as ET

from market_copilot.domain.congressional.constants import (
    MIN_SUPPORTED_CONGRESSIONAL_YEAR,
    SOURCE_TYPE_CONGRESSIONAL_HOUSE_PTR,
)


PTR_KEYWORDS = ("ptr", "periodic transaction")


@dataclass(frozen=True)
class HousePtrDiscoveryRecord:
    source_type: str
    source_record_id: str
    filing_type: str | None
    reporting_person: str | None
    filing_date_text: str | None
    filing_status: str | None
    district_or_state: str | None
    pdf_url: str | None
    raw_xml: str


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _text_or_none(element: ET.Element | None) -> str | None:
    if element is None or element.text is None:
        return None
    value = element.text.strip()
    return value or None


def _child_map(element: ET.Element) -> dict[str, str]:
    result: dict[str, str] = {}
    for child in list(element):
        text = _text_or_none(child)
        if text is not None:
            result[_local_name(child.tag)] = text
    return result


def _find_pdf_url(fields: dict[str, str]) -> str | None:
    for key, value in fields.items():
        if "pdf" in key and value:
            return value
        if value.lower().endswith(".pdf"):
            return value
    return None


def _is_ptr_record(fields: dict[str, str], pdf_url: str | None) -> bool:
    candidate_values = " ".join(value.lower() for value in fields.values())
    if any(keyword in candidate_values for keyword in PTR_KEYWORDS):
        return True
    return bool(pdf_url and "ptr" in PurePosixPath(pdf_url).name.lower())


def _extract_record_year(fields: dict[str, str], pdf_url: str | None) -> int | None:
    filing_date = fields.get("filingdate") or fields.get("date")
    if filing_date:
        for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
            try:
                return datetime.strptime(filing_date, fmt).year
            except ValueError:
                continue

    if pdf_url:
        parts = PurePosixPath(pdf_url).parts
        for part in parts:
            if len(part) == 4 and part.isdigit():
                return int(part)

    return None


def parse_house_ptr_records(xml_text: str) -> list[HousePtrDiscoveryRecord]:
    root = ET.fromstring(xml_text)
    records: list[HousePtrDiscoveryRecord] = []

    for element in root.iter():
        children = list(element)
        if not children:
            continue

        fields = _child_map(element)
        if not fields:
            continue

        pdf_url = _find_pdf_url(fields)
        if not _is_ptr_record(fields, pdf_url):
            continue

        record_year = _extract_record_year(fields, pdf_url)
        if record_year is not None and record_year < MIN_SUPPORTED_CONGRESSIONAL_YEAR:
            continue

        source_record_id = (
            fields.get("filingid")
            or fields.get("filing_id")
            or fields.get("docid")
            or fields.get("documentid")
        )
        if not source_record_id:
            continue

        records.append(
            HousePtrDiscoveryRecord(
                source_type=SOURCE_TYPE_CONGRESSIONAL_HOUSE_PTR,
                source_record_id=source_record_id,
                filing_type=fields.get("filingtype") or fields.get("reporttype") or fields.get("doctype"),
                reporting_person=fields.get("name") or fields.get("filer") or fields.get("reportingperson"),
                filing_date_text=fields.get("filingdate") or fields.get("date"),
                filing_status=fields.get("filingstatus") or fields.get("status"),
                district_or_state=fields.get("state") or fields.get("district") or fields.get("statedistrict"),
                pdf_url=pdf_url,
                raw_xml=ET.tostring(element, encoding="unicode"),
            )
        )

    return _deduplicate_records(records)


def _deduplicate_records(records: Iterable[HousePtrDiscoveryRecord]) -> list[HousePtrDiscoveryRecord]:
    deduped: dict[tuple[str, str], HousePtrDiscoveryRecord] = {}
    for record in records:
        deduped[(record.source_type, record.source_record_id)] = record
    return list(deduped.values())
