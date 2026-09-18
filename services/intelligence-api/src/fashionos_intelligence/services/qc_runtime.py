from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QCDimension:
    name: str
    score: float | None
    critical: bool = False
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class QCOutcome:
    status: str
    dimensions: tuple[QCDimension, ...]
    critical_failures: tuple[str, ...]
    requires_rework: bool
    human_review_required: bool


class QCRuntime:
    """Policy engine for QC scores produced by deterministic or vision evaluators."""

    def evaluate(
        self,
        dimensions: list[QCDimension],
        preservation_required: bool = False,
    ) -> QCOutcome:
        failures: list[str] = []
        warnings = False
        for d in dimensions:
            if d.score is None:
                warnings = True
                if d.critical:
                    failures.append(f"{d.name}:UNKNOWN")
                continue
            if d.critical and d.score <= 2:
                failures.append(f"{d.name}:CRITICAL_LOW")
            elif d.score <= 2:
                warnings = True
            elif d.score < 4:
                warnings = True

        if preservation_required:
            p = next((d for d in dimensions if d.name == "preservation"), None)
            if p is None or p.score is None or p.score <= 2:
                failures.append("preservation:FAILED_OR_UNKNOWN")

        status = "fail" if failures else "warn" if warnings else "pass"
        return QCOutcome(
            status=status,
            dimensions=tuple(dimensions),
            critical_failures=tuple(sorted(set(failures))),
            requires_rework=bool(failures),
            human_review_required=bool(failures) or warnings,
        )
