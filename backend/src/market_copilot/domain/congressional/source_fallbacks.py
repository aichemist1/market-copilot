from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime


ROW_START_RE = re.compile(r"^(SP|JT|DC|SC|ZZ|XX)\s+")
ROW_PARSE_RE = re.compile(
    r"^(?P<owner>[A-Z/]+)\s+"
    r"(?P<asset>.+?)\s+"
    r"\[(?P<asset_code>[A-Z]+)\]\s+"
    r"(?P<txn>P|S(?:\s+\(partial\))?|E)\s+"
    r"(?P<transaction_date>\d{2}/\d{2}/\d{4})"
    r"(?P<notification_date>\d{2}/\d{2}/\d{4})\s+"
    r"(?P<tail>.+)$"
)
ROW_CODE_ONLY_RE = re.compile(
    r"^(?P<owner>[A-Z/]+)\s+.+?\[(?P<asset_code>[A-Z]+)\]",
)
TRANSACTION_LINE_RE = re.compile(
    r"^(?P<txn>P|S(?:\s+\(partial\))?|E)\s+"
    r"(?P<transaction_date>\d{2}/\d{2}/\d{4})"
    r"(?P<notification_date>\d{2}/\d{2}/\d{4})"
)
ASSET_CODE_IN_ROW_RE = re.compile(r"\[(?P<asset_code>[A-Z]+)\]")


@dataclass(frozen=True)
class FilingFallbacks:
    reporting_person: str | None = None
    reporting_status: str | None = None
    district_or_state: str | None = None
    filing_date_iso: str | None = None
    filing_status: str | None = None
    filing_type: str | None = None


@dataclass(frozen=True)
class RowFallback:
    index: int
    owner_code: str | None = None
    asset_code: str | None = None
    raw_row_reference: str | None = None


def extract_filing_fallbacks(extracted_text: str) -> FilingFallbacks:
    text = _clean_text(extracted_text)
    reporting_person = _match_group(text, r"Name:\s*(.+)")
    reporting_status = _match_group(text, r"Status:\s*(.+)")
    district_or_state = _match_group(text, r"State/District:\s*([A-Z0-9]+)")
    signed_date = _match_group(text, r"Digitally Signed:.*?,\s*(\d{2}/\d{2}/\d{4})")
    filing_date_iso = _to_iso_date(signed_date) if signed_date else None
    filing_status = "New" if "Filing Status: New" in text or "Status: New" in text else None
    filing_type = "Periodic Transaction Report" if "Periodic Transaction Report" in text or "PTR" in text else None
    return FilingFallbacks(
        reporting_person=reporting_person,
        reporting_status=reporting_status,
        district_or_state=district_or_state,
        filing_date_iso=filing_date_iso,
        filing_status=filing_status,
        filing_type=filing_type,
    )


def extract_row_fallbacks(extracted_text: str) -> list[RowFallback]:
    text = _clean_text(extracted_text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    rows = _extract_owner_prefixed_rows(lines)
    if not rows:
        rows = _extract_transaction_anchored_rows(lines)

    fallbacks: list[RowFallback] = []
    for idx, row in enumerate(rows, start=1):
        match = ROW_PARSE_RE.match(row)
        if match:
            fallbacks.append(
                RowFallback(
                    index=idx,
                    owner_code=match.group("owner"),
                    asset_code=match.group("asset_code"),
                    raw_row_reference=f"row-{idx}",
                )
            )
            continue

        code_only_match = ROW_CODE_ONLY_RE.match(row)
        if code_only_match:
            fallbacks.append(
                RowFallback(
                    index=idx,
                    owner_code=code_only_match.group("owner"),
                    asset_code=code_only_match.group("asset_code"),
                    raw_row_reference=f"row-{idx}",
                )
            )
            continue

        asset_code_match = ASSET_CODE_IN_ROW_RE.search(row)
        if asset_code_match:
            fallbacks.append(
                RowFallback(
                    index=idx,
                    asset_code=asset_code_match.group("asset_code"),
                    raw_row_reference=f"row-{idx}",
                )
            )
            continue

        fallbacks.append(
            RowFallback(
                index=idx,
                raw_row_reference=f"row-{idx}",
            )
        )
    return fallbacks


def _extract_owner_prefixed_rows(lines: list[str]) -> list[str]:
    rows: list[str] = []
    current: list[str] = []
    for line in lines:
        if ROW_START_RE.match(line):
            if current:
                rows.append(" ".join(current))
            current = [line]
            continue

        if current and not _looks_like_metadata_line(line):
            current.append(line)
        elif current:
            rows.append(" ".join(current))
            current = []

    if current:
        rows.append(" ".join(current))
    return rows


def _extract_transaction_anchored_rows(lines: list[str]) -> list[str]:
    rows: list[str] = []
    current_asset_lines: list[str] = []

    for line in lines:
        if _looks_like_metadata_line(line) or _looks_like_header_line(line):
            continue

        if TRANSACTION_LINE_RE.match(line):
            if current_asset_lines:
                rows.append(" ".join(current_asset_lines + [line]))
                current_asset_lines = []
            continue

        current_asset_lines.append(line)

    return rows


def _clean_text(text: str) -> str:
    cleaned = text.replace("\x00", "")
    replacements = {
        "P T R": "PTR",
        "Filing Status": "Filing Status",
    }
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    return cleaned


def _match_group(text: str, pattern: str) -> str | None:
    match = re.search(pattern, text)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None


def _to_iso_date(raw_value: str) -> str | None:
    try:
        return datetime.strptime(raw_value, "%m/%d/%Y").date().isoformat()
    except ValueError:
        return None


def _looks_like_metadata_line(line: str) -> bool:
    metadata_markers = (
        "Filing Status:",
        "Filing ID",
        "Digitally Signed:",
        "Status:",
        "State/District:",
        "Name:",
        "For the complete list",
    )
    return any(marker in line for marker in metadata_markers)


def _looks_like_header_line(line: str) -> bool:
    header_markers = (
        "ID Owner Asset Transaction",
        "Type",
        "Date Notification",
        "Amount Cap.",
        "Gains >",
        "$200?",
        "T",
        "I V D",
        "I P O",
        "Yes  No",
        "PTR",
        "Clerk of the House of Representatives",
        "F I",
    )
    return any(marker in line for marker in header_markers)
