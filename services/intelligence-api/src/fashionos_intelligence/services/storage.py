from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class StoredBlob:
    uri: str
    content_hash: str
    size_bytes: int


class BlobStore(Protocol):
    def put(self, payload: bytes, *, suffix: str = "") -> StoredBlob: ...
    def get(self, uri: str) -> bytes: ...


class LocalContentAddressedStore:
    """Local MVP store. S3-compatible implementations can satisfy the same contract."""

    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, payload: bytes, *, suffix: str = "") -> StoredBlob:
        digest = sha256(payload).hexdigest()
        clean_suffix = suffix if suffix.startswith(".") or not suffix else f".{suffix}"
        target = self.root / digest[:2] / f"{digest}{clean_suffix}"
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(payload)
        return StoredBlob(
            uri=f"file://{target}",
            content_hash=digest,
            size_bytes=len(payload),
        )

    def get(self, uri: str) -> bytes:
        if not uri.startswith("file://"):
            raise ValueError("UNSUPPORTED_BLOB_URI")
        path = Path(uri.removeprefix("file://")).resolve()
        root = self.root.resolve()
        if root not in path.parents and path != root:
            raise PermissionError("BLOB_OUTSIDE_STORE")
        return path.read_bytes()
