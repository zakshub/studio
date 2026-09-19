from pathlib import Path

from fashionos_intelligence.domain.enums import TaskMode
from fashionos_intelligence.persistence.benchmarks import BenchmarkRepository
from fashionos_intelligence.persistence.db import build_session_factory
from fashionos_intelligence.persistence.learning import LearningRepository
from fashionos_intelligence.persistence.memory import MemoryRepository
from fashionos_intelligence.persistence.runtime_records import (
    ExecutionRepository,
    ProvenanceRepository,
    QCRepository,
)
from fashionos_intelligence.services.benchmarks import BenchmarkService
from fashionos_intelligence.services.brain import BrainIndex
from fashionos_intelligence.services.cognition import CognitionService
from fashionos_intelligence.services.creative_synthesis import CreativeSynthesisService
from fashionos_intelligence.services.executors import ExecutorGateway
from fashionos_intelligence.services.expert_intelligence import ExpertIntelligenceService
from fashionos_intelligence.services.learning import LearningService
from fashionos_intelligence.services.memory import MemoryService
from fashionos_intelligence.services.organism_loop import CreativeOrganismLoop, OrganismTask
from fashionos_intelligence.services.provenance import ProvenanceService
from fashionos_intelligence.services.qc_runtime import QCDimension, QCRuntime


def _loop(tmp_path: Path) -> CreativeOrganismLoop:
    brain_root = tmp_path / "brain"
    brain_root.mkdir()
    (brain_root / "SKILL.md").write_text(
        "# Constitution\nPreserve truth, constraints, and source integrity.",
        encoding="utf-8",
    )
    brain = BrainIndex(brain_root)
    brain.sync_local()

    sessions = build_session_factory("sqlite+pysqlite:///:memory:")
    return CreativeOrganismLoop(
        brain=brain,
        cognition=CognitionService(),
        experts=ExpertIntelligenceService([]),
        creativity=CreativeSynthesisService(),
        benchmarks=BenchmarkService(BenchmarkRepository(sessions)),
        executors=ExecutorGateway(),
        qc=QCRuntime(),
        provenance=ProvenanceService(ProvenanceRepository(sessions)),
        memory=MemoryService(MemoryRepository(sessions)),
        learning=LearningService(LearningRepository(sessions)),
        execution_repository=ExecutionRepository(sessions),
        qc_repository=QCRepository(sessions),
    )


def test_organism_loop_closes_think_execute_qc_memory_cycle(tmp_path: Path):
    loop = _loop(tmp_path)
    result = loop.run(
        OrganismTask(
            task_id="task_1",
            objective="Run a deterministic internal practice action",
            mode=TaskMode.REFERENCE_RESEARCH,
            capability="noop",
            rights_statuses=("authorized",),
            independent_source_count=2,
            execution_payload={"assetIds": []},
        ),
        qc_evaluator=lambda _: [
            QCDimension("physical_coherence", 5, critical=True),
            QCDimension("provenance", 5, critical=True),
        ],
    )
    assert result.status == "completed"
    assert result.qc_status == "pass"
    assert result.provenance_id is not None
    assert result.knowledge_unit_ids


def test_organism_loop_blocks_hard_lock_conflict_before_execution(tmp_path: Path):
    loop = _loop(tmp_path)
    result = loop.run(
        OrganismTask(
            task_id="task_2",
            objective="Change a locked garment",
            mode=TaskMode.STRICT_PRESERVATION_EDIT,
            capability="noop",
            rights_statuses=("authorized",),
            hard_locks=("garment",),
            allowed_changes=("garment",),
            preservation_required=True,
            independent_source_count=2,
        ),
        qc_evaluator=lambda _: [QCDimension("preservation", 5, critical=True)],
    )
    assert result.status == "blocked"
    assert "HARD_LOCK_CONFLICT:garment" in result.blockers
    assert result.executor_classes == ()
