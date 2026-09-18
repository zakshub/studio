from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


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
    def __init__(self) -> None:
        self._candidates: dict[str, LearningCandidate] = {}

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
        return candidate

    def get(self, candidate_id: str) -> LearningCandidate | None:
        return self._candidates.get(candidate_id)

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
        return candidate

    def reject(self, candidate_id: str) -> LearningCandidate:
        candidate = self._require(candidate_id)
        candidate.decision_status = "rejected"
        candidate.decided_at = datetime.now(timezone.utc).isoformat()
        return candidate

    def _require(self, candidate_id: str) -> LearningCandidate:
        candidate = self.get(candidate_id)
        if candidate is None:
            raise KeyError("LEARNING_CANDIDATE_NOT_FOUND")
        return candidate
