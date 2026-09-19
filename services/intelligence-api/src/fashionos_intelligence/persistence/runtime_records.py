from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session, sessionmaker

from fashionos_intelligence.persistence.db import (
    ApprovalRow,
    ExecutionRecordRow,
    ProvenanceRow,
    QCResultRow,
)


@dataclass(frozen=True)
class StoredExecution:
    execution_id: str
    task_id: str
    brain_revision: str
    source_asset_ids: list[str]
    output_asset_ids: list[str]
    knowledge_unit_ids: list[str]
    executor_class: str | None
    status: str
    payload: dict


@dataclass(frozen=True)
class StoredQC:
    qc_id: str
    execution_id: str
    status: str
    dimensions: dict
    critical_failures: list[str]
    requires_rework: bool
    human_review_required: bool


@dataclass(frozen=True)
class StoredApproval:
    approval_id: str
    workspace_id: str
    task_id: str
    subject_type: str
    subject_id: str
    status: str
    reason: str | None = None
    decided_by: str | None = None


@dataclass(frozen=True)
class StoredProvenance:
    provenance_id: str
    execution_id: str
    task_id: str
    brain_revision: str
    source_asset_ids: list[str]
    output_asset_ids: list[str]
    knowledge_unit_ids: list[str]
    qc_status: str
    lineage: list[dict]


class ExecutionRepository:
    def __init__(self, sessions: sessionmaker[Session]):
        self.sessions = sessions

    def upsert(self, item: StoredExecution) -> StoredExecution:
        with self.sessions() as session:
            row = session.get(ExecutionRecordRow, item.execution_id)
            if row is None:
                row = ExecutionRecordRow(execution_id=item.execution_id)
                session.add(row)
            row.task_id = item.task_id
            row.brain_revision = item.brain_revision
            row.source_asset_ids = list(item.source_asset_ids)
            row.output_asset_ids = list(item.output_asset_ids)
            row.knowledge_unit_ids = list(item.knowledge_unit_ids)
            row.executor_class = item.executor_class
            row.status = item.status
            row.payload = dict(item.payload)
            session.commit()
        return item

    def get(self, execution_id: str) -> StoredExecution | None:
        with self.sessions() as session:
            row = session.get(ExecutionRecordRow, execution_id)
            if row is None:
                return None
            return StoredExecution(
                execution_id=row.execution_id,
                task_id=row.task_id,
                brain_revision=row.brain_revision,
                source_asset_ids=list(row.source_asset_ids or []),
                output_asset_ids=list(row.output_asset_ids or []),
                knowledge_unit_ids=list(row.knowledge_unit_ids or []),
                executor_class=row.executor_class,
                status=row.status,
                payload=dict(row.payload or {}),
            )


class QCRepository:
    def __init__(self, sessions: sessionmaker[Session]):
        self.sessions = sessions

    def upsert(self, item: StoredQC) -> StoredQC:
        with self.sessions() as session:
            row = session.get(QCResultRow, item.qc_id)
            if row is None:
                row = QCResultRow(qc_id=item.qc_id)
                session.add(row)
            row.execution_id = item.execution_id
            row.status = item.status
            row.dimensions = dict(item.dimensions)
            row.critical_failures = list(item.critical_failures)
            row.requires_rework = item.requires_rework
            row.human_review_required = item.human_review_required
            session.commit()
        return item


class ApprovalRepository:
    def __init__(self, sessions: sessionmaker[Session]):
        self.sessions = sessions

    def upsert(self, item: StoredApproval) -> StoredApproval:
        with self.sessions() as session:
            row = session.get(ApprovalRow, item.approval_id)
            if row is None:
                row = ApprovalRow(approval_id=item.approval_id)
                session.add(row)
            row.workspace_id = item.workspace_id
            row.task_id = item.task_id
            row.subject_type = item.subject_type
            row.subject_id = item.subject_id
            row.status = item.status
            row.reason = item.reason
            row.decided_by = item.decided_by
            if item.status in {"approved", "rejected", "cancelled"}:
                row.decided_at = datetime.now(timezone.utc)
            session.commit()
        return item


class ProvenanceRepository:
    def __init__(self, sessions: sessionmaker[Session]):
        self.sessions = sessions

    def upsert(self, item: StoredProvenance) -> StoredProvenance:
        with self.sessions() as session:
            row = session.get(ProvenanceRow, item.provenance_id)
            if row is None:
                row = ProvenanceRow(provenance_id=item.provenance_id)
                session.add(row)
            row.execution_id = item.execution_id
            row.task_id = item.task_id
            row.brain_revision = item.brain_revision
            row.source_asset_ids = list(item.source_asset_ids)
            row.output_asset_ids = list(item.output_asset_ids)
            row.knowledge_unit_ids = list(item.knowledge_unit_ids)
            row.qc_status = item.qc_status
            row.lineage = list(item.lineage)
            session.commit()
        return item
