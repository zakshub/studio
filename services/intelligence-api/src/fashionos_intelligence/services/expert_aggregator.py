from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict


@dataclass(frozen=True)
class ExpertContribution:
    expert_id: str
    council: str
    principle: str
    evidence_ids: tuple[str, ...]
    confidence: str
    domain_weight: float = 1.0


@dataclass(frozen=True)
class AggregatedInsight:
    council: str
    principles: tuple[str, ...]
    expert_ids: tuple[str, ...]
    disagreements: tuple[str, ...]
    confidence: str


class ExpertAggregator:
    """Combine expert-derived principles without flattening experts into one style."""

    _CONF = {"low": 0.35, "medium": 0.65, "high": 0.9}

    def aggregate(
        self,
        contributions: list[ExpertContribution],
        selected_councils: list[str],
        max_principles_per_council: int = 5,
    ) -> list[AggregatedInsight]:
        selected = set(selected_councils)
        groups: dict[str, list[ExpertContribution]] = defaultdict(list)
        for item in contributions:
            if item.council in selected:
                groups[item.council].append(item)

        output: list[AggregatedInsight] = []
        for council in sorted(groups):
            group = groups[council]
            ranked = sorted(
                group,
                key=lambda x: (
                    -(self._CONF.get(x.confidence, 0.0) * x.domain_weight),
                    x.expert_id,
                    x.principle,
                ),
            )
            principles: list[str] = []
            experts: set[str] = set()
            for item in ranked:
                if item.principle not in principles:
                    principles.append(item.principle)
                experts.add(item.expert_id)
                if len(principles) >= max_principles_per_council:
                    break

            # Explicit disagreement markers are preserved instead of averaged away.
            disagreement_map: dict[str, set[str]] = defaultdict(set)
            for item in group:
                normalized = item.principle.lower()
                if normalized.startswith("prefer:"):
                    disagreement_map["preference"].add(item.principle)
                if normalized.startswith("avoid:"):
                    disagreement_map["preference"].add(item.principle)
            disagreements = tuple(
                sorted(v)
                for v in disagreement_map.values()
                if len(v) > 1
            )
            flattened = tuple(x for group_ in disagreements for x in group_)

            avg = sum(
                self._CONF.get(i.confidence, 0.0) * i.domain_weight for i in group
            ) / max(1, len(group))
            confidence = "high" if avg >= 0.78 else "medium" if avg >= 0.5 else "low"

            output.append(
                AggregatedInsight(
                    council=council,
                    principles=tuple(principles),
                    expert_ids=tuple(sorted(experts)),
                    disagreements=flattened,
                    confidence=confidence,
                )
            )
        return output
