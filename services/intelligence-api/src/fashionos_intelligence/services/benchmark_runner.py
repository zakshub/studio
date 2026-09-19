from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable

from fashionos_intelligence.services.benchmarks import BenchmarkCase, BenchmarkResult, BenchmarkService
from fashionos_intelligence.services.executors import ExecutionRequest, ExecutorAdapter


@dataclass(frozen=True)
class BenchmarkRunCase:
    case: BenchmarkCase
    request: ExecutionRequest


class BenchmarkRunner:
    """Runs the same benchmark case against eligible executors and records evidence."""

    def __init__(self, service: BenchmarkService) -> None:
        self.service = service

    def run_case(
        self,
        *,
        item: BenchmarkRunCase,
        executors: list[ExecutorAdapter],
        scorer: Callable[[object, BenchmarkCase], tuple[dict[str, float], bool | None]],
        cost_reader: Callable[[object], float | None] | None = None,
    ) -> list[BenchmarkResult]:
        results: list[BenchmarkResult] = []
        for executor in executors:
            if not executor.supports(item.case.capability):
                continue
            started = perf_counter()
            output = executor.execute(item.request)
            latency_ms = (perf_counter() - started) * 1000.0
            scores, accepted = scorer(output, item.case)
            cost = cost_reader(output) if cost_reader else None
            results.append(
                self.service.record(
                    case_id=item.case.case_id,
                    capability=item.case.capability,
                    executor_name=executor.name,
                    scores=scores,
                    latency_ms=latency_ms,
                    cost_estimate=cost,
                    accepted=accepted,
                )
            )
        return results
