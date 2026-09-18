from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class NoveltyResult:
    score: float
    nearest_similarity: float
    label: str


class NoveltyService:
    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {
            token
            for token in re.findall(r"[a-z0-9_-]+", text.lower())
            if len(token) > 2
        }

    @classmethod
    def _jaccard(cls, left: str, right: str) -> float:
        a = cls._tokens(left)
        b = cls._tokens(right)
        if not a and not b:
            return 1.0
        if not a or not b:
            return 0.0
        return len(a & b) / len(a | b)

    def evaluate(self, candidate: str, references: list[str]) -> NoveltyResult:
        nearest = max((self._jaccard(candidate, ref) for ref in references), default=0.0)
        score = round(1.0 - nearest, 4)
        if score >= 0.7:
            label = "high"
        elif score >= 0.4:
            label = "medium"
        else:
            label = "low"
        return NoveltyResult(score=score, nearest_similarity=round(nearest, 4), label=label)
