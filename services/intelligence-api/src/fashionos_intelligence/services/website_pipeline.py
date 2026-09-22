from __future__ import annotations

from dataclasses import dataclass

from fashionos_intelligence.persistence.assets import AssetRepository, StoredAsset
from fashionos_intelligence.services.crawler import GovernedCrawler
from fashionos_intelligence.services.media_transport import HttpxMediaTransport
from fashionos_intelligence.services.storage import BlobStore
from fashionos_intelligence.services.website_intake import WebsiteIntakeResult, WebsiteIntakeService


@dataclass(frozen=True)
class WebsitePipelineResult:
    intake: WebsiteIntakeResult
    stored_asset_ids: tuple[str, ...]
    failures: tuple[str, ...]


class GovernedWebsitePipeline:
    """End to end approved website ingestion.

    Reference only sources may be fetched and analyzed but their binaries are not
    persisted. Authorized sources may enter the configured content addressed store.
    """

    def __init__(
        self,
        *,
        crawler: GovernedCrawler,
        intake: WebsiteIntakeService,
        media_transport: HttpxMediaTransport,
        blob_store: BlobStore,
        assets: AssetRepository,
    ) -> None:
        self.crawler = crawler
        self.intake = intake
        self.media_transport = media_transport
        self.blob_store = blob_store
        self.assets = assets

    def ingest(
        self,
        *,
        workspace_id: str | None,
        page_url: str,
        role: str,
        rights_status: str,
        access_approved: bool,
    ) -> WebsitePipelineResult:
        page = self.crawler.fetch_live(
            url=page_url,
            role=role,
            rights_status=rights_status,
            access_approved=access_approved,
        )
        intake = self.intake.ingest_html(
            workspace_id=workspace_id,
            page_url=page.url,
            html=page.html,
            role=role,
            rights_status=rights_status,
        )

        if not intake.policy.may_store_binary:
            return WebsitePipelineResult(
                intake=intake,
                stored_asset_ids=(),
                failures=(),
            )

        stored_ids: list[str] = []
        failures: list[str] = []
        for asset_id, discovered in zip(intake.asset_ids, intake.discovered):
            try:
                fetched = self.media_transport.get(discovered.url)
                blob = self.blob_store.put(fetched.payload, suffix=fetched.suffix)
                existing = self.assets.get(asset_id)
                metadata = dict(existing.metadata if existing is not None else {})
                metadata.update(
                    {
                        "contentType": fetched.content_type,
                        "sizeBytes": blob.size_bytes,
                        "fetchedFrom": fetched.url,
                    }
                )
                self.assets.upsert(
                    StoredAsset(
                        asset_id=asset_id,
                        workspace_id=workspace_id,
                        source_type=(
                            existing.source_type
                            if existing is not None
                            else ("primary_website" if role == "primary" else "secondary_reference")
                        ),
                        source_url=discovered.url,
                        role=role,
                        rights_status=rights_status,
                        content_hash=blob.content_hash,
                        storage_uri=blob.uri,
                        metadata=metadata,
                    )
                )
                stored_ids.append(asset_id)
            except Exception as exc:
                failures.append(f"{asset_id}:{type(exc).__name__}")

        return WebsitePipelineResult(
            intake=intake,
            stored_asset_ids=tuple(stored_ids),
            failures=tuple(failures),
        )
