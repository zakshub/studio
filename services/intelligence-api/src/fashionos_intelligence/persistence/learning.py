from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session, sessionmaker

from fashionos_intelligence.persistence.db import LearningCandidateRow


@dataclass(frozen=True)
class StoredLearningCandidate:
    candidate_id: str
    observation: str
    proposed_principle: str
    scope: str
    evidence_ids: list[str]
    confidence: str
    decision_status: str
    created_at: str
    decided_at: str | None


class LearningRepository:
    def __init__(self, sessions: sessionmaker[Session]):
        self.sessions = sessions

    def upsert(self, candidate: StoredLearningCandidate) -> StoredLearningCandidate:
        with self.sessions() as session:
            row = session.get(LearningCandidateRow, candidate.candidate_id)
            if row is None:
                row = LearningCandidateRow(candidate_id=candidate.candidate_id)
                session.add(row)
            row.observation = candidate.observation
            row.proposed_principle = candidate.proposed_principle
            row.scope = candidate.scope
            row.evidence_ids = list(candidate.evidence_ids)
            row.confidence = candidate.confidence
            row.decision_status = candidate.decision_status
            row.created_at = datetime.fromisoformat(candidate.created_at)
            row.decided_at = (
                datetime.fromisoformat(candidate.decided_at)
                if candidate.decided_at
                else None
            )
            session.commit()
        return candidate

    def get(self, candidate_id: str) -> StoredLearningCandidate | None:
        with self.sessions() as session:
            row = session.get(LearningCandidateRow, candidate_id)
            if row is None:
                return None
            return StoredLearningCandidate(
                candidate_id=row.candidate_id,
                observation=row.observation,
                proposed_principle=row.proposed_principle,
                scope=row.scope,
                evidence_ids=list(row.evidence_ids or []),
                confidence=row.confidence,
                decision_status=row.decision_status,
                created_at=row.created_at.isoformat(),
                decided_at=row.decided_at.isoformat() if row.decided_at else None,
            )
