from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import httpx


HOUSE_DISCLOSURE_INDEX_URL = "https://disclosures-clerk.house.gov/FinancialDisclosure"


@dataclass(frozen=True)
class DownloadedArtifact:
    source_url: str
    content: bytes
    mime_type: str | None


def build_house_xml_candidate_urls(target_date: date | None = None) -> list[str]:
    year = (target_date or date.today()).year
    return [
        f"https://disclosures-clerk.house.gov/public_disc/financial-pdfs/{year}FD.zip",
        f"https://disclosures-clerk.house.gov/public_disc/financial-pdfs/{year}FD.xml",
        f"https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/{year}/",
    ]


def download_artifact(source_url: str, timeout_seconds: float = 30.0) -> DownloadedArtifact:
    with httpx.Client(follow_redirects=True, timeout=timeout_seconds) as client:
        response = client.get(source_url)
        response.raise_for_status()
        return DownloadedArtifact(
            source_url=str(response.url),
            content=response.content,
            mime_type=response.headers.get("content-type"),
        )
