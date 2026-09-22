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
    """Generic internal adapter. Concrete provider SDK or HTTP transports are injected."""

    name: str
    capabilities: set[str]
    transport: ProviderTransport
    provider: str | None = None

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
        diagnostics = dict(response.get("diagnostics", {}))
        if self.provider:
            diagnostics.setdefault("provider", self.provider)
        return ExecutionResult(
            executor_class=self.name,
            status=str(response.get("status", "succeeded")),
            output=dict(response.get("output", {})),
            diagnostics=diagnostics,
        )


class OpenAIExecutorAdapter(ProviderExecutorAdapter):
    """OpenAI transport wrapper. Network or SDK implementation is injected at deployment."""


class GeminiExecutorAdapter(ProviderExecutorAdapter):
    """Gemini transport wrapper. Network or SDK implementation is injected at deployment."""


@dataclass
class CrossProviderVerifierAdapter:
    """Prefer a verifier from a provider different from the generator, with fallback."""

    verifiers: tuple[ProviderExecutorAdapter, ...]
    name: str = "cross-provider-verifier"

    @property
    def capabilities(self) -> set[str]:
        return {"vision_qc"}

    def supports(self, capability: str) -> bool:
        return capability == "vision_qc" and any(
            verifier.supports(capability) for verifier in self.verifiers
        )

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        if not self.supports(request.capability):
            raise ValueError("OPERATION_UNSUPPORTED")

        generator_provider = str(request.payload.get("generatorProvider") or "").strip()
        eligible = [
            verifier
            for verifier in self.verifiers
            if verifier.supports(request.capability)
        ]
        if generator_provider:
            eligible.sort(
                key=lambda verifier: 1 if verifier.provider == generator_provider else 0
            )

        last_error: Exception | None = None
        for verifier in eligible:
            try:
                result = verifier.execute(request)
                diagnostics = dict(result.diagnostics)
                diagnostics["crossProviderPreferred"] = bool(generator_provider)
                diagnostics["generatorProvider"] = generator_provider or None
                diagnostics["sameProviderFallback"] = bool(
                    generator_provider and verifier.provider == generator_provider
                )
                return ExecutionResult(
                    executor_class=result.executor_class,
                    status=result.status,
                    output=result.output,
                    diagnostics=diagnostics,
                )
            except Exception as exc:
                last_error = exc

        raise RuntimeError("VERIFIER_FAILED") from last_error
