from __future__ import annotations

from unittest import TestCase

from market_copilot.domain.congressional.source_fallbacks import (
    extract_filing_fallbacks,
    extract_row_fallbacks,
)


class SourceFallbackAcceptanceTests(TestCase):
    def test_extract_filing_fallbacks_reads_header_metadata(self) -> None:
        text = """
        Name: Hon. Example Member
        Status: Member
        State/District: TX18
        Filing Status: New
        Digitally Signed: Example, 05/31/2026
        """

        result = extract_filing_fallbacks(text)

        self.assertEqual(result.reporting_person, "Hon. Example Member")
        self.assertEqual(result.reporting_status, "Member")
        self.assertEqual(result.district_or_state, "TX18")
        self.assertEqual(result.filing_status, "New")
        self.assertEqual(result.filing_date_iso, "2026-05-31")

    def test_extract_row_fallbacks_preserves_row_reference_and_asset_code(self) -> None:
        text = """
        JT Microsoft Corporation [OP]
        P 05/19/2026 05/20/2026 $500,001 - $1,000,000
        """

        result = extract_row_fallbacks(text)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].asset_code, "OP")
        self.assertEqual(result[0].raw_row_reference, "row-1")
