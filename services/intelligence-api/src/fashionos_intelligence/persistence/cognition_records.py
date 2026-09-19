from __future__ import annotations

from dataclasses import dataclass
from sqlalchemy.orm import Session, sessionmaker

from fashionos_intelligence.persistence.db import DecisionRow, PracticeSessionRow, ObservationRow


@dataclass(frozen=True)
class StoredDecision:
    decision_id: str
    task_id: str | None
    payload: dict


@dataclass(frozen=True)
class StoredPractice:
    session_id: str
    target_principle: str
    mode: str
    status: str
    payload: dict


@dataclass(frozen=True)
class StoredObservation:
    observation_id: str
    source_id: str
    media_type: str
    dimension: str
    value: str
    confidence: str
    evidence_ref: str | None
    interpretation: bool


class DecisionRepository:
    def __init__(self, sessions: sessionmaker[Session]):
        self.sessions = sessions

    def upsert(self, item: StoredDecision) -> StoredDecision:
        with self.sessions() as session:
            row = session.get(DecisionRow, item.decision_id)
            if row is None:
                row = DecisionRow(decision_id=item.decision_id)
                session.add(row)
            row.task_id = item.task_id
            row.payload = dict(item.payload)
            session.commit()
        return item


class PracticeRepository:
    def __init__(self, sessions: sessionmaker[Session]):
        self.sessions = sessions

    def upsert(self, item: StoredPractice) -> StoredPractice:
        with self.sessions() as session:
            row = session.get(PracticeSessionRow, item.session_id)
            if row is None:
                row = PracticeSessionRow(session_id=item.session_id)
                session.add(row)
            row.target_principle = item.target_principle
            row.mode = item.mode
            row.status = item.status
            row.payload = dict(item.payload)
            session.commit()
        return item


class ObservationRepository:
    def __init__(self, sessions: sessionmaker[Session]):
        self.sessions = sessions

    def upsert(self, item: StoredObservation) -> StoredObservation:
        with self.sessions() as session:
            row = session.get(ObservationRow, item.observation_id)
            if row is None:
                row = ObservationRow(observation_id=item.observation_id)
                session.add(row)
            row.source_id = item.source_id
            row.media_type = item.media_type
            row.dimension = item.dimension
            row.value = item.value
            row.confidence = item.confidence
            row.evidence_ref = item.evidence_ref
            row.interpretation = item.interpretation
            session.commit()
        return item
