from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from fashionos_intelligence.persistence.memory import MemoryRepository, StoredMemory


@dataclass
class MemoryRecord:
    memory_id: str
    memory_type: str
    scope: str
    content: str
    evidence_ids: list[str]
    status: str
    weight: float
    created_at: str
    updated_at: str


class MemoryService:
    def __init__(self, repository: MemoryRepository | None = None) -> None:
        self._records: dict[str, MemoryRecord] = {}
        self.repository = repository

    def remember(
        self,
        *,
        memory_type: str,
        scope: str,
        content: str,
        evidence_ids: list[str] | None = None,
        weight: float = 1.0,
    ) -> MemoryRecord:
        now = datetime.now(timezone.utc).isoformat()
        record = MemoryRecord(
            memory_id=f"mem_{uuid4().hex[:16]}",
            memory_type=memory_type,
            scope=scope,
            content=content,
            evidence_ids=list(evidence_ids or []),
            status="active",
            weight=max(0.0, min(1.0, weight)),
            created_at=now,
            updated_at=now,
        )
        self._records[record.memory_id] = record
        self._persist(record)
        return record

    def retrieve(
        self,
        *,
        memory_type: str | None = None,
        scope: str | None = None,
    ) -> list[MemoryRecord]:
        if self.repository is not None:
            return [
                self._from_stored(item)
                for item in self.repository.list_active(
                    memory_type=memory_type,
                    scope=scope,
                )
            ]

        records = list(self._records.values())
        if memory_type is not None:
            records = [r for r in records if r.memory_type == memory_type]
        if scope is not None:
            records = [r for r in records if r.scope == scope]
        return [r for r in records if r.status == "active"]

    def deprecate(self, memory_id: str, reason: str) -> MemoryRecord:
        record = self._get(memory_id)
        record.status = "deprecated"
        record.content = f"{record.content}\n[Deprecated: {reason}]"
        record.updated_at = datetime.now(timezone.utc).isoformat()
        self._records[record.memory_id] = record
        self._persist(record)
        return record

    def decay(self, memory_id: str, amount: float) -> MemoryRecord:
        record = self._get(memory_id)
        record.weight = max(0.0, record.weight - max(0.0, amount))
        record.updated_at = datetime.now(timezone.utc).isoformat()
        self._records[record.memory_id] = record
        self._persist(record)
        return record

    def _get(self, memory_id: str) -> MemoryRecord:
        record = self._records.get(memory_id)
        if record is not None:
            return record
        if self.repository is not None:
            stored = self.repository.get(memory_id)
            if stored is not None:
                record = self._from_stored(stored)
                self._records[memory_id] = record
                return record
        raise KeyError("MEMORY_NOT_FOUND")

    def _persist(self, record: MemoryRecord) -> None:
        if self.repository is None:
            return
        self.repository.upsert(
            StoredMemory(
                memory_id=record.memory_id,
                memory_type=record.memory_type,
                scope=record.scope,
                content=record.content,
                evidence_ids=list(record.evidence_ids),
                status=record.status,
                weight=record.weight,
                created_at=record.created_at,
                updated_at=record.updated_at,
            )
        )

    @staticmethod
    def _from_stored(record: StoredMemory) -> MemoryRecord:
        return MemoryRecord(
            memory_id=record.memory_id,
            memory_type=record.memory_type,
            scope=record.scope,
            content=record.content,
            evidence_ids=list(record.evidence_ids),
            status=record.status,
            weight=record.weight,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
