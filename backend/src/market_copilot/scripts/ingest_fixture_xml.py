from market_copilot.db.session import SessionLocal
from market_copilot.ingestion.congressional.fixtures import SAMPLE_HOUSE_PTR_XML
from market_copilot.ingestion.congressional.service import ingest_house_ptr_xml_artifact
from market_copilot.ingestion.congressional.fetch import DownloadedArtifact
from market_copilot.settings import get_settings


def main() -> None:
    settings = get_settings()
    artifact = DownloadedArtifact(
        source_url=settings.house_xml_source_url,
        content=SAMPLE_HOUSE_PTR_XML.encode("utf-8"),
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
