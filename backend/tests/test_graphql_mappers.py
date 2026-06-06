from __future__ import annotations

from datetime import date
from unittest import TestCase
from unittest.mock import patch
from uuid import uuid4

from market_copilot.api.graphql.mappers import map_filing
from market_copilot.db.models import CongressionalFiling, CongressionalTransaction


class GraphQLMapperAcceptanceTests(TestCase):
    def test_map_filing_excludes_out_of_scope_transactions(self) -> None:
        filing = CongressionalFiling(
            id=uuid4(),
            source_type="congressional_house_ptr",
            source_record_id="20000001",
            filing_type="Periodic Transaction Report",
            reporting_person="Hon. Example Member",
            source_document_url="https://example.test/ptr.pdf",
            publication_status="published",
            domain_release_state="published",
            normalization_version="raw_house_ptr_v1",
            model_name="test-model",
        )
        filing.transactions = [
            CongressionalTransaction(
                id=uuid4(),
                filing_id=filing.id,
                transaction_index=1,
                issuer_name="Apple Inc.",
                ticker="AAPL",
                asset_type="stock",
                transaction_type="purchase",
                transaction_date=date(2026, 5, 10),
                publication_status="published",
            ),
            CongressionalTransaction(
                id=uuid4(),
                filing_id=filing.id,
                transaction_index=2,
                issuer_name="Future Corp.",
                ticker="FTR",
                asset_type="stock",
                transaction_type="purchase",
                transaction_date=date(2026, 12, 26),
                publication_status="published",
            ),
            CongressionalTransaction(
                id=uuid4(),
                filing_id=filing.id,
                transaction_index=3,
                issuer_name="Past Corp.",
                ticker="OLD",
                asset_type="stock",
                transaction_type="sale",
                transaction_date=date(2025, 12, 15),
                publication_status="published",
            ),
        ]

        with patch(
            "market_copilot.api.graphql.mappers._is_product_transaction_in_scope",
            side_effect=lambda value: value == date(2026, 5, 10),
        ):
            result = map_filing(filing)

        self.assertEqual(len(result.transactions), 1)
        self.assertEqual(result.transactions[0].ticker, "AAPL")
