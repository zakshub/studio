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
        )
