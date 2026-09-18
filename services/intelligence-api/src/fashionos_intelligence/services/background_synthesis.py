from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict
import re


@dataclass(frozen=True)
class SynthesisCandidate:
    cluster_key: str
    evidence_count: int
    observations: tuple[str, ...]
    proposed_action: str


class BackgroundSynthesisService:
    @staticmethod
    def _cluster_key(text: str) -> str:
        tokens = [
            token
            for token in re.findall(r"[a-z0-9_-]+", text.lower())
            if len(token) > 4
        ]
        return "|".join(sorted(set(tokens))[:4]) or "misc"

    def synthesize(
        self,
        observations: list[str],
        *,
        minimum_repeat: int = 2,
    ) -> list[SynthesisCandidate]:
        groups: dict[str, list[str]] = defaultdict(list)
        for observation in observations:
            groups[self._cluster_key(observation)].append(observation)

        candidates: list[SynthesisCandidate] = []
        for key, group in groups.items():
            if len(group) < minimum_repeat:
                continue
            candidates.append(
                SynthesisCandidate(
                    cluster_key=key,
                    evidence_count=len(group),
                    observations=tuple(group),
                    proposed_action="CREATE_LEARNING_CANDIDATE",
                )
            )

        return sorted(
            candidates,
            key=lambda candidate: (-candidate.evidence_count, candidate.cluster_key),
        )
