from market_copilot.db.session import SessionLocal
from market_copilot.ingestion.congressional.service import run_normalization_cycle
from market_copilot.settings import get_settings


def main() -> None:
    settings = get_settings()
    with SessionLocal() as session:
        result = run_normalization_cycle(
            session=session,
            artifact_root=settings.local_artifact_root,
        )
        print(result)


if __name__ == "__main__":
    main()
