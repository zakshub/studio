from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from uuid import uuid4

from fashionos_intelligence.persistence.assets import AssetRepository, StoredAsset
from fashionos_intelligence.services.source_harvester import DiscoveredMedia, WebsiteHarvester
from fashionos_intelligence.services.source_policy import SourcePolicy, SourcePolicyDecision


@dataclass(frozen=True)
class WebsiteIntakeResult:
    source_url: str
    policy: SourcePolicyDecision
    discovered: tuple[DiscoveredMedia, ...]
    asset_ids: tuple[str, ...]


class WebsiteIntakeService:
    """Turns an approved fetched page into traceable asset metadata.

    It does not download discovered binaries. Binary acquisition is a separate,
    rights-gated step so reference-only sources cannot silently enter production storage.
    """

    def __init__(self, asset_repository: AssetRepository | None = None) -> None:
        self.assets = asset_repository
        self.harvester = WebsiteHarvester()
        self.policy = SourcePolicy()

    def ingest_html(
        self,
        *,
        workspace_id: str | None,
        page_url: str,
        html: str,
        role: str,
        rights_status: str,
    ) -> WebsiteIntakeResult:
        decision = self.policy.decide(role=role, rights_status=rights_status)
        if not decision.may_analyze:
            raise PermissionError("SOURCE_ANALYSIS_NOT_ALLOWED")

        discovered = self.harvester.discover(page_url=page_url, html=html)
        asset_ids: list[str] = []
        for media in discovered:
            stable = sha256(
                f"{page_url}|{media.media_type}|{media.url}".encode("utf-8")
            ).hexdigest()[:20]
            asset_id = f"asset_web_{stable}"
            asset_ids.append(asset_id)
            if self.assets is not None:
                self.assets.upsert(
                    StoredAsset(
                        asset_id=asset_id,
                        workspace_id=workspace_id,
                        source_type="primary_website" if role == "primary" else "secondary_reference",
                        source_url=media.url,
                        role=role,
                        rights_status=rights_status,
                        content_hash=None,
                        storage_uri=None,
                        metadata={
                            "discoveredFrom": page_url,
                            "mediaType": media.media_type,
                            "alt": media.alt,
                            "binaryStorageAllowed": decision.may_store_binary,
                            "publicationAllowed": decision.may_publish,
                        },
                    )
                )
        return WebsiteIntakeResult(
            source_url=page_url,
            policy=decision,
            discovered=tuple(discovered),
            asset_ids=tuple(asset_ids),
        )
