from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class DecisionRecord:
    decision_id: str
    objective: str
    selected_option: str
    alternatives_considered: tuple[str, ...]
    retrieved_knowledge_ids: tuple[str, ...]
    expert_councils: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    confidence: str
    flags: tuple[str, ...]
    unresolved_risks: tuple[str, ...]
    human_review_required: bool
    created_at: str


class DecisionRecordService:
    def create(
        self,
        *,
        objective: str,
        selected_option: str,
        alternatives_considered: list[str],
        retrieved_knowledge_ids: list[str],
        expert_councils: list[str],
        evidence_ids: list[str],
        blockers: list[str],
        warnings: list[str],
        confidence: str,
        flags: list[str],
        unresolved_risks: list[str],
        human_review_required: bool,
    ) -> DecisionRecord:
        return DecisionRecord(
            decision_id=f"decision_{uuid4().hex[:16]}",
            objective=objective,
            selected_option=selected_option,
            alternatives_considered=tuple(alternatives_considered),
            retrieved_knowledge_ids=tuple(retrieved_knowledge_ids),
            expert_councils=tuple(expert_councils),
            evidence_ids=tuple(evidence_ids),
            blockers=tuple(blockers),
            warnings=tuple(warnings),
            confidence=confidence,
            flags=tuple(flags),
            unresolved_risks=tuple(unresolved_risks),
            human_review_required=human_review_required,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
