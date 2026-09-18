from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class CreativeDirection:
    direction_id: str
    principles: tuple[str, ...]
    tension: str | None
    councils: tuple[str, ...]


class CreativeSynthesisService:
    TENSIONS = (
        "refined/raw",
        "traditional/contemporary",
        "stillness/motion",
        "soft/hard",
        "intimate/monumental",
        "ornate/restrained",
        "familiar/unexpected",
    )

    def diverge(
        self,
        *,
        principles: list[str],
        councils: list[str],
        max_directions: int = 4,
    ) -> list[CreativeDirection]:
        unique = [p for i, p in enumerate(principles) if p not in principles[:i]]
        if not unique:
            return []

        pairs = list(combinations(unique, 2)) or [(unique[0],)]
        directions: list[CreativeDirection] = []

        for index, combo in enumerate(pairs[: max(1, max_directions)]):
            directions.append(
                CreativeDirection(
                    direction_id=f"direction_{index + 1}",
                    principles=tuple(combo),
                    tension=self.TENSIONS[index % len(self.TENSIONS)],
                    councils=tuple(sorted(set(councils))),
                )
            )

        return directions
