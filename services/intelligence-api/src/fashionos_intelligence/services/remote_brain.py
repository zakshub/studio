from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from urllib.parse import quote
from urllib.request import Request, urlopen
import json
import shutil
import tempfile


@dataclass(frozen=True)
class RemoteManifest:
    revision: str
    files: tuple[str, ...]


class RepositoryTransport(Protocol):
    def manifest(self) -> RemoteManifest: ...
    def read_text(self, path: str) -> str: ...


class GitHubRepositoryTransport:
    """Read-only GitHub transport. Credentials are optional and never returned."""

    def __init__(
        self,
        *,
        owner: str,
        repository: str,
        ref: str = "main",
        token: str | None = None,
    ) -> None:
        self.owner = owner
        self.repository = repository
        self.ref = ref
        self.token = token

    def _get(self, url: str) -> bytes:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "fashionos-intelligence",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = Request(url, headers=headers)
        with urlopen(request, timeout=20) as response:
            return response.read()

    def manifest(self) -> RemoteManifest:
        url = (
            f"https://api.github.com/repos/{quote(self.owner)}/{quote(self.repository)}"
            f"/git/trees/{quote(self.ref)}?recursive=1"
        )
        payload = json.loads(self._get(url).decode("utf-8"))
        revision = str(payload.get("sha") or "")
        if not revision:
            raise RuntimeError("REMOTE_REVISION_MISSING")
        files = tuple(
            item["path"]
            for item in payload.get("tree", [])
            if item.get("type") == "blob"
        )
        return RemoteManifest(revision=revision, files=files)

    def read_text(self, path: str) -> str:
        clean = "/".join(part for part in path.split("/") if part not in {"", ".", ".."})
        if clean != path:
            raise ValueError("INVALID_REMOTE_PATH")
        url = (
            f"https://raw.githubusercontent.com/{quote(self.owner)}/"
            f"{quote(self.repository)}/{quote(self.ref)}/{quote(clean, safe='/')}"
        )
        return self._get(url).decode("utf-8")


class RemoteBrainRefresher:
    ALLOWED_PREFIXES = (
        "architecture/",
        "knowledge/",
        "qc/",
        "workflows/",
        "research/learned-rules/",
        "expert-intelligence/",
    )
    ALLOWED_ROOT_FILES = {"README.md", "SKILL.md", "research/research-policy.md"}
    EXCLUDED_PREFIXES = (
        "qc/reports/",
        "project-management/",
        "backend/",
        "services/",
        "research/rolling-observations/",
    )

    def __init__(self, mirror_root: Path, transport: RepositoryTransport):
        self.mirror_root = mirror_root
        self.transport = transport
        self.revisions_root = mirror_root / "revisions"
        self.revisions_root.mkdir(parents=True, exist_ok=True)

    @classmethod
    def eligible(cls, path: str) -> bool:
        if path in cls.ALLOWED_ROOT_FILES:
            return True
        if any(path.startswith(prefix) for prefix in cls.EXCLUDED_PREFIXES):
            return False
        return path.endswith(".md") and any(
            path.startswith(prefix) for prefix in cls.ALLOWED_PREFIXES
        )

    def refresh(self) -> Path:
        manifest = self.transport.manifest()
        final_root = self.revisions_root / manifest.revision
        if final_root.exists():
            (self.mirror_root / "CURRENT").write_text(manifest.revision, encoding="utf-8")
            return final_root

        temp_root = Path(tempfile.mkdtemp(prefix="brain-refresh-", dir=self.mirror_root))
        try:
            for remote_path in manifest.files:
                if not self.eligible(remote_path):
                    continue
                target = temp_root / remote_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(self.transport.read_text(remote_path), encoding="utf-8")

            if not (temp_root / "SKILL.md").exists():
                raise RuntimeError("REMOTE_BRAIN_INCOMPLETE")

            temp_root.replace(final_root)
            (self.mirror_root / "CURRENT").write_text(manifest.revision, encoding="utf-8")
            return final_root
        except Exception:
            shutil.rmtree(temp_root, ignore_errors=True)
            raise

    def current(self) -> Path | None:
        pointer = self.mirror_root / "CURRENT"
        if not pointer.exists():
            return None
        revision = pointer.read_text(encoding="utf-8").strip()
        path = self.revisions_root / revision
        return path if path.exists() else None