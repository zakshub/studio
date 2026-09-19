from fashionos_intelligence.persistence.benchmarks import BenchmarkRepository
from fashionos_intelligence.persistence.db import build_session_factory
from fashionos_intelligence.services.benchmarks import BenchmarkService
from fashionos_intelligence.services.executors import (
    CallableExecutorAdapter,
    ExecutionRequest,
    ExecutionResult,
    ExecutorGateway,
)
from fashionos_intelligence.services.routing import EvidenceRouter


def _runner(name: str, score: float):
    def run(request: ExecutionRequest) -> ExecutionResult:
        return ExecutionResult(
            executor_class=name,
            status="succeeded",
            output={"name": name, "task": request.task_id},
            diagnostics={"score": score},
        )
    return run


def test_benchmark_routing_is_capability_specific():
    sessions = build_session_factory("sqlite+pysqlite:///:memory:")
    service = BenchmarkService(BenchmarkRepository(sessions))

    for idx, value in enumerate((5.0, 4.5), start=1):
        service.record(
            case_id=f"case_a_{idx}",
            capability="image_editing",
            executor_name="alpha",
            scores={"preservation": value, "quality": value},
            accepted=True,
        )
    for idx, value in enumerate((3.0, 3.5), start=1):
        service.record(
            case_id=f"case_b_{idx}",
            capability="image_editing",
            executor_name="beta",
            scores={"preservation": value, "quality": value},
            accepted=True,
        )

    decision = EvidenceRouter(service).decide(
        capability="image_editing",
        available_executors=["alpha", "beta"],
    )
    assert decision.ordered_executors[0] == "alpha"
    assert decision.reason_code == "CAPABILITY_BENCHMARK_EVIDENCE"


def test_cold_start_does_not_invent_global_winner():
    service = BenchmarkService()
    decision = EvidenceRouter(service).decide(
        capability="research",
        available_executors=["zeta", "alpha"],
    )
    assert decision.reason_code == "COLD_START_NO_SUFFICIENT_EVIDENCE"
    assert decision.ordered_executors == ("alpha", "zeta")


def test_competitive_execution_uses_routing_decision():
    service = BenchmarkService()
    for idx in range(2):
        service.record(
            case_id=f"a_{idx}",
            capability="image_generation",
            executor_name="alpha",
            scores={"quality": 4.8},
            accepted=True,
        )
        service.record(
            case_id=f"b_{idx}",
            capability="image_generation",
            executor_name="beta",
            scores={"quality": 4.4},
            accepted=True,
        )

    router = EvidenceRouter(service)
    decision = router.decide(
        capability="image_generation",
        available_executors=["alpha", "beta"],
        high_value=True,
    )
    gateway = ExecutorGateway(
        [
            CallableExecutorAdapter(
                name="alpha",
                capabilities={"image_generation"},
                runner=_runner("alpha", 4.8),
            ),
            CallableExecutorAdapter(
                name="beta",
                capabilities={"image_generation"},
                runner=_runner("beta", 4.4),
            ),
        ]
    )
    result = gateway.run_decision(
        ExecutionRequest(
            task_id="task_1",
            capability="image_generation",
            operation="generate",
            payload={},
        ),
        decision,
    )
    assert isinstance(result, list)
    assert {item.executor_class for item in result} == {"alpha", "beta"}
