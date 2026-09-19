from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any

from fashionos_intelligence.services.executors import (
    ExecutionRequest,
    ExecutionResult,
    ExecutorAdapter,
)


@dataclass(frozen=True)
class VerificationResult:
    primary: ExecutionResult
    verifier: ExecutionResult
    accepted: bool
    reasons: tuple[str, ...]


class VerifierWorkflow:
    """Runs production and verification as separate roles/capabilities."""

    def run(
        self,
        *,
        primary_adapter: ExecutorAdapter,
        primary_request: ExecutionRequest,
        verifier_adapter: ExecutorAdapter,
        verifier_request_builder: Callable[[ExecutionResult], ExecutionRequest],
        decision_reader: Callable[[ExecutionResult], tuple[bool, list[str]]],
    ) -> VerificationResult:
        if not primary_adapter.supports(primary_request.capability):
            raise ValueError("PRIMARY_CAPABILITY_UNSUPPORTED")

        primary = primary_adapter.execute(primary_request)
        verifier_request = verifier_request_builder(primary)
        if not verifier_adapter.supports(verifier_request.capability):
            raise ValueError("VERIFIER_CAPABILITY_UNSUPPORTED")

        verifier = verifier_adapter.execute(verifier_request)
        accepted, reasons = decision_reader(verifier)
        return VerificationResult(
            primary=primary,
            verifier=verifier,
            accepted=accepted,
            reasons=tuple(reasons),
        )
