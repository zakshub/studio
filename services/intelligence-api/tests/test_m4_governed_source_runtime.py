from __future__ import annotations

from io import BytesIO

import pytest

from fashionos_intelligence.persistence.assets import AssetRepository
from fashionos_intelligence.persistence.db import build_session_factory
from fashionos_intelligence.services.crawler import GovernedCrawler
from fashionos_intelligence.services.media_transport import FetchedMedia
from fashionos_intelligence.services.storage import (
    LocalContentAddressedStore,
    S3ContentAddressedStore,
)
from fashionos_intelligence.services.website_intake import WebsiteIntakeService
from fashionos_intelligence.services.website_pipeline import GovernedWebsitePipeline


class FakePageTransport:
    def __init__(self):
        self.calls: list[str] = []

    def get_text(self, url: str) -> str:
        self.calls.append(url)
        if url.endswith("/robots.txt"):
            return "User-agent: *\nAllow: /"
        return '<img src="/look.jpg">'


class ForbiddenMediaTransport:
    def get(self, url: str):
        raise AssertionError("reference-only binary must not be fetched")


class FakeMediaTransport:
    def __init__(self):
        self.calls: list[str] = []

    def get(self, url: str) -> FetchedMedia:
        self.calls.append(url)
        return FetchedMedia(
            url=url,
            payload=b"authorized-image",
            content_type="image/jpeg",
            suffix=".jpg",
        )


class FakeS3Client:
    def __init__(self):
        self.objects: dict[tuple[str, str], bytes] = {}

    def put_object(self, *, Bucket, Key, Body, Metadata):
        self.objects[(Bucket, Key)] = bytes(Body)
        return {"ETag": "fake"}

    def get_object(self, *, Bucket, Key):
        return {"Body": BytesIO(self.objects[(Bucket, Key)])}


def test_live_crawler_requires_explicit_access_review():
    transport = FakePageTransport()
    crawler = GovernedCrawler(transport)

    with pytest.raises(PermissionError, match="SOURCE_ACCESS_REVIEW_REQUIRED"):
        crawler.fetch_live(
            url="https://example.com/lookbook",
            role="primary",
            rights_status="authorized",
            access_approved=False,
        )
    assert transport.calls == []


def test_live_crawler_fetches_robots_before_page():
    transport = FakePageTransport()
    crawler = GovernedCrawler(transport)

    result = crawler.fetch_live(
        url="https://example.com/lookbook",
        role="primary",
        rights_status="authorized",
        access_approved=True,
    )

    assert result.robots_allowed is True
    assert transport.calls == [
        "https://example.com/robots.txt",
        "https://example.com/lookbook",
    ]


def test_reference_only_pipeline_never_persists_binary(tmp_path):
    sessions = build_session_factory("sqlite+pysqlite:///:memory:")
    assets = AssetRepository(sessions)
    page_transport = FakePageTransport()
    pipeline = GovernedWebsitePipeline(
        crawler=GovernedCrawler(page_transport),
        intake=WebsiteIntakeService(assets),
        media_transport=ForbiddenMediaTransport(),
        blob_store=LocalContentAddressedStore(tmp_path / "objects"),
        assets=assets,
    )

    result = pipeline.ingest(
        workspace_id="ws_ref",
        page_url="https://example.com/lookbook",
        role="secondary_reference",
        rights_status="reference_only",
        access_approved=True,
    )

    assert len(result.intake.asset_ids) == 1
    assert result.stored_asset_ids == ()
    stored = assets.get(result.intake.asset_ids[0])
    assert stored is not None
    assert stored.storage_uri is None
    assert stored.content_hash is None


def test_authorized_pipeline_stores_binary_and_provenance(tmp_path):
    sessions = build_session_factory("sqlite+pysqlite:///:memory:")
    assets = AssetRepository(sessions)
    media = FakeMediaTransport()
    pipeline = GovernedWebsitePipeline(
        crawler=GovernedCrawler(FakePageTransport()),
        intake=WebsiteIntakeService(assets),
        media_transport=media,
        blob_store=LocalContentAddressedStore(tmp_path / "objects"),
        assets=assets,
    )

    result = pipeline.ingest(
        workspace_id="ws_primary",
        page_url="https://example.com/lookbook",
        role="primary",
        rights_status="authorized",
        access_approved=True,
    )

    assert len(result.stored_asset_ids) == 1
    assert result.failures == ()
    stored = assets.get(result.stored_asset_ids[0])
    assert stored is not None
    assert stored.storage_uri is not None
    assert stored.content_hash is not None
    assert stored.metadata["contentType"] == "image/jpeg"
    assert stored.metadata["sizeBytes"] == len(b"authorized-image")
    assert media.calls == ["https://example.com/look.jpg"]


def test_s3_content_addressed_store_roundtrip_and_scope():
    client = FakeS3Client()
    store = S3ContentAddressedStore(
        client,
        bucket="fashionos-assets",
        prefix="production",
    )

    stored = store.put(b"same-payload", suffix="png")
    assert stored.uri.startswith("s3://fashionos-assets/production/")
    assert store.get(stored.uri) == b"same-payload"

    with pytest.raises(PermissionError, match="BLOB_OUTSIDE_STORE"):
        store.get("s3://fashionos-assets/other/object.png")
