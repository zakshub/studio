from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    brain_root: Path
    brain_snapshot_root: Path
    brain_remote_repo: str | None = None
    brain_remote_ref: str = "main"
    brain_remote_mirror_root: Path | None = None
    github_token: str | None = None
    stale_after_seconds: int = 3600
    internal_token: str | None = None
    database_url: str = "sqlite+pysqlite:///:memory:"
    openai_api_key: str | None = None
    openai_image_model: str = "gpt-image-2.5-flare"
    openai_image_edit_model: str = "gpt-image-2.5-sunburst"
    openai_vision_model: str = "gpt-5.6-luna"
    gemini_api_key: str | None = None
    gemini_image_model: str = "gemini-3.1-flash-image"
    gemini_vision_model: str = "gemini-3.8-flash"
    generated_asset_root: Path | None = None
    blob_store_backend: str = "local"
    s3_bucket: str | None = None
    s3_prefix: str = "fashionos"
    s3_region: str | None = None
    s3_endpoint_url: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        root = Path(os.getenv("FASHIONOS_BRAIN_ROOT", ".")).resolve()
        snapshot_root = Path(
            os.getenv(
                "FASHIONOS_BRAIN_SNAPSHOT_ROOT",
                str(root / ".fashionos-cache" / "brain-revisions"),
            )
        ).resolve()
        remote_repo = os.getenv("FASHIONOS_BRAIN_REMOTE_REPO") or None
        remote_ref = os.getenv("FASHIONOS_BRAIN_REMOTE_REF", "main")
        remote_mirror = (
            Path(
                os.getenv(
                    "FASHIONOS_BRAIN_REMOTE_MIRROR_ROOT",
                    str(root / ".fashionos-cache" / "remote-brain"),
                )
            ).resolve()
            if remote_repo
            else None
        )
        stale = int(os.getenv("FASHIONOS_BRAIN_STALE_AFTER_SECONDS", "3600"))
        token = os.getenv("FASHIONOS_INTERNAL_TOKEN") or None
        github_token = os.getenv("FASHIONOS_GITHUB_TOKEN") or None
        database_url = os.getenv(
            "FASHIONOS_DATABASE_URL",
            "sqlite+pysqlite:///:memory:",
        )
        openai_api_key = os.getenv("OPENAI_API_KEY") or None
        openai_image_model = os.getenv(
            "FASHIONOS_OPENAI_IMAGE_MODEL",
            "gpt-image-2.5-flare",
        )
        openai_image_edit_model = os.getenv(
            "FASHIONOS_OPENAI_IMAGE_EDIT_MODEL",
            "gpt-image-2.5-sunburst",
        )
        openai_vision_model = os.getenv(
            "FASHIONOS_OPENAI_VISION_MODEL",
            "gpt-5.6-luna",
        )
        gemini_api_key = os.getenv("GEMINI_API_KEY") or None
        gemini_image_model = os.getenv(
            "FASHIONOS_GEMINI_IMAGE_MODEL",
            "gemini-3.1-flash-image",
        )
        gemini_vision_model = os.getenv(
            "FASHIONOS_GEMINI_VISION_MODEL",
            "gemini-3.8-flash",
        )
        generated_asset_root = Path(
            os.getenv(
                "FASHIONOS_GENERATED_ASSET_ROOT",
                str(root / ".fashionos-cache" / "generated-assets"),
            )
        ).resolve()
        blob_store_backend = os.getenv("FASHIONOS_BLOB_STORE_BACKEND", "local").strip().lower()
        if blob_store_backend not in {"local", "s3"}:
            raise ValueError("FASHIONOS_BLOB_STORE_BACKEND must be local or s3")
        s3_bucket = os.getenv("FASHIONOS_S3_BUCKET") or None
        s3_prefix = os.getenv("FASHIONOS_S3_PREFIX", "fashionos")
        s3_region = os.getenv("FASHIONOS_S3_REGION") or None
        s3_endpoint_url = os.getenv("FASHIONOS_S3_ENDPOINT_URL") or None
        if blob_store_backend == "s3" and not s3_bucket:
            raise ValueError("FASHIONOS_S3_BUCKET is required when S3 storage is enabled")
        return cls(
            brain_root=root,
            brain_snapshot_root=snapshot_root,
            brain_remote_repo=remote_repo,
            brain_remote_ref=remote_ref,
            brain_remote_mirror_root=remote_mirror,
            github_token=github_token,
            stale_after_seconds=stale,
            internal_token=token,
            database_url=database_url,
            openai_api_key=openai_api_key,
            openai_image_model=openai_image_model,
            openai_image_edit_model=openai_image_edit_model,
            openai_vision_model=openai_vision_model,
            gemini_api_key=gemini_api_key,
            gemini_image_model=gemini_image_model,
            gemini_vision_model=gemini_vision_model,
            generated_asset_root=generated_asset_root,
            blob_store_backend=blob_store_backend,
            s3_bucket=s3_bucket,
            s3_prefix=s3_prefix,
            s3_region=s3_region,
            s3_endpoint_url=s3_endpoint_url,
        )
