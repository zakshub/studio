from pathlib import Path

import pytest

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
from fashionos_intelligence.services.attention import AttentionService
from fashionos_intelligence.services.benchmarks import BenchmarkService
from fashionos_intelligence.services.brain import BrainIndex
from fashionos_intelligence.services.cognition import CognitionService
from fashionos_intelligence.services.contamination import ContaminationMonitor
from fashionos_intelligence.services.creative_synthesis import CreativeSynthesisService
from fashionos_intelligence.services.curiosity import CuriosityService
from fashionos_intelligence.services.executors import (
    CallableExecutorAdapter,
    ExecutionRequest,
    ExecutionResult,
    ExecutorGateway,
)
from fashionos_intelligence.services.expert_intelligence import ExpertIntelligenceService
from fashionos_intelligence.services.expert_profiles import ExpertProfileLoader
from fashionos_intelligence.services.learning import LearningService
from fashionos_intelligence.services.memory import MemoryService
from fashionos_intelligence.services.novelty import NoveltyService
from fashionos_intelligence.services.organism_loop import CreativeOrganismLoop, OrganismTask
from fashionos_intelligence.services.provenance import ProvenanceService
from fashionos_intelligence.services.qc_runtime import QCDimension, QCRuntime
from fashionos_intelligence.services.routing import EvidenceRouter
from fashionos_intelligence.services.source_harvester import WebsiteHarvester
from fashionos_intelligence.services.source_policy import SourcePolicy


REPO_ROOT = Path(__file__).resolve().parents[3]
PROFILES_ROOT = REPO_ROOT / "expert-intelligence" / "profiles"


def _brain(tmp_path: Path) -> BrainIndex:
    root = tmp_path / "brain"
    root.mkdir()
    (root / "SKILL.md").write_text(
        "# Constitution\nTruth, source integrity, explicit uncertainty, and human sovereignty.",
        encoding="utf-8",
    )
    preservation = root / "knowledge" / "source-preservation"
    preservation.mkdir(parents=True)
    (preservation / "source-preservation.md").write_text(
        "# Preservation\nIdentity and garment locks outrank aesthetic change.",
        encoding="utf-8",
    )
    qc = root / "qc"
    qc.mkdir()
    (qc / "forensic-reality-qc.md").write_text(
        "# QC\nCritical preservation failure requires rework.",
        encoding="utf-8",
    )
    brain = BrainIndex(root)
    brain.sync_local()
    return brain


def _executor(name: str = "test-image-generator"):
    def run(request: ExecutionRequest) -> ExecutionResult:
        return ExecutionResult(
            executor_class=name,
            status="succeeded",
            output={"assetIds": [f"{name}-asset"], "operation": request.operation},
            diagnostics={"test": True},
        )
    return CallableExecutorAdapter(
        name=name,
        capabilities={"image_generation", "image_editing", "noop"},
        runner=run,
    )


def _organism(
    tmp_path: Path,
    *,
    memory: MemoryService | None = None,
    learning: LearningService | None = None,
    executor: CallableExecutorAdapter | None = None,
) -> CreativeOrganismLoop:
    sessions = build_session_factory("sqlite+pysqlite:///:memory:")
    profiles = ExpertProfileLoader(PROFILES_ROOT).load_all()
    return CreativeOrganismLoop(
        brain=_brain(tmp_path),
        cognition=CognitionService(),
        experts=ExpertIntelligenceService(profiles),
        creativity=CreativeSynthesisService(),
        benchmarks=BenchmarkService(BenchmarkRepository(sessions)),
        executors=ExecutorGateway([executor or _executor()]),
        qc=QCRuntime(),
        provenance=ProvenanceService(ProvenanceRepository(sessions)),
        memory=memory or MemoryService(MemoryRepository(sessions)),
        learning=learning or LearningService(LearningRepository(sessions)),
        execution_repository=ExecutionRepository(sessions),
        qc_repository=QCRepository(sessions),
    )


