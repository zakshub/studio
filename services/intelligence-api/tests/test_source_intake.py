from pathlib import Path

import pytest

from fashionos_intelligence.persistence.assets import AssetRepository
from fashionos_intelligence.persistence.db import build_session_factory
from fashionos_intelligence.services.crawler import GovernedCrawler
from fashionos_intelligence.services.source_policy import SourcePolicy
from fashionos_intelligence.services.storage import LocalContentAddressedStore
from fashionos_intelligence.services.website_intake import WebsiteIntakeService


def test_source_policy_separates_authorized_and_reference_only():
    policy = SourcePolicy()
    primary = policy.decide(role="primary", rights_status="authorized")
    assert primary.may_store_binary is True
    assert primary.may_publish is True

    reference = policy.decide(
        role="secondary_reference",
        rights_status="reference_only",
    )
    assert reference.may_analyze is True
    assert reference.may_store_binary is False
    assert reference.may_publish is False


def test_unknown_rights_blocks_fetch():
    class Transport:
        def get_text(self, url: str) -> str:
            raise AssertionError("transport should not be called")

    crawler = GovernedCrawler(Transport())
    with pytest.raises(PermissionError, match="SOURCE_FETCH_NOT_ALLOWED"):
        crawler.fetch(
            url="https://example.com/lookbook",
            role="secondary_reference",
            rights_status="unknown",
            robots_text="User-agent: *\nAllow: /",
        )


def test_robots_disallow_blocks_transport():
    class Transport:
        def get_text(self, url: str) -> str:
            raise AssertionError("transport should not be called")

    crawler = GovernedCrawler(Transport())
    with pytest.raises(PermissionError, match="ROBOTS_DISALLOW"):
        crawler.fetch(
            url="https://example.com/private/lookbook",
            role="primary",
            rights_status="authorized",
            robots_text="User-agent: *\nDisallow: /private/",
        )


def test_website_intake_persists_reference_metadata_without_binary_storage():
    sessions = build_session_factory("sqlite+pysqlite:///:memory:")
    assets = AssetRepository(sessions)
    service = WebsiteIntakeService(assets)
    result = service.ingest_html(
        workspace_id="ws_1",
        page_url="https://example.com/lookbook",
        html='<img src="/one.jpg"><video src="/film.mp4"></video>',
        role="secondary_reference",
        rights_status="reference_only",
    )
    assert len(result.asset_ids) == 2
    stored = assets.get(result.asset_ids[0])
    assert stored is not None
    assert stored.storage_uri is None
    assert stored.metadata["binaryStorageAllowed"] is False
    assert stored.metadata["publicationAllowed"] is False


def test_local_content_addressed_store_deduplicates_same_payload(tmp_path: Path):
    store = LocalContentAddressedStore(tmp_path / "objects")
    first = store.put(b"same", suffix=".jpg")
    second = store.put(b"same", suffix=".jpg")
    assert first.content_hash == second.content_hash
    assert first.uri == second.uri
    assert store.get(first.uri) == b"same"
