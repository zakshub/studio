from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValueDecision:
    allowed: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]


class ValueSystem:
    """High-authority constraints applied before creative optimization."""

    def evaluate(
        self,
        *,
        rights_statuses: list[str] | None = None,
        preservation_required: bool = False,
        hard_locks: list[str] | None = None,
        requested_changes: list[str] | None = None,
        unresolved_critical_uncertainty: bool = False,
    ) -> ValueDecision:
        rights_statuses = rights_statuses or []
        hard_locks = hard_locks or []
        requested_changes = requested_changes or []

        blockers: list[str] = []
        warnings: list[str] = []

        if any(status == "reference_only" for status in rights_statuses):
            if any(change in {"publish", "production_reuse", "source_mutation"} for change in requested_changes):
                blockers.append("REFERENCE_ONLY_SOURCE_CANNOT_BE_USED_AS_PRODUCTION_ASSET")

        if any(status == "unknown" for status in rights_statuses):
            warnings.append("SOURCE_RIGHTS_UNKNOWN")

        if preservation_required and not hard_locks:
            warnings.append("PRESERVATION_REQUIRED_WITHOUT_EXPLICIT_LOCKS")

        lock_set = {item.lower() for item in hard_locks}
        for change in requested_changes:
            normalized = change.lower()
            if normalized in lock_set:
                blockers.append(f"HARD_LOCK_CONFLICT:{normalized}")

        if unresolved_critical_uncertainty:
            blockers.append("CRITICAL_UNCERTAINTY_UNRESOLVED")

        return ValueDecision(
            allowed=not blockers,
            blockers=tuple(blockers),
            warnings=tuple(warnings),
        )