def test_acceptance_01_values_block_reference_only_production_reuse():
    plan = CognitionService().plan(
        mode="SOURCE_WEBSITE_TREATMENT",
        capabilities=["photography"],
        rights_statuses=["reference_only"],
        hard_locks=[],
        requested_changes=["production_reuse"],
        preservation_required=False,
        evidence_count=3,
        independent_source_count=2,
        contradiction_count=0,
        unknown_count=0,
        high_risk=False,
    )
    assert plan.value_allowed is False
    assert "REFERENCE_ONLY_SOURCE_CANNOT_BE_USED_AS_PRODUCTION_ASSET" in plan.blockers
    assert plan.human_review_required is True


def test_acceptance_02_hard_lock_beats_requested_change():
    plan = CognitionService().plan(
        mode="STRICT_PRESERVATION_EDIT",
        capabilities=["preservation"],
        rights_statuses=["authorized"],
        hard_locks=["garment", "identity"],
        requested_changes=["garment"],
        preservation_required=True,
        evidence_count=5,
        independent_source_count=2,
        contradiction_count=0,
        unknown_count=0,
        high_risk=False,
    )
    assert plan.value_allowed is False
    assert "HARD_LOCK_CONFLICT:garment" in plan.blockers


def test_acceptance_03_metacognition_reduces_confidence_without_evidence():
    plan = CognitionService().plan(
        mode="FASHION_EDITORIAL",
        capabilities=["lighting"],
        rights_statuses=["authorized"],
        hard_locks=[],
        requested_changes=[],
        preservation_required=False,
        evidence_count=0,
        independent_source_count=0,
        contradiction_count=0,
        unknown_count=0,
        high_risk=False,
    )
    assert plan.confidence == "low"
    assert "NO_EVIDENCE" in plan.metacognitive_flags
    assert plan.human_review_required is True
    assert plan.research_questions


def test_acceptance_04_attention_prioritizes_high_risk_identity_over_background_polish():
    ranked = AttentionService().rank(
        [
            {
                "item_id": "identity_drift",
                "relevance": 1.0,
                "risk": 1.0,
                "uncertainty": 0.8,
                "novelty": 0.1,
                "user_priority": 1.0,
                "cost": 0.2,
            },
            {
                "item_id": "background_polish",
                "relevance": 0.5,
                "risk": 0.1,
                "uncertainty": 0.1,
                "novelty": 0.4,
                "user_priority": 0.3,
                "cost": 0.1,
            },
        ]
    )
    assert ranked[0].item_id == "identity_drift"
    assert "HIGH_RISK" in ranked[0].reasons


def test_acceptance_05_curiosity_turns_uncertainty_and_failure_into_research_questions():
    questions = CuriosityService().generate(
        repeated_uncertainties=["white embroidery response under mixed light"],
        recurring_failures=["GARMENT_DRIFT"],
        contradictions=[],
        coverage_gaps=["Pakistani formalwear motion references"],
        affected_domains=["fashion_garment", "lighting"],
    )
    reasons = {q.reason for q in questions}
    assert {"REPEATED_UNCERTAINTY", "RECURRING_FAILURE", "COVERAGE_GAP"} <= reasons


def test_acceptance_06_memory_survives_service_recreation(tmp_path: Path):
    sessions = build_session_factory(f"sqlite+pysqlite:///{tmp_path / 'memory.db'}")
    repository = MemoryRepository(sessions)
    first = MemoryService(repository)
    record = first.remember(
        memory_type="episodic",
        scope="campaign:test",
        content="Garment fidelity was approved; preserve the exact embroidery layout.",
        evidence_ids=["approval_1"],
    )

    second = MemoryService(repository)
    recalled = second.retrieve(memory_type="episodic", scope="campaign:test")
    assert len(recalled) == 1
    assert recalled[0].memory_id == record.memory_id
    assert "embroidery" in recalled[0].content


