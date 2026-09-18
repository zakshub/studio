from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class CoverageReport:
    total: int
    dominant_values: dict[str, tuple[str, float]]
    underrepresented: dict[str, tuple[str, ...]]
    warnings: tuple[str, ...]


class CoverageMonitor:
    def evaluate(
        self,
        records: list[dict[str, str]],
        dimensions: list[str],
        known_values: dict[str, list[str]] | None = None,
        dominance_threshold: float = 0.7,
    ) -> CoverageReport:
        total = len(records)
        dominant: dict[str, tuple[str, float]] = {}
        under: dict[str, tuple[str, ...]] = {}
        warnings: list[str] = []

        for dim in dimensions:
            values = [r[dim] for r in records if r.get(dim)]
            if values:
                counts = Counter(values)
                value, count = counts.most_common(1)[0]
                ratio = count / len(values)
                dominant[dim] = (value, ratio)
                if ratio >= dominance_threshold and len(counts) > 1:
                    warnings.append(f"DOMINANCE:{dim}:{value}")
            if known_values and dim in known_values:
                present = set(values)
                missing = tuple(sorted(v for v in known_values[dim] if v not in present))
                if missing:
                    under[dim] = missing

        return CoverageReport(
            total=total,
            dominant_values=dominant,
            underrepresented=under,
            warnings=tuple(sorted(warnings)),
        )
