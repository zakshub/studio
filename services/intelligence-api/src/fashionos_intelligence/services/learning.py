from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from fashionos_intelligence.persistence.learning import LearningRepository, StoredLearningCandidate


@dataclass
class LearningCandidate:
    candidate_id: str
    observation: str
    proposed_principle: str
    scope: str
    evidence_ids: list[str]
    confidence: str
    decision_status: str
    created_at: str
    decided_at: str | None = None


class LearningService:
    def __init__(self, repository: LearningRepository | None = None) -> None:
        self._candidates: dict[str, LearningCandidate] = {}
        self.repository = repository

    def create(
        self,
        *,
        observation: str,
        proposed_principle: str,
        scope: str,
        evidence_ids: list[str],
        confidence: str,
    ) -> LearningCandidate:
        candidate = LearningCandidate(
            candidate_id=f"learn_{uuid4().hex[:16]}",
            observation=observation,
            proposed_principle=proposed_principle,
            scope=scope,
            evidence_ids=list(evidence_ids),
            confidence=confidence,
            decision_status="pending",
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._candidates[candidate.candidate_id] = candidate
        self._persist(candidate)
        return candidate

    def get(self, candidate_id: str) -> LearningCandidate | None:
        candidate = self._candidates.get(candidate_id)
        if candidate is not None:
            return candidate
        if self.repository is None:
            return None
        stored = self.repository.get(candidate_id)
        if stored is None:
            return None
        candidate = self._from_stored(stored)
        self._candidates[candidate_id] = candidate
        return candidate

    def promote(self, candidate_id: str, *, human_approved: bool) -> LearningCandidate:
        candidate = self._require(candidate_id)
        if not human_approved:
            raise PermissionError("HUMAN_APPROVAL_REQUIRED")
        if not candidate.evidence_ids:
            raise ValueError("EVIDENCE_REQUIRED")
        if candidate.confidence == "low":
            raise ValueError("LOW_CONFIDENCE_CANNOT_PROMOTE")
        candidate.decision_status = "promoted"
        candidate.decided_at = datetime.now(timezone.utc).isoformat()
        self._persist(candidate)
        return candidate

    def reject(self, candidate_id: str) -> LearningCandidate:
        candidate = self._require(candidate_id)
        candidate.decision_status = "rejected"
        candidate.decided_at = datetime.now(timezone.utc).isoformat()
        self._persist(candidate)
        return candidate

    def _require(self, candidate_id: str) -> LearningCandidate:
        candidate = self.get(candidate_id)
        if candidate is None:
            raise KeyError("LEARNING_CANDIDATE_NOT_FOUND")
        return candidate

    def _persist(self, candidate: LearningCandidate) -> None:
        if self.repository is None:
            return
        self.repository.upsert(
            StoredLearningCandidate(
                candidate_id=candidate.candidate_id,
                observation=candidate.observation,
                proposed_principle=candidate.proposed_principle,
                scope=candidate.scope,
                evidence_ids=list(candidate.evidence_ids),
                confidence=candidate.confidence,
                decision_status=candidate.decision_status,
                created_at=candidate.created_at,
                decided_at=candidate.decided_at,
            )
        )

    @staticmethod
    def _from_stored(candidate: StoredLearningCandidate) -> LearningCandidate:
        return LearningCandidate(
            candidate_id=candidate.candidate_id,
            observation=candidate.observation,
            proposed_principle=candidate.proposed_principle,
            scope=candidate.scope,
            evidence_ids=list(candidate.evidence_ids),
            confidence=candidate.confidence,
            decision_status=candidate.decision_status,
            created_at=candidate.created_at,
            decided_at=candidate.decided_at,
        )
