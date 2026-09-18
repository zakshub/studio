from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict


@dataclass(frozen=True)
class StructuredRule:
    rule_id: str
    subject: str
    effect: str
    authority: int
    specificity: int
    source: str


@dataclass(frozen=True)
class ConflictResolution:
    subject: str
    selected_rule_id: str | None
    unresolved_rule_ids: tuple[str, ...]
    reason: str


class ConflictResolver:
    """Resolve explicit structured rule conflicts without guessing from prose."""

    VALID_EFFECTS = {"allow", "forbid", "require", "prefer", "avoid"}

    def resolve(self, rules: list[StructuredRule]) -> list[ConflictResolution]:
        by_subject: dict[str, list[StructuredRule]] = defaultdict(list)
        for rule in rules:
            if rule.effect not in self.VALID_EFFECTS:
                raise ValueError(f"INVALID_RULE_EFFECT:{rule.effect}")
            by_subject[rule.subject].append(rule)

        resolutions: list[ConflictResolution] = []
        for subject, group in sorted(by_subject.items()):
            effects = {rule.effect for rule in group}
            if len(effects) == 1:
                winner = max(group, key=lambda r: (r.authority, r.specificity, r.rule_id))
                resolutions.append(
                    ConflictResolution(
                        subject=subject,
                        selected_rule_id=winner.rule_id,
                        unresolved_rule_ids=(),
                        reason="NO_EFFECT_CONFLICT",
                    )
                )
                continue

            ranked = sorted(
                group,
                key=lambda r: (-r.authority, -r.specificity, r.rule_id),
            )
            first = ranked[0]
            tied = [
                rule
                for rule in ranked
                if rule.authority == first.authority
                and rule.specificity == first.specificity
            ]
            tied_effects = {rule.effect for rule in tied}

            if len(tied_effects) > 1:
                resolutions.append(
                    ConflictResolution(
                        subject=subject,
                        selected_rule_id=None,
                        unresolved_rule_ids=tuple(rule.rule_id for rule in tied),
                        reason="UNRESOLVED_EQUAL_AUTHORITY_CONFLICT",
                    )
                )
            else:
                resolutions.append(
                    ConflictResolution(
                        subject=subject,
                        selected_rule_id=first.rule_id,
                        unresolved_rule_ids=(),
                        reason="HIGHER_AUTHORITY_OR_SPECIFICITY",
                    )
                )

        return resolutions
