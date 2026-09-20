from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class ExpertPrinciple:
    title: str
    principle: str
    evidence: tuple[str, ...]
    principle_type: str


@dataclass(frozen=True)
class ExpertProfile:
    expert_id: str
    name: str
    status: str
    councils: tuple[str, ...]
    principles: tuple[ExpertPrinciple, ...]
    source_path: str


class ExpertProfileLoader:
    def __init__(self, profiles_root: Path):
        self.profiles_root = profiles_root

    @staticmethod
    def _field(text: str, label: str) -> str:
        match = re.search(rf"^{re.escape(label)}:\s*(.+)$", text, re.MULTILINE)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _normalize_council(value: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
        aliases = {
            "fashion_garment": "fashion_garment",
            "fine_art_perception": "fine_art_perception",
            "graphic_digital_design": "graphic_digital_design",
            "camera_lens": "camera_lens",
            "color_lut_finishing": "color_finishing",
            "color_finishing": "color_finishing",
        }
        return aliases.get(normalized, normalized)

    @staticmethod
    def _principle_section(text: str) -> str:
        """Return the first major section explicitly devoted to principles.

        Expert files may label the evidence section differently
        (for example "Documented decision principles", "Evidence-backed
        principles", or a deliberately conservative partnership-level
        principles section). The loader should preserve that editorial
        distinction instead of requiring one exact heading.
        """
        matches = list(
            re.finditer(
                r"^##\s+(.+?)\s*$",
                text,
                re.MULTILINE,
            )
        )
        for index, match in enumerate(matches):
            heading = match.group(1).strip().lower()
            if "principle" not in heading:
                continue
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            body = text[start:end]
            if re.search(r"^###\s+", body, re.MULTILINE):
                return body
        return ""

    @staticmethod
    def _principles(text: str) -> tuple[ExpertPrinciple, ...]:
        body = ExpertProfileLoader._principle_section(text)
        if not body:
            return ()

        chunks = re.split(r"\n###\s+", body)
        output: list[ExpertPrinciple] = []
        for chunk in chunks[1:]:
            lines = chunk.strip().splitlines()
            if not lines:
                continue
            title = lines[0].strip()
            raw = "\n".join(lines[1:])
            ptype = ExpertProfileLoader._field(raw, "Type")
            evidence_raw = ExpertProfileLoader._field(raw, "Evidence")
            evidence = tuple(
                item.strip()
                for item in evidence_raw.split(",")
                if item.strip()
            )
            match = re.search(
                r"^Principle:\s*\n(.+?)(?=\n\n|\Z)",
                raw,
                re.MULTILINE | re.DOTALL,
            )
            principle = " ".join(match.group(1).split()) if match else ""
            if principle:
                output.append(
                    ExpertPrinciple(
                        title=title,
                        principle=principle,
                        evidence=evidence,
                        principle_type=ptype,
                    )
                )
        return tuple(output)

    def load_file(self, path: Path) -> ExpertProfile:
        text = path.read_text(encoding="utf-8")
        title = text.splitlines()[0].removeprefix("# Expert Intelligence — ").strip()
        councils = tuple(
            self._normalize_council(item.strip())
            for item in self._field(text, "Primary councils").split(",")
            if item.strip()
        )
        return ExpertProfile(
            expert_id=self._field(text, "Expert ID"),
            name=title,
            status=self._field(text, "Status"),
            councils=councils,
            principles=self._principles(text),
            source_path=path.as_posix(),
        )

    def load_all(self) -> list[ExpertProfile]:
        if not self.profiles_root.exists():
            return []
        return [
            self.load_file(path)
            for path in sorted(self.profiles_root.glob("*.md"))
        ]
