from __future__ import annotations

from dataclasses import dataclass

from fashionos_intelligence.services.expert_councils import ExpertCouncilSelector
from fashionos_intelligence.services.metacognition import MetacognitionService
from fashionos_intelligence.services.value_system import ValueSystem


@dataclass(frozen=True)
class CognitionPlan:
    stages: tuple[str, ...]
    councils: tuple[str, ...]
    value_allowed: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    confidence: str
    metacognitive_flags: tuple[str, ...]
    research_questions: tuple[str, ...]
    human_review_required: bool


class CognitionService:
    def __init__(self) -> None:
        self.values = ValueSystem()
        self.councils = ExpertCouncilSelector()
        self.meta = MetacognitionService()

    def plan(
        self,
        *,
        mode: str,
        capabilities: list[str],
        rights_statuses: list[str],
        hard_locks: list[str],
        requested_changes: list[str],
        preservation_required: bool,
        evidence_count: int,
        independent_source_count: int,
        contradiction_count: int,
        unknown_count: int,
        high_risk: bool,
    ) -> CognitionPlan:
        selected = self.councils.select(capabilities, mode)
        value = self.values.evaluate(
            rights_statuses=rights_statuses,
            preservation_required=preservation_required,
            hard_locks=hard_locks,
            requested_changes=requested_changes,
            unresolved_critical_uncertainty=high_risk and unknown_count > 0,
        )
        meta = self.meta.check(
            evidence_count=evidence_count,
            independent_source_count=independent_source_count,
            contradiction_count=contradiction_count,
            unknown_count=unknown_count,
            expert_council_count=len(selected),
            high_risk=high_risk,
        )
        return CognitionPlan(
            stages=(
                "ORIENT",
                "ATTEND",
                "FRAME",
                "RECALL",
                "DIVERGE",
                "SIMULATE",
                "CONSULT",
                "CRITIQUE",
                "CONVERGE",
                "DECIDE",
                "EXECUTE",
                "VERIFY",
                "REFLECT",
                "LEARN",
            ),
            councils=tuple(selected),
            value_allowed=value.allowed,
            blockers=value.blockers,
            warnings=value.warnings,
            confidence=meta.confidence,
            metacognitive_flags=meta.flags,
            research_questions=meta.research_questions,
            human_review_required=meta.human_review_required or not value.allowed,
        )
