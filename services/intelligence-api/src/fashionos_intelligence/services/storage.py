from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import urlparse


@dataclass(frozen=True)
class StoredBlob:
    uri: str
    content_hash: str
    size_bytes: int


class BlobStore(Protocol):
    def put(self, payload: bytes, *, suffix: str = "") -> StoredBlob: ...
    def get(self, uri: str) -> bytes: ...


class LocalContentAddressedStore:
    """Local development store with content addressed deduplication."""

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


class S3Client(Protocol):
    def put_object(self, **kwargs: Any) -> Any: ...
    def get_object(self, **kwargs: Any) -> dict[str, Any]: ...


class S3ContentAddressedStore:
    """Content addressed object store for AWS S3 or S3 compatible services.

    The client is injected so credentials stay in the deployment environment and
    tests never require a real cloud account.
    """

    def __init__(
        self,
        client: S3Client,
        *,
        bucket: str,
        prefix: str = "fashionos",
    ) -> None:
        if not bucket.strip():
            raise ValueError("S3_BUCKET_REQUIRED")
        self.client = client
        self.bucket = bucket.strip()
        self.prefix = prefix.strip("/")

    def _key(self, digest: str, suffix: str) -> str:
        clean_suffix = suffix if suffix.startswith(".") or not suffix else f".{suffix}"
        leaf = f"{digest}{clean_suffix}"
        path = f"{digest[:2]}/{leaf}"
        return f"{self.prefix}/{path}" if self.prefix else path

    def put(self, payload: bytes, *, suffix: str = "") -> StoredBlob:
        digest = sha256(payload).hexdigest()
        key = self._key(digest, suffix)
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=payload,
            Metadata={"sha256": digest},
        )
        return StoredBlob(
            uri=f"s3://{self.bucket}/{key}",
            content_hash=digest,
            size_bytes=len(payload),
        )

    def get(self, uri: str) -> bytes:
        parsed = urlparse(uri)
        if parsed.scheme != "s3" or parsed.netloc != self.bucket:
            raise ValueError("UNSUPPORTED_BLOB_URI")
        key = parsed.path.lstrip("/")
        if self.prefix and not key.startswith(f"{self.prefix}/"):
            raise PermissionError("BLOB_OUTSIDE_STORE")
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        body = response.get("Body")
        if body is None or not hasattr(body, "read"):
            raise RuntimeError("S3_OBJECT_BODY_MISSING")
        return bytes(body.read())
