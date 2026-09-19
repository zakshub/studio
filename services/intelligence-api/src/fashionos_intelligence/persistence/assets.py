from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session, sessionmaker

from fashionos_intelligence.persistence.db import AssetRow


@dataclass(frozen=True)
class StoredAsset:
    asset_id: str
    workspace_id: str | None
    source_type: str
    source_url: str | None
    role: str
    rights_status: str
    content_hash: str | None
    storage_uri: str | None
    metadata: dict


class AssetRepository:
    def __init__(self, sessions: sessionmaker[Session]):
        self.sessions = sessions

    def upsert(self, asset: StoredAsset) -> StoredAsset:
        with self.sessions() as session:
            row = session.get(AssetRow, asset.asset_id)
            if row is None:
                row = AssetRow(asset_id=asset.asset_id)
                session.add(row)
            row.workspace_id = asset.workspace_id
            row.source_type = asset.source_type
            row.source_url = asset.source_url
            row.role = asset.role
            row.rights_status = asset.rights_status
            row.content_hash = asset.content_hash
            row.storage_uri = asset.storage_uri
            row.metadata_json = dict(asset.metadata)
            session.commit()
        return asset

    def get(self, asset_id: str) -> StoredAsset | None:
        with self.sessions() as session:
            row = session.get(AssetRow, asset_id)
            if row is None:
                return None
            return StoredAsset(
                asset_id=row.asset_id,
                workspace_id=row.workspace_id,
                source_type=row.source_type,
                source_url=row.source_url,
                role=row.role,
                rights_status=row.rights_status,
                content_hash=row.content_hash,
                storage_uri=row.storage_uri,
                metadata=dict(row.metadata_json or {}),
            )
