from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re

from fashionos_intelligence.domain.models import BrainRetrieveRequest


_ALLOWED_PREFIXES = (
    "architecture/",
    "knowledge/",
    "qc/",
    "workflows/",
    "research/learned-rules/",
    "research/research-policy.md",
)
_EXCLUDED_PREFIXES = (
    "qc/reports/",
    "project-management/",
    "backend/",
    "services/",
    "research/rolling-observations/",
)


@dataclass(frozen=True)
class KnowledgeUnit:
    unit_id: str
    document_id: str
    section: str
    domain: str
    authority: int
    text: str


class BrainIndex:
    def __init__(self, root: Path):
        self.root = root
        self.revision = "uninitialized"
        self.units: list[KnowledgeUnit] = []

    @staticmethod
    def _eligible(relative_path: str) -> bool:
        if relative_path in {"README.md", "SKILL.md"}:
            return True
        if any(relative_path.startswith(p) for p in _EXCLUDED_PREFIXES):
            return False
        return any(relative_path.startswith(p) for p in _ALLOWED_PREFIXES)

    @staticmethod
    def _domain(relative_path: str) -> str:
        if relative_path == "SKILL.md":
            return "constitution"
        if relative_path.startswith("architecture/"):
            return "architecture"
        if relative_path.startswith("knowledge/source-preservation"):
            return "source_preservation"
        if relative_path.startswith("knowledge/photographic-reality"):
            return "photographic_reality"
        if relative_path.startswith("knowledge/anti-ai-realism"):
            return "anti_ai_realism"
        if relative_path.startswith("knowledge/production-intelligence"):
            return "production_intelligence"
        if relative_path.startswith("qc/"):
            return "qc"
        if relative_path.startswith("workflows/"):
            return "workflow"
        if relative_path.startswith("research/learned-rules/"):
            return "learned_rules"
        if relative_path.startswith("research/"):
            return "research_policy"
        return "general"

    @staticmethod
    def _authority(relative_path: str) -> int:
        if relative_path == "SKILL.md":
            return 100
        if relative_path.startswith("architecture/operating-constitution"):
            return 100
        if relative_path.startswith("knowledge/source-preservation"):
            return 95
        if relative_path.startswith("qc/"):
            return 90
        if relative_path.startswith("knowledge/"):
            return 85
        if relative_path.startswith("workflows/"):
            return 80
        if relative_path.startswith("research/learned-rules/"):
            return 60
        return 50

    @staticmethod
    def _split_sections(text: str) -> list[tuple[str, str]]:
        sections: list[tuple[str, list[str]]] = []
        current_title = "document"
        current_lines: list[str] = []
        for line in text.splitlines():
            if line.startswith("#"):
                if current_lines:
                    sections.append((current_title, current_lines))
                current_title = line.lstrip("#").strip() or "section"
                current_lines = []
            else:
                current_lines.append(line)
        if current_lines:
            sections.append((current_title, current_lines))
        return [
            (title, "\n".join(lines).strip())
            for title, lines in sections
            if "\n".join(lines).strip()
        ]

    def sync_local(self) -> str:
        files: list[tuple[str, str]] = []
        for path in self.root.rglob("*.md"):
            rel = path.relative_to(self.root).as_posix()
            if not self._eligible(rel):
                continue
            files.append((rel, path.read_text(encoding="utf-8")))
        files.sort(key=lambda item: item[0])

        digest = sha256()
        units: list[KnowledgeUnit] = []
        for rel, text in files:
            digest.update(rel.encode())
            digest.update(text.encode())
            domain = self._domain(rel)
            authority = self._authority(rel)
            for idx, (section, body) in enumerate(self._split_sections(text)):
                unit_id = sha256(f"{rel}:{section}:{idx}".encode()).hexdigest()[:20]
                units.append(KnowledgeUnit(unit_id, rel, section, domain, authority, body))

        self.revision = digest.hexdigest()[:24]
        self.units = units
        return self.revision

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {
            t
            for t in re.findall(r"[a-z0-9_\-]+", text.lower())
            if len(t) > 2
        }

    def retrieve(
        self,
        request: BrainRetrieveRequest,
        limit: int = 16,
    ) -> list[KnowledgeUnit]:
        if not self.units:
            self.sync_local()

        query = " ".join(
            [
                request.mode.value,
                request.reality_class or "",
                " ".join(request.source_roles),
                " ".join(request.required_capabilities),
            ]
        )
        qtokens = self._tokens(query)

        always_domains = {"constitution"}
        if "PRESERVATION" in request.mode.value or "EDIT" in request.mode.value:
            always_domains.update(
                {"source_preservation", "qc", "anti_ai_realism"}
            )

        scored: list[tuple[float, KnowledgeUnit]] = []
        for unit in self.units:
            text_tokens = self._tokens(unit.section + " " + unit.text)
            overlap = len(qtokens & text_tokens)
            domain_bonus = 12 if unit.domain in always_domains else 0
            authority_bonus = unit.authority / 25
            score = overlap * 5 + domain_bonus + authority_bonus
            if score > 2:
                scored.append((score, unit))

        scored.sort(
            key=lambda pair: (-pair[0], -pair[1].authority, pair[1].unit_id)
        )
        selected: list[KnowledgeUnit] = []
        seen: set[str] = set()
        for _, unit in scored:
            if unit.unit_id in seen:
                continue
            selected.append(unit)
            seen.add(unit.unit_id)
            if len(selected) >= limit:
                break
        return selected
