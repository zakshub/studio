from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from fashionos_intelligence.persistence.runtime_records import (
    ProvenanceRepository,
    StoredProvenance,
)


@dataclass(frozen=True)
class LineageEdge:
    parent_asset_id: str
    child_asset_id: str
    relation: str


@dataclass(frozen=True)
class ProvenanceRecord:
    provenance_id: str
    execution_id: str
    task_id: str
    brain_revision: str
    source_asset_ids: tuple[str, ...]
    output_asset_ids: tuple[str, ...]
    knowledge_unit_ids: tuple[str, ...]
    qc_status: str
    created_at: str


class ProvenanceService:
    def __init__(self, repository: ProvenanceRepository | None = None) -> None:
        self.repository = repository

    def create_record(
        self,
        *,
        execution_id: str,
        task_id: str,
        brain_revision: str,
        source_asset_ids: list[str],
        output_asset_ids: list[str],
        knowledge_unit_ids: list[str],
        qc_status: str,
    ) -> ProvenanceRecord:
        if not brain_revision:
            raise ValueError("PROVENANCE_INCOMPLETE")
        provenance_id = f"prov_{uuid4().hex[:16]}"
        record = ProvenanceRecord(
            provenance_id=provenance_id,
            execution_id=execution_id,
            task_id=task_id,
            brain_revision=brain_revision,
            source_asset_ids=tuple(source_asset_ids),
            output_asset_ids=tuple(output_asset_ids),
            knowledge_unit_ids=tuple(knowledge_unit_ids),
            qc_status=qc_status,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        if self.repository is not None:
            edges = self.lineage(source_asset_ids, output_asset_ids)
            self.repository.upsert(
                StoredProvenance(
                    provenance_id=record.provenance_id,
                    execution_id=record.execution_id,
                    task_id=record.task_id,
                    brain_revision=record.brain_revision,
                    source_asset_ids=list(record.source_asset_ids),
                    output_asset_ids=list(record.output_asset_ids),
                    knowledge_unit_ids=list(record.knowledge_unit_ids),
                    qc_status=record.qc_status,
                    lineage=[
                        {
                            "parentAssetId": edge.parent_asset_id,
                            "childAssetId": edge.child_asset_id,
                            "relation": edge.relation,
                        }
                        for edge in edges
                    ],
                )
            )
        return record

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
