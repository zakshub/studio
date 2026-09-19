from __future__ import annotations

from dataclasses import dataclass

from fashionos_intelligence.services.conflicts import (
    ConflictResolver,
    ConflictResolution,
    StructuredRule,
)


@dataclass(frozen=True)
class RuleContext:
    mode: str
    preservation_required: bool
    rights_statuses: tuple[str, ...]
    hard_locks: tuple[str, ...]
    allowed_changes: tuple[str, ...]


class StructuredRuleRegistry:
    """Small canonical machine-readable policy layer used before prose knowledge."""

    def rules_for(self, context: RuleContext) -> list[StructuredRule]:
        rules: list[StructuredRule] = [
            StructuredRule(
                rule_id="CORE_TRUTH_UNKNOWN_REMAINS_UNKNOWN",
                subject="truth_status",
                effect="require",
                authority=100,
                specificity=100,
                source="operating_constitution",
            ),
            StructuredRule(
                rule_id="CORE_NO_CLIENT_CONTAMINATION",
                subject="universal_learning",
                effect="forbid",
                authority=100,
                specificity=100,
                source="operating_constitution",
            ),
        ]

        if context.preservation_required or "PRESERVATION" in context.mode or "EDIT" in context.mode:
            rules.extend(
                [
                    StructuredRule(
                        rule_id="PRESERVE_LOCKED_ELEMENTS",
                        subject="locked_element_change",
                        effect="forbid",
                        authority=100,
                        specificity=100,
                        source="source_preservation",
                    ),
                    StructuredRule(
                        rule_id="QC_PRESERVATION_REQUIRED",
                        subject="preservation_qc",
                        effect="require",
                        authority=100,
                        specificity=100,
                        source="forensic_qc",
                    ),
                ]
            )

        if any(status in {"unknown", "reference_only"} for status in context.rights_statuses):
            rules.append(
                StructuredRule(
                    rule_id="RIGHTS_BLOCK_UNAUTHORIZED_PRODUCTION",
                    subject="production_publication",
                    effect="forbid",
                    authority=100,
                    specificity=100,
                    source="source_authority",
                )
            )

        if context.hard_locks and any(
            change in set(context.hard_locks) for change in context.allowed_changes
        ):
            rules.append(
                StructuredRule(
                    rule_id="REQUESTED_CHANGE_CONFLICTS_WITH_HARD_LOCK",
                    subject="hard_lock_conflict",
                    effect="forbid",
                    authority=100,
                    specificity=100,
                    source="runtime_contract",
                )
            )

        return rules

    def evaluate(self, context: RuleContext) -> list[ConflictResolution]:
        return ConflictResolver().resolve(self.rules_for(context))
