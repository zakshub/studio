from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    brain_root: Path
    stale_after_seconds: int = 3600
    internal_token: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        root = Path(os.getenv("FASHIONOS_BRAIN_ROOT", ".")).resolve()
        stale = int(os.getenv("FASHIONOS_BRAIN_STALE_AFTER_SECONDS", "3600"))
        token = os.getenv("FASHIONOS_INTERNAL_TOKEN") or None
        return cls(
            brain_root=root,
            stale_after_seconds=stale,
            internal_token=token,
        )
