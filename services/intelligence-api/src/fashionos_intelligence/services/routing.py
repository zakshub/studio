from __future__ import annotations

from dataclasses import dataclass

from fashionos_intelligence.services.benchmarks import BenchmarkService


@dataclass(frozen=True)
class RoutingDecision:
    capability: str
    strategy: str
    ordered_executors: tuple[str, ...]
    reason_code: str
    evidence_counts: dict[str, int]


class EvidenceRouter:
    def __init__(self, benchmarks: BenchmarkService):
        self.benchmarks = benchmarks

    def decide(
        self,
        *,
        capability: str,
        available_executors: list[str],
        high_value: bool = False,
        verifier_available: bool = False,
        current_versions: dict[str, str | None] | None = None,
    ) -> RoutingDecision:
        evidence = self.benchmarks.route_evidence(
            capability,
            current_versions=current_versions,
        )
        available = set(available_executors)
        ranked = tuple(name for name in evidence.ranked_executors if name in available)

        if not ranked:
            ordered = tuple(sorted(available))
            return RoutingDecision(
                capability=capability,
                strategy="single" if len(ordered) <= 1 else "competitive",
                ordered_executors=ordered,
                reason_code="COLD_START_NO_SUFFICIENT_EVIDENCE",
                evidence_counts=evidence.evidence_counts,
            )

        if high_value and len(ranked) >= 2:
            strategy = "competitive"
            ordered = ranked[:2]
            reason = "HIGH_VALUE_COMPETITIVE_EVIDENCE"
        elif verifier_available and len(ranked) >= 2:
            strategy = "verifier"
            ordered = ranked[:2]
            reason = "PRIMARY_PLUS_INDEPENDENT_VERIFIER"
        else:
            strategy = "single"
            ordered = ranked
            reason = "CAPABILITY_BENCHMARK_EVIDENCE"

        return RoutingDecision(
            capability=capability,
            strategy=strategy,
            ordered_executors=ordered,
            reason_code=reason,
            evidence_counts=evidence.evidence_counts,
        )
