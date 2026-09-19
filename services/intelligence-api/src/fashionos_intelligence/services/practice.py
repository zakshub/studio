from __future__ import annotations

from dataclasses import asdict, dataclass
from uuid import uuid4

from fashionos_intelligence.persistence.cognition_records import PracticeRepository, StoredPractice


@dataclass(frozen=True)
class PracticePlan:
    session_id: str
    target_principle: str
    mode: str
    fixed_variables: tuple[str, ...]
    controlled_variables: tuple[str, ...]
    candidate_count: int
    evaluation_dimensions: tuple[str, ...]
    public_asset: bool


class PracticeService:
    def __init__(self, repository: PracticeRepository | None = None) -> None:
        self.repository = repository

    def plan(
        self,
        *,
        target_principle: str,
        mode: str,
        fixed_variables: list[str],
        controlled_variables: list[str],
        candidate_count: int = 3,
    ) -> PracticePlan:
        safe_count = max(2, min(candidate_count, 12))
        plan = PracticePlan(
            session_id=f"practice_{uuid4().hex[:16]}",
            target_principle=target_principle,
            mode=mode,
            fixed_variables=tuple(fixed_variables),
            controlled_variables=tuple(controlled_variables),
            candidate_count=safe_count,
            evaluation_dimensions=(
                "objective_fit",
                "constraint_compliance",
                "physical_coherence",
                "originality",
                "context_suitability",
                "execution_quality",
            ),
            public_asset=False,
        )
        if self.repository is not None:
            self.repository.upsert(
                StoredPractice(
                    session_id=plan.session_id,
                    target_principle=plan.target_principle,
                    mode=plan.mode,
                    status="planned",
                    payload=asdict(plan),
                )
            )
        return plan
