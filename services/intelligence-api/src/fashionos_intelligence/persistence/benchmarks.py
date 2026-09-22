from __future__ import annotations

from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from fashionos_intelligence.persistence.db import BenchmarkRow


@dataclass(frozen=True)
class StoredBenchmark:
    benchmark_id: str
    case_id: str
    capability: str
    executor_name: str
    executor_version: str | None
    scores: dict[str, float]
    latency_ms: float | None
    cost_estimate: float | None
    accepted: bool | None


class BenchmarkRepository:
    def __init__(self, sessions: sessionmaker[Session]):
        self.sessions = sessions

    def add(self, item: StoredBenchmark) -> StoredBenchmark:
        with self.sessions() as session:
            session.add(
                BenchmarkRow(
                    benchmark_id=item.benchmark_id,
                    case_id=item.case_id,
                    capability=item.capability,
                    executor_name=item.executor_name,
                    executor_version=item.executor_version,
                    scores=dict(item.scores),
                    latency_ms=item.latency_ms,
                    cost_estimate=item.cost_estimate,
                    accepted=item.accepted,
                )
            )
            session.commit()
        return item

    def for_capability(self, capability: str) -> list[StoredBenchmark]:
        with self.sessions() as session:
            rows = session.scalars(
                select(BenchmarkRow).where(BenchmarkRow.capability == capability)
            ).all()
            return [
                StoredBenchmark(
                    benchmark_id=row.benchmark_id,
                    case_id=row.case_id,
                    capability=row.capability,
                    executor_name=row.executor_name,
                    executor_version=row.executor_version,
                    scores=dict(row.scores or {}),
                    latency_ms=row.latency_ms,
                    cost_estimate=row.cost_estimate,
                    accepted=row.accepted,
                )
                for row in rows
            ]
