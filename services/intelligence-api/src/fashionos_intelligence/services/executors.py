from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Any


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


class ExecutorGateway:
    def __init__(self, adapters: list[ExecutorAdapter] | None = None):
        self.adapters: list[ExecutorAdapter] = adapters or [DeterministicExecutor()]

    def register(self, adapter: ExecutorAdapter) -> None:
        self.adapters.append(adapter)

    def available(self, capability: str) -> list[str]:
        return [a.name for a in self.adapters if a.supports(capability)]

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
