from __future__ import annotations

import argparse

from market_copilot.db.session import SessionLocal
from market_copilot.domain.congressional.constants import MIN_SUPPORTED_CONGRESSIONAL_YEAR
from market_copilot.ingestion.congressional.fetch import DownloadedArtifact
from market_copilot.ingestion.congressional.service import ingest_house_ptr_xml_artifact
from market_copilot.settings import get_settings


def _build_eval_xml(
    *,
    filing_id: str,
    name: str,
    filing_date: str,
    filing_status: str,
    state_district: str,
    pdf_url: str,
) -> str:
    return f"""\
<root>
  <record>
    <FilingID>{filing_id}</FilingID>
    <Name>{name}</Name>
    <FilingType>Periodic Transaction Report</FilingType>
    <FilingDate>{filing_date}</FilingDate>
    <FilingStatus>{filing_status}</FilingStatus>
    <StateDistrict>{state_district}</StateDistrict>
    <PDFUrl>{pdf_url}</PDFUrl>
  </record>
</root>
"""


def main() -> None:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Queue a single congressional PTR evaluation sample.")
    parser.add_argument("--filing-id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--filing-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--filing-status", default="New")
    parser.add_argument("--state-district", required=True)
    parser.add_argument("--pdf-url", required=True)
    parser.add_argument(
        "--source-url",
        default=settings.house_xml_source_url,
    )
    args = parser.parse_args()

    filing_year = int(args.filing_date[:4])
    if filing_year < MIN_SUPPORTED_CONGRESSIONAL_YEAR:
        raise SystemExit(
            f"Evaluation samples before {MIN_SUPPORTED_CONGRESSIONAL_YEAR} are out of scope for this product."
        )

    artifact = DownloadedArtifact(
        source_url=args.source_url,
        content=_build_eval_xml(
            filing_id=args.filing_id,
            name=args.name,
            filing_date=args.filing_date,
            filing_status=args.filing_status,
            state_district=args.state_district,
            pdf_url=args.pdf_url,
        ).encode("utf-8"),
        mime_type="application/xml",
    )
    with SessionLocal() as session:
        result = ingest_house_ptr_xml_artifact(
            session=session,
            artifact=artifact,
            artifact_root=settings.local_artifact_root,
            run_type="manual",
        )
        print(result)


if __name__ == "__main__":
    main()
