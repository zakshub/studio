from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from fashionos_intelligence.services.source_policy import SourcePolicy


class PageTransport(Protocol):
    def get_text(self, url: str) -> str: ...


@dataclass(frozen=True)
class FetchedPage:
    url: str
    html: str
    robots_allowed: bool


class GovernedCrawler:
    """Fetches only after rights policy and robots checks pass.

    Site terms/access-policy review remains an external registration responsibility.
    """

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
