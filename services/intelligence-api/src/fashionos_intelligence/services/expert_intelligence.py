from __future__ import annotations

from dataclasses import dataclass

from fashionos_intelligence.services.expert_aggregator import (
    AggregatedInsight,
    ExpertAggregator,
    ExpertContribution,
)
from fashionos_intelligence.services.expert_profiles import ExpertProfile


@dataclass(frozen=True)
class ExpertConsultation:
    selected_experts: tuple[str, ...]
    insights: tuple[AggregatedInsight, ...]


class ExpertIntelligenceService:
    def __init__(
        self,
        profiles: list[ExpertProfile],
        aggregator: ExpertAggregator | None = None,
    ) -> None:
        self.profiles = profiles
        self.aggregator = aggregator or ExpertAggregator()

    def consult(
        self,
        *,
        councils: list[str],
        max_experts: int = 12,
        max_principles_per_council: int = 5,
    ) -> ExpertConsultation:
        selected_councils = set(councils)
        candidates = [
            profile
            for profile in self.profiles
            if selected_councils.intersection(profile.councils)
        ]
        candidates.sort(
            key=lambda profile: (
                -len(selected_councils.intersection(profile.councils)),
                profile.expert_id,
            )
        )
        selected = candidates[:max_experts]

        contributions: list[ExpertContribution] = []
        for profile in selected:
            matched_councils = sorted(selected_councils.intersection(profile.councils))
            for council in matched_councils:
                for principle in profile.principles:
                    contributions.append(
                        ExpertContribution(
                            expert_id=profile.expert_id,
                            council=council,
                            principle=principle.principle,
                            evidence_ids=principle.evidence,
                            confidence="medium",
                            domain_weight=1.0,
                        )
                    )

        insights = self.aggregator.aggregate(
            contributions,
            list(councils),
            max_principles_per_council=max_principles_per_council,
        )
        return ExpertConsultation(
            selected_experts=tuple(profile.expert_id for profile in selected),
            insights=tuple(insights),
        )
