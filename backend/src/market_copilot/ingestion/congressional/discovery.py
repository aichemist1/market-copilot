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
PTR_FILING_TYPE_CODES = {"p"}
PTR_FILING_TYPE_VALUES = {
    "periodic transaction report",
    "periodic transaction",
    "ptr",
}


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
    filing_type_value = (
        fields.get("filingtype")
        or fields.get("reporttype")
        or fields.get("doctype")
        or ""
    ).strip().lower()
    if filing_type_value in PTR_FILING_TYPE_CODES or filing_type_value in PTR_FILING_TYPE_VALUES:
        return True

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


def _build_ptr_pdf_url(source_record_id: str | None, record_year: int | None) -> str | None:
    if not source_record_id or not record_year:
        return None
    return f"https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/{record_year}/{source_record_id}.pdf"


def _compose_reporting_person(fields: dict[str, str]) -> str | None:
    explicit_name = fields.get("name") or fields.get("filer") or fields.get("reportingperson")
    if explicit_name:
        return explicit_name

    name_parts = [
        fields.get("prefix"),
        fields.get("firstname") or fields.get("first"),
        fields.get("middlename") or fields.get("middle"),
        fields.get("lastname") or fields.get("last"),
        fields.get("suffix"),
    ]
    composed = " ".join(part.strip() for part in name_parts if part and part.strip())
    return composed or None


def _compose_district_or_state(fields: dict[str, str]) -> str | None:
    explicit = fields.get("state") or fields.get("district") or fields.get("statedistrict")
    if explicit:
        return explicit

    state = (fields.get("stateabbrev") or fields.get("statecode") or "").strip()
    district = (fields.get("districtnumber") or fields.get("districtnum") or "").strip()
    if state and district:
        return f"{state}{district}"
    return state or district or None


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

        source_record_id = (
            fields.get("filingid")
            or fields.get("filing_id")
            or fields.get("docid")
            or fields.get("documentid")
        )
        pdf_url = _find_pdf_url(fields)
        if not _is_ptr_record(fields, pdf_url):
            continue

        record_year = _extract_record_year(fields, pdf_url)
        if record_year is not None and record_year < MIN_SUPPORTED_CONGRESSIONAL_YEAR:
            continue

        if not source_record_id:
            continue

        if pdf_url is None:
            pdf_url = _build_ptr_pdf_url(source_record_id, record_year)

        records.append(
            HousePtrDiscoveryRecord(
                source_type=SOURCE_TYPE_CONGRESSIONAL_HOUSE_PTR,
                source_record_id=source_record_id,
                filing_type=fields.get("filingtype") or fields.get("reporttype") or fields.get("doctype"),
                reporting_person=_compose_reporting_person(fields),
                filing_date_text=fields.get("filingdate") or fields.get("date"),
                filing_status=fields.get("filingstatus") or fields.get("status"),
                district_or_state=_compose_district_or_state(fields),
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
