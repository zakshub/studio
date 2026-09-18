from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MetaCheck:
    confidence: str
    flags: tuple[str, ...]
    research_questions: tuple[str, ...]
    human_review_required: bool


class MetacognitionService:
    def check(
        self,
        *,
        evidence_count: int,
        independent_source_count: int,
        contradiction_count: int,
        unknown_count: int,
        expert_council_count: int,
        high_risk: bool = False,
    ) -> MetaCheck:
        flags: list[str] = []
        questions: list[str] = []

        if evidence_count == 0:
            flags.append("NO_EVIDENCE")
            questions.append("What evidence is required before this decision can be trusted?")

        if evidence_count > 0 and independent_source_count < 2:
            flags.append("LOW_SOURCE_DIVERSITY")
            questions.append("Can the observation be verified through an independent source?")

        if contradiction_count > 0:
            flags.append("CONTRADICTION_PRESENT")
            questions.append("Under which contexts are the conflicting observations each valid?")

        if unknown_count > 0:
            flags.append("UNRESOLVED_UNKNOWNS")

        if expert_council_count == 0 and evidence_count > 0:
            flags.append("NO_SPECIALIST_COUNCIL_SELECTED")

        if high_risk:
            flags.append("HIGH_RISK_DECISION")

        severity = len(flags)
        if high_risk or contradiction_count > 1 or "NO_EVIDENCE" in flags:
            confidence = "low"
        elif severity >= 2:
            confidence = "medium"
        else:
            confidence = "high"

        return MetaCheck(
            confidence=confidence,
            flags=tuple(flags),
            research_questions=tuple(questions),
            human_review_required=high_risk or confidence == "low",
        )
