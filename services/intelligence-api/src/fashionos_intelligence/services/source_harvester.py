from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urljoin


@dataclass(frozen=True)
class DiscoveredMedia:
    url: str
    media_type: str
    source_url: str
    alt: str | None = None


class _MediaParser(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.items: list[DiscoveredMedia] = []

    def handle_starttag(self, tag: str, attrs):
        data = dict(attrs)
        if tag == "img" and data.get("src"):
            self.items.append(
                DiscoveredMedia(
                    url=urljoin(self.base_url, data["src"]),
                    media_type="image",
                    source_url=self.base_url,
                    alt=data.get("alt"),
                )
            )
        elif tag in {"video", "source"} and data.get("src"):
            media_type = "video" if tag == "video" or str(data.get("type", "")).startswith("video/") else "media"
            self.items.append(
                DiscoveredMedia(
                    url=urljoin(self.base_url, data["src"]),
                    media_type=media_type,
                    source_url=self.base_url,
                )
            )


class WebsiteHarvester:
    """Parses already-fetched HTML. Network/robots/permission handling stays outside this parser."""

    def discover(self, *, page_url: str, html: str) -> list[DiscoveredMedia]:
        parser = _MediaParser(page_url)
        parser.feed(html)
        seen: set[tuple[str, str]] = set()
        output: list[DiscoveredMedia] = []
        for item in parser.items:
            key = (item.url, item.media_type)
            if key in seen:
                continue
            seen.add(key)
            output.append(item)
        return output
