from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from urllib.parse import urlparse

import httpx

from fashionos_intelligence.services.crawler import HttpxPageTransport


@dataclass(frozen=True)
class FetchedMedia:
    url: str
    payload: bytes
    content_type: str
    suffix: str


class HttpxMediaTransport:
    """Bounded binary transport for authorized public image and video assets."""

    def __init__(
        self,
        *,
        user_agent: str = "FashionOSResearchBot",
        timeout_seconds: float = 30.0,
        max_media_bytes: int = 50_000_000,
    ) -> None:
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds
        self.max_media_bytes = max_media_bytes

    @staticmethod
    def _suffix(url: str, content_type: str) -> str:
        known = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
            "image/gif": ".gif",
            "video/mp4": ".mp4",
            "video/webm": ".webm",
            "video/quicktime": ".mov",
        }
        if content_type in known:
            return known[content_type]
        suffix = PurePosixPath(urlparse(url).path).suffix.lower()
        return suffix if 1 <= len(suffix) <= 8 else ""

    def get(self, url: str) -> FetchedMedia:
        HttpxPageTransport._validate_public_url(url)
        with httpx.Client(
            timeout=self.timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": self.user_agent},
        ) as client:
            response = client.get(url)
            response.raise_for_status()
            final_url = str(response.url)
            HttpxPageTransport._validate_public_url(final_url)
            content_type = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
            if not (
                content_type.startswith("image/")
                or content_type.startswith("video/")
            ):
                raise ValueError("SOURCE_MEDIA_CONTENT_TYPE_REQUIRED")
            payload = response.content
            if len(payload) > self.max_media_bytes:
                raise ValueError("SOURCE_MEDIA_TOO_LARGE")
            return FetchedMedia(
                url=final_url,
                payload=payload,
                content_type=content_type,
                suffix=self._suffix(final_url, content_type),
            )
