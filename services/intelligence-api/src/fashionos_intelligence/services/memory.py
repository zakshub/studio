from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


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
    def __init__(self) -> None:
        self._records: dict[str, MemoryRecord] = {}

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
        return record

    def retrieve(self, *, memory_type: str | None = None, scope: str | None = None) -> list[MemoryRecord]:
        records = list(self._records.values())
        if memory_type is not None:
            records = [r for r in records if r.memory_type == memory_type]
        if scope is not None:
            records = [r for r in records if r.scope == scope]
        return [r for r in records if r.status == "active"]

    def deprecate(self, memory_id: str, reason: str) -> MemoryRecord:
        record = self._records.get(memory_id)
        if record is None:
            raise KeyError("MEMORY_NOT_FOUND")
        record.status = "deprecated"
        record.content = f"{record.content}\n[Deprecated: {reason}]"
        record.updated_at = datetime.now(timezone.utc).isoformat()
        return record

    def decay(self, memory_id: str, amount: float) -> MemoryRecord:
        record = self._records.get(memory_id)
        if record is None:
            raise KeyError("MEMORY_NOT_FOUND")
        record.weight = max(0.0, record.weight - max(0.0, amount))
        record.updated_at = datetime.now(timezone.utc).isoformat()
        return record
