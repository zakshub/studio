from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from uuid import uuid4

from fashionos_intelligence.persistence.benchmarks import (
    BenchmarkRepository,
    StoredBenchmark,
)


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    capability: str
    required_dimensions: tuple[str, ...]


@dataclass(frozen=True)
class BenchmarkResult:
    benchmark_id: str
    case_id: str
    capability: str
    executor_name: str
    executor_version: str | None
    scores: dict[str, float]
    latency_ms: float | None
    cost_estimate: float | None
    accepted: bool | None


@dataclass(frozen=True)
class RouteEvidence:
    capability: str
    ranked_executors: tuple[str, ...]
    evidence_counts: dict[str, int]
    composite_scores: dict[str, float]


class BenchmarkService:
    """Maintains capability specific evidence. It deliberately has no global winner."""

    def __init__(self, repository: BenchmarkRepository | None = None) -> None:
        self.repository = repository
        self._memory: list[BenchmarkResult] = []

    def record(
        self,
        *,
        case_id: str,
        capability: str,
        executor_name: str,
        scores: dict[str, float],
        executor_version: str | None = None,
        latency_ms: float | None = None,
        cost_estimate: float | None = None,
        accepted: bool | None = None,
    ) -> BenchmarkResult:
        clean_scores = {
            key: max(0.0, min(5.0, float(value)))
            for key, value in scores.items()
        }
        result = BenchmarkResult(
            benchmark_id=f"bench_{uuid4().hex[:16]}",
            case_id=case_id,
            capability=capability,
            executor_name=executor_name,
            executor_version=executor_version,
            scores=clean_scores,
            latency_ms=latency_ms,
            cost_estimate=cost_estimate,
            accepted=accepted,
        )
        self._memory.append(result)
        if self.repository is not None:
            self.repository.add(
                StoredBenchmark(
                    benchmark_id=result.benchmark_id,
                    case_id=result.case_id,
                    capability=result.capability,
                    executor_name=result.executor_name,
                    executor_version=result.executor_version,
                    scores=result.scores,
                    latency_ms=result.latency_ms,
                    cost_estimate=result.cost_estimate,
                    accepted=result.accepted,
                )
            )
        return result

    def evidence_for(self, capability: str) -> list[BenchmarkResult]:
        if self.repository is not None:
            return [
                BenchmarkResult(
                    benchmark_id=item.benchmark_id,
                    case_id=item.case_id,
                    capability=item.capability,
                    executor_name=item.executor_name,
                    executor_version=item.executor_version,
                    scores=dict(item.scores),
                    latency_ms=item.latency_ms,
                    cost_estimate=item.cost_estimate,
                    accepted=item.accepted,
                )
                for item in self.repository.for_capability(capability)
            ]
        return [item for item in self._memory if item.capability == capability]

    def requires_rebenchmark(
        self,
        *,
        capability: str,
        executor_name: str,
        executor_version: str | None,
        minimum_evidence: int = 2,
    ) -> bool:
        """True when current model or executor version lacks enough evidence."""
        rows = [
            item
            for item in self.evidence_for(capability)
            if item.executor_name == executor_name
            and item.executor_version == executor_version
        ]
        return len(rows) < minimum_evidence

    def route_evidence(
        self,
        capability: str,
        *,
        minimum_evidence: int = 2,
        current_versions: dict[str, str | None] | None = None,
    ) -> RouteEvidence:
        items = self.evidence_for(capability)
        if current_versions is not None:
            items = [
                item
                for item in items
                if item.executor_name in current_versions
                and item.executor_version == current_versions[item.executor_name]
            ]

        by_executor: dict[str, list[BenchmarkResult]] = {}
        for item in items:
            by_executor.setdefault(item.executor_name, []).append(item)

        counts: dict[str, int] = {}
        composite: dict[str, float] = {}

        for executor, rows in by_executor.items():
            counts[executor] = len(rows)
            if len(rows) < minimum_evidence:
                continue

            quality_values: list[float] = []
            acceptance_values: list[float] = []
            for row in rows:
                if row.scores:
                    quality_values.append(mean(row.scores.values()) / 5.0)
                if row.accepted is not None:
                    acceptance_values.append(1.0 if row.accepted else 0.0)

            quality = mean(quality_values) if quality_values else 0.0
            acceptance = mean(acceptance_values) if acceptance_values else quality
            # Quality and acceptance dominate. Cost and latency remain observability
            # dimensions and are not allowed to erase poor output quality.
            composite[executor] = round(0.7 * quality + 0.3 * acceptance, 6)

        ranked = tuple(
            name
            for name, _ in sorted(
                composite.items(),
                key=lambda item: (-item[1], item[0]),
            )
        )
        return RouteEvidence(
            capability=capability,
            ranked_executors=ranked,
            evidence_counts=counts,
            composite_scores=composite,
        )
