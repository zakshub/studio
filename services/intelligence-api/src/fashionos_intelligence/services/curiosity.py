from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class ResearchQuestion:
    question_id: str
    question: str
    reason: str
    affected_domains: tuple[str, ...]
    urgency: str
    evidence_needed: tuple[str, ...]


class CuriosityService:
    def generate(
        self,
        *,
        repeated_uncertainties: list[str],
        recurring_failures: list[str],
        contradictions: list[str],
        coverage_gaps: list[str],
        affected_domains: list[str],
    ) -> list[ResearchQuestion]:
        questions: list[ResearchQuestion] = []
        domains = tuple(sorted(set(affected_domains)))

        for uncertainty in repeated_uncertainties:
            questions.append(
                self._make(
                    f"What evidence would resolve: {uncertainty}?",
                    "REPEATED_UNCERTAINTY",
                    domains,
                    "high",
                    ("independent_primary_source", "controlled_observation"),
                )
            )

        for failure in recurring_failures:
            questions.append(
                self._make(
                    f"Which conditions repeatedly produce {failure}, and which remediation is reliable?",
                    "RECURRING_FAILURE",
                    domains,
                    "high",
                    ("failure_cases", "successful_repairs"),
                )
            )

        for contradiction in contradictions:
            questions.append(
                self._make(
                    f"Under which contexts are the conflicting claims valid: {contradiction}?",
                    "CONTRADICTION",
                    domains,
                    "medium",
                    ("independent_sources", "context_metadata"),
                )
            )

        for gap in coverage_gaps:
            questions.append(
                self._make(
                    f"What representative evidence is missing for {gap}?",
                    "COVERAGE_GAP",
                    domains,
                    "medium",
                    ("representative_sources",),
                )
            )

        return questions

    @staticmethod
    def _make(
        question: str,
        reason: str,
        domains: tuple[str, ...],
        urgency: str,
        evidence_needed: tuple[str, ...],
    ) -> ResearchQuestion:
        return ResearchQuestion(
            question_id=f"rq_{uuid4().hex[:16]}",
            question=question,
            reason=reason,
            affected_domains=domains,
            urgency=urgency,
            evidence_needed=evidence_needed,
        )
