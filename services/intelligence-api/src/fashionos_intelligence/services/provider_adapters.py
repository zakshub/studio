from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from fashionos_intelligence.services.executors import ExecutionRequest, ExecutionResult


class ProviderTransport(Protocol):
    def invoke(
        self,
        *,
        operation: str,
        payload: dict[str, Any],
        source_asset_ids: tuple[str, ...],
    ) -> dict[str, Any]: ...


@dataclass
class ProviderExecutorAdapter:
    """Generic internal adapter. Concrete provider SDK/HTTP transports are injected."""

    name: str
    capabilities: set[str]
    transport: ProviderTransport

    def supports(self, capability: str) -> bool:
        return capability in self.capabilities

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        if not self.supports(request.capability):
            raise ValueError("OPERATION_UNSUPPORTED")
        response = self.transport.invoke(
            operation=request.operation,
            payload=request.payload,
            source_asset_ids=request.source_asset_ids,
        )
        return ExecutionResult(
            executor_class=self.name,
            status=str(response.get("status", "succeeded")),
            output=dict(response.get("output", {})),
            diagnostics=dict(response.get("diagnostics", {})),
        )


class OpenAIExecutorAdapter(ProviderExecutorAdapter):
    """OpenAI transport wrapper. Network/SDK implementation is injected at deployment."""


class GeminiExecutorAdapter(ProviderExecutorAdapter):
    """Gemini transport wrapper. Network/SDK implementation is injected at deployment."""
