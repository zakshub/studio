from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json

from fashionos_intelligence.services.brain import KnowledgeUnit


class BrainSnapshotStore:
    """Durable JSON snapshot store for normalized brain revisions."""

    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, revision: str, units: list[KnowledgeUnit]) -> Path:
        target = self.root / f"{revision}.json"
        temp = self.root / f".{revision}.tmp"
        payload = {
            "revision": revision,
            "units": [asdict(unit) for unit in units],
        }
        temp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        temp.replace(target)
        return target

    def load(self, revision: str) -> list[KnowledgeUnit]:
        target = self.root / f"{revision}.json"
        if not target.exists():
            raise KeyError("BRAIN_REVISION_NOT_FOUND")
        payload = json.loads(target.read_text(encoding="utf-8"))
        if payload.get("revision") != revision:
            raise ValueError("BRAIN_SNAPSHOT_REVISION_MISMATCH")
        return [KnowledgeUnit(**item) for item in payload.get("units", [])]

    def revisions(self) -> tuple[str, ...]:
        return tuple(sorted(path.stem for path in self.root.glob("*.json")))
