from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class LineageEdge:
    parent_asset_id: str
    child_asset_id: str
    relation: str


@dataclass(frozen=True)
class ProvenanceRecord:
    execution_id: str
    task_id: str
    brain_revision: str
    source_asset_ids: tuple[str, ...]
    output_asset_ids: tuple[str, ...]
    knowledge_unit_ids: tuple[str, ...]
    qc_status: str
    created_at: str


class ProvenanceService:
    def create_record(
        self,
        *,
        task_id: str,
        brain_revision: str,
        source_asset_ids: list[str],
        output_asset_ids: list[str],
        knowledge_unit_ids: list[str],
        qc_status: str,
    ) -> ProvenanceRecord:
        if not brain_revision:
            raise ValueError("PROVENANCE_INCOMPLETE")
        return ProvenanceRecord(
            execution_id=f"exec_{uuid4().hex[:16]}",
            task_id=task_id,
            brain_revision=brain_revision,
            source_asset_ids=tuple(source_asset_ids),
            output_asset_ids=tuple(output_asset_ids),
            knowledge_unit_ids=tuple(knowledge_unit_ids),
            qc_status=qc_status,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def lineage(
        self,
        source_asset_ids: list[str],
        output_asset_ids: list[str],
    ) -> list[LineageEdge]:
        return [
            LineageEdge(parent, child, "derived_from")
            for parent in source_asset_ids
            for child in output_asset_ids
        ]
