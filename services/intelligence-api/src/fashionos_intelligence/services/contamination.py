from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class ContaminationReport:
    dominant_group: str | None
    dominant_share: float
    flags: tuple[str, ...]
    promotion_blocked: bool


class ContaminationMonitor:
    def evaluate(
        self,
        origins: list[str],
        *,
        dominance_threshold: float = 0.6,
        minimum_sample: int = 5,
    ) -> ContaminationReport:
        if not origins:
            return ContaminationReport(None, 0.0, ("NO_ORIGIN_DATA",), True)

        counts = Counter(origins)
        dominant_group, dominant_count = counts.most_common(1)[0]
        share = dominant_count / len(origins)
        flags: list[str] = []

        if len(origins) < minimum_sample:
            flags.append("INSUFFICIENT_SAMPLE")

        if share > dominance_threshold:
            flags.append("SOURCE_CONCENTRATION")

        return ContaminationReport(
            dominant_group=dominant_group,
            dominant_share=round(share, 4),
            flags=tuple(flags),
            promotion_blocked=bool(flags),
        )
