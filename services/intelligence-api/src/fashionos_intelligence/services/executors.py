from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Any, Callable

from fashionos_intelligence.services.routing import RoutingDecision


@dataclass(frozen=True)
class ExecutionRequest:
    task_id: str
    capability: str
    operation: str
    payload: dict[str, Any]
    source_asset_ids: tuple[str, ...] = ()
    budget_ms: int | None = None


@dataclass(frozen=True)
class ExecutionResult:
    executor_class: str
    status: str
    output: dict[str, Any]
    diagnostics: dict[str, Any]


class ExecutorAdapter(Protocol):
    name: str
    capabilities: set[str]

    def supports(self, capability: str) -> bool: ...
    def execute(self, request: ExecutionRequest) -> ExecutionResult: ...


class DeterministicExecutor:
    name = "deterministic"
    capabilities = {"resize", "crop", "metadata", "fingerprint", "noop"}

    def supports(self, capability: str) -> bool:
        return capability in self.capabilities

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        if not self.supports(request.capability):
            raise ValueError("OPERATION_UNSUPPORTED")
        return ExecutionResult(
            executor_class=self.name,
            status="succeeded",
            output={"operation": request.operation, "payload": request.payload},
            diagnostics={"deterministic": True},
        )


class CallableExecutorAdapter:
    """Provider-neutral adapter for injected transports/SDK clients."""

    def __init__(
        self,
        *,
        name: str,
        capabilities: set[str],
        runner: Callable[[ExecutionRequest], ExecutionResult],
    ) -> None:
        self.name = name
        self.capabilities = set(capabilities)
        self.runner = runner

    def supports(self, capability: str) -> bool:
        return capability in self.capabilities

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        if not self.supports(request.capability):
            raise ValueError("OPERATION_UNSUPPORTED")
        return self.runner(request)


class ExecutorGateway:
    def __init__(self, adapters: list[ExecutorAdapter] | None = None):
        self.adapters: list[ExecutorAdapter] = adapters or [DeterministicExecutor()]

    def register(self, adapter: ExecutorAdapter) -> None:
        self.adapters.append(adapter)

    def available(self, capability: str) -> list[str]:
        return [a.name for a in self.adapters if a.supports(capability)]

    def versions(self, capability: str) -> dict[str, str | None]:
        versions: dict[str, str | None] = {}
        for adapter in self.adapters:
            if not adapter.supports(capability):
                continue
            resolver = getattr(adapter, "version_for", None)
            versions[adapter.name] = resolver(capability) if callable(resolver) else None
        return versions

    def _adapter(self, name: str, capability: str) -> ExecutorAdapter | None:
        return next(
            (
                adapter
                for adapter in self.adapters
                if adapter.name == name and adapter.supports(capability)
            ),
            None,
        )

    def run(
        self,
        request: ExecutionRequest,
        preferred: str | None = None,
    ) -> ExecutionResult:
        eligible = [a for a in self.adapters if a.supports(request.capability)]
        if preferred:
            eligible.sort(key=lambda a: 0 if a.name == preferred else 1)
        if not eligible:
            raise RuntimeError("EXECUTOR_UNAVAILABLE")

        last_error: Exception | None = None
        for adapter in eligible:
            try:
                return adapter.execute(request)
            except Exception as exc:
                last_error = exc
        raise RuntimeError("EXECUTOR_FAILED") from last_error

    def run_ordered(
        self,
        request: ExecutionRequest,
        ordered_names: tuple[str, ...],
    ) -> ExecutionResult:
        last_error: Exception | None = None
        for name in ordered_names:
            adapter = self._adapter(name, request.capability)
            if adapter is None:
                continue
            try:
                return adapter.execute(request)
            except Exception as exc:
                last_error = exc
        if last_error is not None:
            raise RuntimeError("EXECUTOR_FAILED") from last_error
        raise RuntimeError("EXECUTOR_UNAVAILABLE")

    def run_competitive(
        self,
        request: ExecutionRequest,
        ordered_names: tuple[str, ...],
    ) -> list[ExecutionResult]:
        results: list[ExecutionResult] = []
        errors = 0
        for name in ordered_names:
            adapter = self._adapter(name, request.capability)
            if adapter is None:
                continue
            try:
                results.append(adapter.execute(request))
            except Exception:
                errors += 1
        if not results:
            raise RuntimeError("EXECUTOR_FAILED" if errors else "EXECUTOR_UNAVAILABLE")
        return results

    def run_decision(
        self,
        request: ExecutionRequest,
        decision: RoutingDecision,
    ) -> ExecutionResult | list[ExecutionResult]:
        if decision.capability != request.capability:
            raise ValueError("ROUTING_CAPABILITY_MISMATCH")
        if decision.strategy == "competitive":
            return self.run_competitive(request, decision.ordered_executors)
        # Verifier orchestration is handled as a two-stage workflow because
        # verification normally uses a different capability/contract.
        return self.run_ordered(request, decision.ordered_executors)
