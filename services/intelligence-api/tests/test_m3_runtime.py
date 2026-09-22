from fashionos_intelligence.services.benchmark_runner import BenchmarkRunCase, BenchmarkRunner
from fashionos_intelligence.services.benchmarks import BenchmarkCase, BenchmarkService
from fashionos_intelligence.services.executors import (
    CallableExecutorAdapter,
    ExecutionRequest,
    ExecutionResult,
)
from fashionos_intelligence.services.provider_adapters import ProviderExecutorAdapter
from fashionos_intelligence.services.verifier import VerifierWorkflow


def _exec(name: str, capability: str, accepted: bool = True):
    def runner(request: ExecutionRequest):
        return ExecutionResult(
            executor_class=name,
            status="succeeded",
            output={"accepted": accepted, "assetIds": [f"{name}_asset"]},
            diagnostics={"cost": 0.01, "model": "model-v1"},
        )
    return CallableExecutorAdapter(
        name=name,
        capabilities={capability},
        runner=runner,
    )


def test_benchmark_runner_records_same_case_for_multiple_executors():
    service = BenchmarkService()
    runner = BenchmarkRunner(service)
    case = BenchmarkCase(
        case_id="B-TEST",
        capability="image_generation",
        required_dimensions=("quality",),
    )
    request = ExecutionRequest(
        task_id="task_1",
        capability="image_generation",
        operation="generate",
        payload={},
    )
    results = runner.run_case(
        item=BenchmarkRunCase(case=case, request=request),
        executors=[_exec("alpha", "image_generation"), _exec("beta", "image_generation")],
        scorer=lambda output, _: ({"quality": 4.0}, output.output["accepted"]),
        cost_reader=lambda output: float(output.diagnostics["cost"]),
    )
    assert len(results) == 2
    assert {r.executor_name for r in results} == {"alpha", "beta"}
    assert all(r.latency_ms is not None for r in results)
    assert all(r.cost_estimate == 0.01 for r in results)
    assert all(r.executor_version == "model-v1" for r in results)


def test_verifier_workflow_keeps_generation_and_verification_separate():
    primary = _exec("generator", "image_generation")
    verifier = _exec("reviewer", "vision_qc")

    result = VerifierWorkflow().run(
        primary_adapter=primary,
        primary_request=ExecutionRequest(
            task_id="task_2",
            capability="image_generation",
            operation="generate",
            payload={},
        ),
        verifier_adapter=verifier,
        verifier_request_builder=lambda output: ExecutionRequest(
            task_id="task_2",
            capability="vision_qc",
            operation="verify",
            payload={"candidate": output.output},
        ),
        decision_reader=lambda output: (bool(output.output["accepted"]), ["verified"]),
    )
    assert result.primary.executor_class == "generator"
    assert result.verifier.executor_class == "reviewer"
    assert result.accepted is True


def test_provider_adapter_uses_injected_transport_without_provider_leak_logic():
    class Transport:
        def invoke(self, *, operation, payload, source_asset_ids):
            return {
                "status": "succeeded",
                "output": {"operation": operation, "value": payload["value"]},
                "diagnostics": {"internal": True},
            }

    adapter = ProviderExecutorAdapter(
        name="internal-provider-a",
        capabilities={"reasoning"},
        transport=Transport(),
    )
    result = adapter.execute(
        ExecutionRequest(
            task_id="task_3",
            capability="reasoning",
            operation="analyze",
            payload={"value": 7},
        )
    )
    assert result.status == "succeeded"
    assert result.output["value"] == 7



def test_model_version_change_requires_rebenchmark_and_stale_evidence_is_not_routed():
    service = BenchmarkService()
    for case_id in ("B-A", "B-B"):
        service.record(
            case_id=case_id,
            capability="image_generation",
            executor_name="alpha",
            executor_version="model-v1",
            scores={"quality": 4.5},
            accepted=True,
        )

    assert service.requires_rebenchmark(
        capability="image_generation",
        executor_name="alpha",
        executor_version="model-v1",
    ) is False
    assert service.requires_rebenchmark(
        capability="image_generation",
        executor_name="alpha",
        executor_version="model-v2",
    ) is True

    old_route = service.route_evidence(
        "image_generation",
        current_versions={"alpha": "model-v1"},
    )
    new_route = service.route_evidence(
        "image_generation",
        current_versions={"alpha": "model-v2"},
    )
    assert old_route.ranked_executors == ("alpha",)
    assert new_route.ranked_executors == ()
    assert new_route.evidence_counts == {}
