from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MARKET_COPILOT_",
        env_file=".env",
        extra="ignore",
    )

    database_url: str = "postgresql+psycopg://dev@localhost:5432/market_copilot"
    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    normalization_provider: str = "stub"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    artifact_storage_mode: str = "local"
    local_artifact_root: str = "/Users/dev/Documents/market-copilot/.artifacts"
    s3_bucket: str | None = None
    s3_region: str | None = None
    house_xml_source_url: str = "https://disclosures-clerk.house.gov/public_disc/financial-pdfs/2026FD.xml"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
