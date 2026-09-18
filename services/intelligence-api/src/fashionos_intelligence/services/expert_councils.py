from __future__ import annotations


CAPABILITY_TO_COUNCILS: dict[str, set[str]] = {
    "photography": {"photography", "fashion_photography"},
    "composition": {"photography", "graphic_digital_design", "art_direction"},
    "fashion": {"fashion_garment", "fashion_photography"},
    "garment": {"fashion_garment", "fashion_photography"},
    "embroidery": {"fashion_garment"},
    "material": {"fashion_garment", "lighting"},
    "camera": {"camera_lens", "cinematography"},
    "lens": {"camera_lens", "cinematography"},
    "lighting": {"lighting", "cinematography", "photography"},
    "color": {"color_finishing", "art_direction"},
    "lut": {"color_finishing"},
    "editing": {"editing", "storytelling"},
    "video": {"cinematography", "editing", "storytelling", "creative_direction"},
    "storytelling": {"storytelling", "creative_direction", "editing"},
    "graphic": {"graphic_digital_design", "art_direction"},
    "typography": {"graphic_digital_design", "art_direction"},
    "campaign": {"creative_direction", "art_direction", "fashion_garment", "photography"},
    "concept": {"creative_direction", "art_direction", "fine_art_perception"},
    "perception": {"fine_art_perception", "photography"},
    "preservation": {"photography", "fashion_garment"},
    "qc": {"photography", "fashion_garment", "camera_lens", "lighting"},
}


class ExpertCouncilSelector:
    def select(self, capabilities: list[str], mode: str | None = None) -> list[str]:
        councils: set[str] = set()
        for capability in capabilities:
            normalized = capability.lower().strip()
            councils.update(CAPABILITY_TO_COUNCILS.get(normalized, set()))

        mode_upper = (mode or "").upper()
        if "FASHION" in mode_upper:
            councils.update({"fashion_garment", "fashion_photography"})
        if "CINEMATIC" in mode_upper or "VIDEO" in mode_upper:
            councils.update({"cinematography", "editing", "storytelling"})
        if "PRESERVATION" in mode_upper or "EDIT" in mode_upper:
            councils.update({"photography", "fashion_garment"})

        return sorted(councils)
