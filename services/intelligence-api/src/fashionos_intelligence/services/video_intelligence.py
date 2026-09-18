from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VideoSegment:
    start_ms: int
    end_ms: int
    shot_type: str | None = None
    camera_motion: str | None = None
    subject_motion: str | None = None
    garment_motion: str | None = None
    lighting_change: str | None = None
    color_state: str | None = None
    narrative_function: str | None = None


@dataclass(frozen=True)
class VideoAnalysis:
    duration_ms: int
    segments: tuple[VideoSegment, ...]
    average_shot_ms: float | None
    continuity_notes: tuple[str, ...]


class VideoIntelligence:
    def analyze_structured(
        self,
        *,
        duration_ms: int,
        segments: list[VideoSegment],
        continuity_notes: list[str] | None = None,
    ) -> VideoAnalysis:
        if duration_ms <= 0:
            raise ValueError("INVALID_VIDEO_DURATION")
        valid = [s for s in segments if 0 <= s.start_ms < s.end_ms <= duration_ms]
        shot_lengths = [s.end_ms - s.start_ms for s in valid]
        avg = sum(shot_lengths) / len(shot_lengths) if shot_lengths else None
        return VideoAnalysis(
            duration_ms=duration_ms,
            segments=tuple(valid),
            average_shot_ms=avg,
            continuity_notes=tuple(continuity_notes or []),
        )
