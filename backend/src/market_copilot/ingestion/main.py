from market_copilot.db.session import SessionLocal
from market_copilot.ingestion.congressional.service import (
    fetch_and_ingest_house_ptr_xml,
    run_normalization_cycle,
)
from market_copilot.settings import get_settings


def main() -> None:
    """Run one scheduled congressional ingestion flow and drain queued normalization jobs."""

    settings = get_settings()
    with SessionLocal() as session:
        ingest_result = fetch_and_ingest_house_ptr_xml(
            session=session,
            source_url=settings.house_xml_source_url,
            artifact_root=settings.local_artifact_root,
            run_type="scheduled",
        )
        print({"phase": "ingest", **ingest_result})

        while True:
            normalization_result = run_normalization_cycle(
                session=session,
                artifact_root=settings.local_artifact_root,
            )
            print({"phase": "normalize", **normalization_result})
            if normalization_result.get("status") == "no_queued_jobs":
                break


if __name__ == "__main__":
    main()
