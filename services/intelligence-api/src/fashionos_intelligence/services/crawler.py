from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import socket
from typing import Protocol
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx

from fashionos_intelligence.services.source_policy import SourcePolicy


class PageTransport(Protocol):
    def get_text(self, url: str) -> str: ...


@dataclass(frozen=True)
class FetchedPage:
    url: str
    html: str
    robots_allowed: bool


class HttpxPageTransport:
    """Bounded HTTP transport for approved public website ingestion."""

    def __init__(
        self,
        *,
        user_agent: str = "FashionOSResearchBot",
        timeout_seconds: float = 20.0,
        max_text_bytes: int = 5_000_000,
    ) -> None:
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds
        self.max_text_bytes = max_text_bytes

    @staticmethod
    def _validate_public_url(url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("INVALID_SOURCE_URL")

        host = parsed.hostname
        try:
            candidates = {item[4][0] for item in socket.getaddrinfo(host, parsed.port or 443)}
        except socket.gaierror as exc:
            raise ValueError("SOURCE_HOST_UNRESOLVED") from exc

        for candidate in candidates:
            address = ipaddress.ip_address(candidate)
            if (
                address.is_private
                or address.is_loopback
                or address.is_link_local
                or address.is_multicast
                or address.is_reserved
                or address.is_unspecified
            ):
                raise PermissionError("NON_PUBLIC_SOURCE_HOST")

    def get_text(self, url: str) -> str:
        self._validate_public_url(url)
        with httpx.Client(
            timeout=self.timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": self.user_agent},
        ) as client:
            response = client.get(url)
            response.raise_for_status()
            final_url = str(response.url)
            self._validate_public_url(final_url)
            content_type = response.headers.get("content-type", "").lower()
            if content_type and not any(
                token in content_type for token in ("text/", "html", "xml")
            ):
                raise ValueError("SOURCE_TEXT_CONTENT_TYPE_REQUIRED")
            payload = response.content
            if len(payload) > self.max_text_bytes:
                raise ValueError("SOURCE_TEXT_TOO_LARGE")
            return response.text


class GovernedCrawler:
    """Fetches only after rights, access approval and robots checks pass."""

    def __init__(
        self,
        transport: PageTransport,
        *,
        user_agent: str = "FashionOSResearchBot",
    ) -> None:
        self.transport = transport
        self.user_agent = user_agent
        self.policy = SourcePolicy()

    @staticmethod
    def robots_url(page_url: str) -> str:
        parsed = urlparse(page_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("INVALID_SOURCE_URL")
        return f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    def fetch(
        self,
        *,
        url: str,
        role: str,
        rights_status: str,
        robots_text: str,
    ) -> FetchedPage:
        policy = self.policy.decide(role=role, rights_status=rights_status)
        if not policy.may_fetch:
            raise PermissionError("SOURCE_FETCH_NOT_ALLOWED")

        parser = RobotFileParser()
        parser.set_url(self.robots_url(url))
        parser.parse(robots_text.splitlines())
        allowed = parser.can_fetch(self.user_agent, url)
        if not allowed:
            raise PermissionError("ROBOTS_DISALLOW")

        return FetchedPage(
            url=url,
            html=self.transport.get_text(url),
            robots_allowed=True,
        )

    def fetch_live(
        self,
        *,
        url: str,
        role: str,
        rights_status: str,
        access_approved: bool,
    ) -> FetchedPage:
        if not access_approved:
            raise PermissionError("SOURCE_ACCESS_REVIEW_REQUIRED")
        robots_text = self.transport.get_text(self.robots_url(url))
        return self.fetch(
            url=url,
            role=role,
            rights_status=rights_status,
            robots_text=robots_text,
        )
