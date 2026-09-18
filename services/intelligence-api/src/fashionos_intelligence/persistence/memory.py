from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from fashionos_intelligence.persistence.db import MemoryRow


@dataclass(frozen=True)
class StoredMemory:
    memory_id: str
    memory_type: str
    scope: str
    content: str
    evidence_ids: list[str]
    status: str
    weight: float
    created_at: str
    updated_at: str


class MemoryRepository:
    def __init__(self, sessions: sessionmaker[Session]):
        self.sessions = sessions

    def upsert(self, record: StoredMemory) -> StoredMemory:
        with self.sessions() as session:
            row = session.get(MemoryRow, record.memory_id)
            if row is None:
                row = MemoryRow(memory_id=record.memory_id)
                session.add(row)
            row.memory_type = record.memory_type
            row.scope = record.scope
            row.content = record.content
            row.evidence_ids = list(record.evidence_ids)
            row.status = record.status
            row.weight = record.weight
            row.updated_at = datetime.now(timezone.utc)
            session.commit()
        return record

    def list_active(
        self,
        *,
        memory_type: str | None = None,
        scope: str | None = None,
    ) -> list[StoredMemory]:
        with self.sessions() as session:
            query = select(MemoryRow).where(MemoryRow.status == "active")
            if memory_type is not None:
                query = query.where(MemoryRow.memory_type == memory_type)
            if scope is not None:
                query = query.where(MemoryRow.scope == scope)
            rows = session.scalars(query).all()
            return [self._to_stored(row) for row in rows]

    def get(self, memory_id: str) -> StoredMemory | None:
        with self.sessions() as session:
            row = session.get(MemoryRow, memory_id)
            return None if row is None else self._to_stored(row)

    @staticmethod
    def _to_stored(row: MemoryRow) -> StoredMemory:
        return StoredMemory(
            memory_id=row.memory_id,
            memory_type=row.memory_type,
            scope=row.scope,
            content=row.content,
            evidence_ids=list(row.evidence_ids or []),
            status=row.status,
            weight=float(row.weight),
            created_at=row.created_at.isoformat(),
            updated_at=row.updated_at.isoformat(),
        )
