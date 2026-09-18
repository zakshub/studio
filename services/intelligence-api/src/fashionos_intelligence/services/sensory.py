from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from uuid import uuid4


@dataclass
class SensorySource:
    source_id: str
    url: str
    source_class: str
    authority: str
    rights_status: str
    last_fingerprint: str | None = None


class SensoryRegistry:
    def __init__(self) -> None:
        self._sources: dict[str, SensorySource] = {}

    def register(
        self,
        *,
        url: str,
        source_class: str,
        authority: str,
        rights_status: str,
    ) -> SensorySource:
        source = SensorySource(
            source_id=f"source_{uuid4().hex[:16]}",
            url=url,
            source_class=source_class,
            authority=authority,
            rights_status=rights_status,
        )
        self._sources[source.source_id] = source
        return source

    @staticmethod
    def fingerprint(payload: bytes) -> str:
        return sha256(payload).hexdigest()

    def changed(self, source_id: str, payload: bytes) -> bool:
        source = self._sources.get(source_id)
        if source is None:
            raise KeyError("SOURCE_NOT_FOUND")
        current = self.fingerprint(payload)
        has_changed = current != source.last_fingerprint
        source.last_fingerprint = current
        return has_changed
