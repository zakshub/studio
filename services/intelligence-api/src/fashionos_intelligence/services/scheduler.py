from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Any


@dataclass
class ScheduledJob:
    name: str
    interval_seconds: int
    callback: Callable[[], Any]
    last_run_at: datetime | None = None

    def due(self, now: datetime) -> bool:
        if self.last_run_at is None:
            return True
        return (now - self.last_run_at).total_seconds() >= self.interval_seconds


class BackgroundScheduler:
    """Small in-process bootstrap. Production deployment may replace this with a worker scheduler."""

    def __init__(self) -> None:
        self.jobs: dict[str, ScheduledJob] = {}

    def register(
        self,
        name: str,
        interval_seconds: int,
        callback: Callable[[], Any],
    ) -> None:
        if interval_seconds < 60:
            raise ValueError("MIN_INTERVAL_60_SECONDS")
        self.jobs[name] = ScheduledJob(name, interval_seconds, callback)

    def run_due(self) -> dict[str, str]:
        now = datetime.now(timezone.utc)
        results: dict[str, str] = {}
        for name, job in sorted(self.jobs.items()):
            if not job.due(now):
                results[name] = "not_due"
                continue
            try:
                job.callback()
                job.last_run_at = now
                results[name] = "completed"
            except Exception:
                results[name] = "failed"
        return results
