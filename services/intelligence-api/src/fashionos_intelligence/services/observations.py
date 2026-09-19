from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from fashionos_intelligence.persistence.cognition_records import (
    ObservationRepository,
    StoredObservation,
)


@dataclass(frozen=True)
class Observation:
    observation_id: str
    source_id: str
    media_type: str
    dimension: str
    value: str
    confidence: str
    evidence_ref: str | None
    interpretation: bool


class ObservationService:
    VALID_MEDIA = {"image", "video", "text", "web"}
    VALID_CONFIDENCE = {"low", "medium", "high"}

    def __init__(self, repository: ObservationRepository | None = None) -> None:
        self.repository = repository

    def normalize(
        self,
        *,
        source_id: str,
        media_type: str,
        raw: list[dict[str, object]],
    ) -> list[Observation]:
        if media_type not in self.VALID_MEDIA:
            raise ValueError("UNSUPPORTED_MEDIA_TYPE")
        out: list[Observation] = []
        for item in raw:
            dimension = str(item.get("dimension", "")).strip()
            value = str(item.get("value", "")).strip()
            if not dimension or not value:
                continue
            confidence = str(item.get("confidence", "low"))
            if confidence not in self.VALID_CONFIDENCE:
                confidence = "low"
            observation = Observation(
                observation_id=f"obs_{uuid4().hex[:16]}",
                source_id=source_id,
                media_type=media_type,
                dimension=dimension,
                value=value,
                confidence=confidence,
                evidence_ref=(
                    str(item["evidence_ref"])
                    if item.get("evidence_ref") is not None
                    else None
                ),
                interpretation=bool(item.get("interpretation", False)),
            )
            out.append(observation)
            if self.repository is not None:
                self.repository.upsert(
                    StoredObservation(
                        observation_id=observation.observation_id,
                        source_id=observation.source_id,
                        media_type=observation.media_type,
                        dimension=observation.dimension,
                        value=observation.value,
                        confidence=observation.confidence,
                        evidence_ref=observation.evidence_ref,
                        interpretation=observation.interpretation,
                    )
                )
        return out
