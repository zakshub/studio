from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourcePolicyDecision:
    may_fetch: bool
    may_analyze: bool
    may_store_binary: bool
    may_publish: bool
    reasons: tuple[str, ...]


class SourcePolicy:
    """Translate source role/rights into explicit ingestion permissions."""

    def decide(
        self,
        *,
        role: str,
        rights_status: str,
    ) -> SourcePolicyDecision:
        role = role.lower().strip()
        rights_status = rights_status.lower().strip()
        reasons: list[str] = []

        if rights_status == "authorized":
            return SourcePolicyDecision(
                may_fetch=True,
                may_analyze=True,
                may_store_binary=True,
                may_publish=role in {"primary", "internal_approved"},
                reasons=(),
            )

        if rights_status == "reference_only":
            reasons.append("REFERENCE_ONLY")
            return SourcePolicyDecision(
                may_fetch=True,
                may_analyze=True,
                may_store_binary=False,
                may_publish=False,
                reasons=tuple(reasons),
            )

        reasons.append("RIGHTS_UNKNOWN")
        return SourcePolicyDecision(
            may_fetch=False,
            may_analyze=False,
            may_store_binary=False,
            may_publish=False,
            reasons=tuple(reasons),
        )
