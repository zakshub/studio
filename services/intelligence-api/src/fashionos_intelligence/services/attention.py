from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AttentionItem:
    item_id: str
    score: float
    reasons: tuple[str, ...]


class AttentionService:
    """Prioritize what the organism should inspect first."""

    def rank(self, items: list[dict[str, object]]) -> list[AttentionItem]:
        ranked: list[AttentionItem] = []

        for item in items:
            item_id = str(item.get("item_id") or item.get("id") or "unknown")
            relevance = float(item.get("relevance", 0.0))
            risk = float(item.get("risk", 0.0))
            uncertainty = float(item.get("uncertainty", 0.0))
            novelty = float(item.get("novelty", 0.0))
            user_priority = float(item.get("user_priority", 0.0))
            cost = float(item.get("cost", 0.0))

            score = (
                relevance * 0.32
                + risk * 0.22
                + uncertainty * 0.16
                + novelty * 0.12
                + user_priority * 0.18
                - cost * 0.08
            )

            reasons: list[str] = []
            if relevance >= 0.7:
                reasons.append("HIGH_RELEVANCE")
            if risk >= 0.7:
                reasons.append("HIGH_RISK")
            if uncertainty >= 0.7:
                reasons.append("HIGH_UNCERTAINTY")
            if novelty >= 0.7:
                reasons.append("HIGH_NOVELTY")
            if user_priority >= 0.7:
                reasons.append("USER_PRIORITY")

            ranked.append(
                AttentionItem(
                    item_id=item_id,
                    score=round(score, 4),
                    reasons=tuple(reasons),
                )
            )

        return sorted(ranked, key=lambda entry: (-entry.score, entry.item_id))