def test_acceptance_07_learning_requires_evidence_and_human_approval(tmp_path: Path):
    sessions = build_session_factory(f"sqlite+pysqlite:///{tmp_path / 'learning.db'}")
    service = LearningService(LearningRepository(sessions))
    candidate = service.create(
        observation="A repeated failure appears related to garment reconstruction.",
        proposed_principle="Use stronger source-preservation routing for this scoped failure pattern.",
        scope="strict_preservation_edit",
        evidence_ids=["exec_1", "exec_2"],
        confidence="medium",
    )
    with pytest.raises(PermissionError, match="HUMAN_APPROVAL_REQUIRED"):
        service.promote(candidate.candidate_id, human_approved=False)

    promoted = service.promote(candidate.candidate_id, human_approved=True)
    assert promoted.decision_status == "promoted"


def test_acceptance_08_novelty_distinguishes_duplicate_from_new_combination():
    service = NoveltyService()
    duplicate = service.evaluate(
        "soft daylight raw concrete embroidered garment",
        ["soft daylight raw concrete embroidered garment"],
    )
    different = service.evaluate(
        "night transit platform directional flash kinetic fabric",
        ["soft daylight raw concrete embroidered garment"],
    )
    assert duplicate.label == "low"
    assert different.label == "high"
    assert different.score > duplicate.score


def test_acceptance_09_contamination_blocks_source_dominance():
    report = ContaminationMonitor().evaluate(
        ["brand_a", "brand_a", "brand_a", "brand_a", "brand_b"],
        dominance_threshold=0.6,
        minimum_sample=5,
    )
    assert report.dominant_group == "brand_a"
    assert "SOURCE_CONCENTRATION" in report.flags
    assert report.promotion_blocked is True


def test_acceptance_10_all_current_expert_profiles_are_machine_usable_and_not_active():
    profiles = ExpertProfileLoader(PROFILES_ROOT).load_all()
    assert len(profiles) >= 10
    assert all(profile.expert_id for profile in profiles)
    assert all(profile.councils for profile in profiles)
    assert all(profile.principles for profile in profiles), [
        profile.name for profile in profiles if not profile.principles
    ]
    assert all("ACTIVE" not in profile.status.upper() for profile in profiles)


def test_acceptance_11_expert_consultation_uses_relevant_people_and_keeps_evidence():
    profiles = ExpertProfileLoader(PROFILES_ROOT).load_all()
    consultation = ExpertIntelligenceService(profiles).consult(
        councils=["fashion_photography"],
        max_experts=10,
        max_principles_per_council=5,
    )
    assert consultation.selected_experts
    assert consultation.insights
    insight = consultation.insights[0]
    assert insight.council == "fashion_photography"
    assert insight.principles
    assert insight.expert_ids


def test_acceptance_12_creativity_generates_multiple_distinct_directions():
    directions = CreativeSynthesisService().diverge(
        principles=[
            "preserve garment truth",
            "use environment as narrative contrast",
            "let light support material readability",
            "allow motion to reveal fabric behavior",
        ],
        councils=["fashion_garment", "fashion_photography", "lighting"],
        max_directions=4,
    )
    assert len(directions) >= 3
    assert len({d.principles for d in directions}) == len(directions)
    assert all(d.tension for d in directions)


def test_acceptance_13_qc_rejects_critical_preservation_failure():
    result = QCRuntime().evaluate(
        [
            QCDimension("preservation", 2, critical=True),
            QCDimension("lighting_realism", 5, critical=False),
        ],
        preservation_required=True,
    )
    assert result.status == "fail"
    assert result.requires_rework is True
    assert result.human_review_required is True


def test_acceptance_14_source_intake_deduplicates_and_respects_reference_rights():
    html = """
    <img src="/look-01.jpg">
    <img src="/look-01.jpg">
    <video src="/campaign.mp4"></video>
    """
    items = WebsiteHarvester().discover(
        page_url="https://example.com/lookbook",
        html=html,
    )
    assert len(items) == 2

    decision = SourcePolicy().decide(
        role="secondary_reference",
        rights_status="reference_only",
    )
    assert decision.may_analyze is True
    assert decision.may_store_binary is False
    assert decision.may_publish is False


