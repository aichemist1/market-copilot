from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from market_copilot.settings import Settings, get_settings


ARTIFACT_STORAGE_MODE_LOCAL = "local"
ARTIFACT_STORAGE_MODE_S3 = "s3"


def ensure_local_artifact_root(root: str | Path) -> Path:
    path = Path(root)
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_xml_storage_key(target_time: datetime | None = None) -> str:
    timestamp = target_time or datetime.now(UTC)
    return (
        f"raw/congressional/house/xml/"
        f"{timestamp.year:04d}/{timestamp.month:02d}/{timestamp.day:02d}/"
        f"house_ptr_disclosures.xml"
    )


def build_ptr_pdf_storage_key(source_record_id: str, source_url: str) -> str:
    filename = source_url.rstrip("/").rsplit("/", 1)[-1]
    return f"raw/congressional/house/pdfs/{source_record_id}/{filename}"


def build_extracted_text_storage_key(source_record_id: str, source_document_id: str) -> str:
    return (
        f"derived/congressional/extracted-text/"
        f"{source_record_id}/{source_document_id}.txt"
    )


def build_normalization_output_storage_key(source_record_id: str, source_document_id: str) -> str:
    return (
        f"derived/congressional/normalization-outputs/"
        f"{source_record_id}/{source_document_id}.json"
    )


@dataclass(frozen=True)
class ArtifactStore:
    settings: Settings
    artifact_root_override: str | None = None

    def write_bytes(self, storage_key: str, content: bytes) -> str:
        if self.settings.artifact_storage_mode == ARTIFACT_STORAGE_MODE_S3:
            return self._write_s3(storage_key, content)
        if self.settings.artifact_storage_mode != ARTIFACT_STORAGE_MODE_LOCAL:
            raise ValueError(
                f"Unsupported artifact storage mode: {self.settings.artifact_storage_mode}"
            )
        self._write_local(storage_key, content)
        return storage_key

    def _write_local(self, storage_key: str, content: bytes) -> Path:
        root = self.artifact_root_override or self.settings.local_artifact_root
        base = ensure_local_artifact_root(root)
        artifact_path = base / storage_key
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_bytes(content)
        return artifact_path

    def _write_s3(self, storage_key: str, content: bytes) -> str:
        if not self.settings.s3_bucket:
            raise ValueError("S3 artifact storage requires MARKET_COPILOT_S3_BUCKET")

        try:
            import boto3
        except ImportError as exc:
            raise RuntimeError(
                "S3 artifact storage requires boto3 to be installed in the backend environment."
            ) from exc

        client_kwargs: dict[str, str] = {}
        if self.settings.s3_region:
            client_kwargs["region_name"] = self.settings.s3_region

        s3 = boto3.client("s3", **client_kwargs)
        s3.put_object(
            Bucket=self.settings.s3_bucket,
            Key=storage_key,
            Body=content,
        )
        return storage_key


def build_artifact_store(
    settings: Settings | None = None,
    *,
    artifact_root_override: str | None = None,
) -> ArtifactStore:
    return ArtifactStore(
        settings=settings or get_settings(),
        artifact_root_override=artifact_root_override,
    )
