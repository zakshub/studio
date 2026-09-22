from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Iterable

from PIL import Image, UnidentifiedImageError


@dataclass(frozen=True)
class ImageInspection:
    width: int
    height: int
    megapixels: float
    aspect_ratio: float
    format: str | None
    quality_score: float
    flags: tuple[str, ...]


class ImageQualityInspector:
    """Deterministic source-screening bootstrap based on measurable image properties."""

    def inspect(self, payload: bytes) -> ImageInspection:
        try:
            with Image.open(BytesIO(payload)) as image:
                width, height = image.size
                image_format = image.format
        except (UnidentifiedImageError, OSError) as exc:
            raise ValueError("INVALID_IMAGE_BINARY") from exc

        if width <= 0 or height <= 0:
            raise ValueError("INVALID_IMAGE_DIMENSIONS")

        megapixels = (width * height) / 1_000_000.0
        aspect_ratio = max(width / height, height / width)
        flags: list[str] = []
        score = 5.0

        if min(width, height) < 256:
            flags.append("VERY_SMALL_DIMENSION")
            score -= 3.0
        elif min(width, height) < 512:
            flags.append("SMALL_DIMENSION")
            score -= 1.5

        if megapixels < 0.25:
            flags.append("VERY_LOW_RESOLUTION")
            score -= 2.0
        elif megapixels < 1.0:
            flags.append("LOW_RESOLUTION")
            score -= 1.0

        if aspect_ratio > 5.0:
            flags.append("EXTREME_ASPECT_RATIO")
            score -= 1.0

        if megapixels > 100:
            flags.append("EXTREME_PIXEL_COUNT")
            score -= 0.5

        return ImageInspection(
            width=width,
            height=height,
            megapixels=round(megapixels, 3),
            aspect_ratio=round(aspect_ratio, 3),
            format=image_format,
            quality_score=max(0.0, min(5.0, round(score, 2))),
            flags=tuple(flags),
        )


@dataclass(frozen=True)
class PrimaryAssetCandidate:
    asset_id: str
    role: str
    rights_status: str
    media_type: str
    quality_score: float
    pixel_area: int


class PrimaryAssetSelector:
    """Selects a production primary only from authorized primary image candidates."""

    def select(self, candidates: Iterable[PrimaryAssetCandidate]) -> str | None:
        eligible = [
            item
            for item in candidates
            if item.role == "primary"
            and item.rights_status == "authorized"
            and item.media_type == "image"
        ]
        if not eligible:
            return None
        eligible.sort(
            key=lambda item: (
                -item.quality_score,
                -item.pixel_area,
                item.asset_id,
            )
        )
        return eligible[0].asset_id