def test_acceptance_15_cold_start_router_does_not_invent_a_global_model_winner():
    router = EvidenceRouter(BenchmarkService())
    decision = router.decide(
        capability="image_generation",
        available_executors=["provider_z", "provider_a"],
    )
    assert decision.reason_code == "COLD_START_NO_SUFFICIENT_EVIDENCE"
    assert decision.ordered_executors == ("provider_a", "provider_z")


def test_acceptance_16_full_organism_loop_thinks_consults_creates_executes_checks_and_remembers(tmp_path: Path):
    sessions = build_session_factory(f"sqlite+pysqlite:///{tmp_path / 'loop-memory.db'}")
    memory = MemoryService(MemoryRepository(sessions))
    learning = LearningService(LearningRepository(sessions))
    loop = _organism(tmp_path, memory=memory, learning=learning)

    result = loop.run(
        OrganismTask(
            task_id="full_test_success",
            objective="Create an original fashion editorial direction without copying a brand or expert.",
            mode=TaskMode.FASHION_EDITORIAL,
            capability="image_generation",
            rights_statuses=("authorized",),
            independent_source_count=3,
            execution_payload={"brief": "original editorial"},
        ),
        qc_evaluator=lambda _: [
            QCDimension("physical_coherence", 5, critical=True),
            QCDimension("originality", 4.5, critical=False),
            QCDimension("provenance", 5, critical=True),
        ],
    )

    assert result.status == "completed"
    assert result.selected_experts
    assert result.creative_direction_ids
    assert result.executor_classes == ("test-image-generator",)
    assert result.qc_status == "pass"
    assert result.provenance_id
    recalled = memory.retrieve(scope="task:full_test_success")
    assert recalled


def test_acceptance_17_full_organism_stops_before_execution_when_values_are_violated(tmp_path: Path):
    calls = {"count": 0}

    def forbidden_runner(request: ExecutionRequest) -> ExecutionResult:
        calls["count"] += 1
        raise AssertionError("executor must not run after a hard-lock conflict")

    executor = CallableExecutorAdapter(
        name="should-not-run",
        capabilities={"image_editing"},
        runner=forbidden_runner,
    )
    loop = _organism(tmp_path, executor=executor)

    result = loop.run(
        OrganismTask(
            task_id="full_test_block",
            objective="Change a garment that is explicitly locked.",
            mode=TaskMode.STRICT_PRESERVATION_EDIT,
            capability="image_editing",
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
    assert calls["count"] == 0


def test_acceptance_18_failed_qc_becomes_memory_and_learning_candidate(tmp_path: Path):
    sessions = build_session_factory(f"sqlite+pysqlite:///{tmp_path / 'failure-memory.db'}")
    memory = MemoryService(MemoryRepository(sessions))
    learning = LearningService(LearningRepository(sessions))
    loop = _organism(tmp_path, memory=memory, learning=learning)

    result = loop.run(
        OrganismTask(
            task_id="full_test_failure",
            objective="Preserve a garment exactly while improving an image.",
            mode=TaskMode.STRICT_PRESERVATION_EDIT,
            capability="image_editing",
            rights_statuses=("authorized",),
            hard_locks=("garment", "identity"),
            allowed_changes=("lighting",),
            preservation_required=True,
            independent_source_count=2,
        ),
        qc_evaluator=lambda _: [
            QCDimension("preservation", 1.5, critical=True),
            QCDimension("lighting_realism", 4.5),
        ],
    )

    assert result.status == "rework_required"
    assert result.qc_status == "fail"
    assert memory.retrieve(scope="task:full_test_failure")
    assert learning._candidates
    candidate = next(iter(learning._candidates.values()))
    assert candidate.decision_status == "pending"


def test_acceptance_19_expert_profiles_contain_anti_copy_guardrails():
    files = sorted(PROFILES_ROOT.glob("*.md"))
    assert len(files) >= 10
    missing = []
    for path in files:
        text = path.read_text(encoding="utf-8").lower()
        if "anti-copy" not in text and "anti copy" not in text:
            missing.append(path.name)
    assert not missing, missing
