from pathlib import Path
import os

from fastapi.testclient import TestClient

from fashionos_intelligence.services.cognition import CognitionService
from fashionos_intelligence.services.learning import LearningService
from fashionos_intelligence.services.memory import MemoryService
from fashionos_intelligence.services.practice import PracticeService
from fashionos_intelligence.services.sensory import SensoryRegistry


def _configure(tmp_path: Path) -> None:
    (tmp_path / "SKILL.md").write_text(
        "# Constitution\nNeutral brain.",
        encoding="utf-8",
    )
    os.environ["FASHIONOS_BRAIN_ROOT"] = str(tmp_path)
    os.environ["FASHIONOS_INTERNAL_TOKEN"] = "test-secret"
    os.environ["FASHIONOS_DATABASE_URL"] = "sqlite+pysqlite:///:memory:"


def test_cognition_selects_relevant_councils_and_requires_review_for_high_risk():
    service = CognitionService()
    plan = service.plan(
        mode="FASHION_EDITORIAL",
        capabilities=["lighting", "garment", "campaign"],
        rights_statuses=["authorized"],
        hard_locks=[],
        requested_changes=[],
        preservation_required=False,
        evidence_count=4,
        independent_source_count=3,
        contradiction_count=0,
        unknown_count=1,
        high_risk=True,
    )
    assert "lighting" in plan.councils
    assert "fashion_garment" in plan.councils
    assert "creative_direction" in plan.councils
    assert plan.human_review_required is True


def test_value_gate_blocks_reference_only_production_reuse():
    service = CognitionService()
    plan = service.plan(
        mode="SOURCE_WEBSITE_TREATMENT",
        capabilities=["photography"],
        rights_statuses=["reference_only"],
        hard_locks=[],
        requested_changes=["production_reuse"],
        preservation_required=False,
        evidence_count=1,
        independent_source_count=1,
        contradiction_count=0,
        unknown_count=0,
        high_risk=False,
    )
    assert plan.value_allowed is False
    assert "REFERENCE_ONLY_SOURCE_CANNOT_BE_USED_AS_PRODUCTION_ASSET" in plan.blockers


def test_learning_candidate_cannot_auto_promote():
    service = LearningService()
    candidate = service.create(
        observation="Repeated controlled-side-light pattern.",
        proposed_principle="Side light can increase material relief in this scope.",
        scope="fashion_editorial",
        evidence_ids=["e1", "e2"],
        confidence="high",
    )
    assert candidate.decision_status == "pending"

    try:
        service.promote(candidate.candidate_id, human_approved=False)
        assert False, "promotion should require explicit approval"
    except PermissionError:
        pass

    promoted = service.promote(candidate.candidate_id, human_approved=True)
    assert promoted.decision_status == "promoted"


def test_memory_can_decay_and_deprecate_without_silent_deletion():
    service = MemoryService()
    record = service.remember(
        memory_type="episodic",
        scope="practice",
        content="A test failure occurred.",
        evidence_ids=["run_1"],
    )
    service.decay(record.memory_id, 0.4)
    assert record.weight == 0.6
    service.deprecate(record.memory_id, "superseded")
    assert record.status == "deprecated"


def test_practice_planner_is_internal_and_non_public_by_default():
    plan = PracticeService().plan(
        target_principle="motivated side light",
        mode="principle_drill",
        fixed_variables=["garment", "pose"],
        controlled_variables=["light_direction"],
        candidate_count=4,
    )
    assert plan.candidate_count == 4
    assert plan.public_asset is False


def test_sensory_change_detection_is_deterministic():
    registry = SensoryRegistry()
    source = registry.register(
        url="https://example.com/fashion",
        source_class="website",
        authority="primary",
        rights_status="authorized",
    )
    assert registry.changed(source.source_id, b"version-a") is True
    assert registry.changed(source.source_id, b"version-a") is False
    assert registry.changed(source.source_id, b"version-b") is True


def test_internal_cognition_and_learning_endpoints(tmp_path: Path):
    _configure(tmp_path)
    from fashionos_intelligence.main import app

    headers = {"X-Internal-Token": "test-secret"}
    with TestClient(app) as client:
        cognition = client.post(
            "/internal/v1/cognition/plan",
            headers=headers,
            json={
                "mode": "FASHION_EDITORIAL",
                "capabilities": ["garment", "lighting", "campaign"],
                "rightsStatuses": ["authorized"],
                "evidenceCount": 3,
                "independentSourceCount": 2,
            },
        )
        assert cognition.status_code == 200
        body = cognition.json()
        assert "fashion_garment" in body["councils"]
        assert body["valueAllowed"] is True

        candidate = client.post(
            "/internal/v1/learning/candidates",
            headers=headers,
            json={
                "observation": "Observed repeatable pattern.",
                "proposedPrinciple": "A scoped candidate principle.",
                "scope": "test",
                "evidenceIds": ["source_1", "source_2"],
                "confidence": "high",
            },
        )
        assert candidate.status_code == 200
        candidate_id = candidate.json()["candidateId"]

        blocked = client.post(
            f"/internal/v1/learning/candidates/{candidate_id}/promote",
            headers=headers,
            json={"humanApproved": False},
        )
        assert blocked.status_code == 409

        promoted = client.post(
            f"/internal/v1/learning/candidates/{candidate_id}/promote",
            headers=headers,
            json={"humanApproved": True},
        )
        assert promoted.status_code == 200
        assert promoted.json()["decisionStatus"] == "promoted"


def test_memory_practice_and_sensory_endpoints_are_private(tmp_path: Path):
    _configure(tmp_path)
    from fashionos_intelligence.main import app

    headers = {"X-Internal-Token": "test-secret"}
    with TestClient(app) as client:
        denied = client.post(
            "/internal/v1/practice/plan",
            json={
                "targetPrinciple": "contrast",
                "mode": "principle_drill",
            },
        )
        assert denied.status_code == 403

        practice = client.post(
            "/internal/v1/practice/plan",
            headers=headers,
            json={
                "targetPrinciple": "contrast",
                "mode": "principle_drill",
                "fixedVariables": ["garment"],
                "controlledVariables": ["environment"],
                "candidateCount": 3,
            },
        )
        assert practice.status_code == 200
        assert practice.json()["publicAsset"] is False

        memory = client.post(
            "/internal/v1/memory",
            headers=headers,
            json={
                "memoryType": "episodic",
                "scope": "test",
                "content": "test episode",
                "evidenceIds": ["e1"],
            },
        )
        assert memory.status_code == 200

        source = client.post(
            "/internal/v1/sensory/sources",
            headers=headers,
            json={
                "url": "https://example.com",
                "sourceClass": "website",
                "authority": "primary",
                "rightsStatus": "authorized",
            },
        )
        assert source.status_code == 200
        assert source.json()["sourceId"].startswith("source_")


def test_novelty_contamination_background_and_failure_services():
    from fashionos_intelligence.services.background_synthesis import BackgroundSynthesisService
    from fashionos_intelligence.services.contamination import ContaminationMonitor
    from fashionos_intelligence.services.failure_learning import FailureLearningService
    from fashionos_intelligence.services.novelty import NoveltyService

    novelty = NoveltyService().evaluate(
        "soft daylight against raw concrete",
        ["soft daylight against raw concrete", "hard flash in studio"],
    )
    assert novelty.label == "low"

    contamination = ContaminationMonitor().evaluate(
        ["source_a", "source_a", "source_a", "source_a", "source_b"],
        dominance_threshold=0.6,
        minimum_sample=5,
    )
    assert "SOURCE_CONCENTRATION" in contamination.flags
    assert contamination.promotion_blocked is True

    synthesis = BackgroundSynthesisService().synthesize(
        [
            "raw concrete contrast garment",
            "raw concrete contrast garment",
            "soft botanical daylight",
        ]
    )
    assert synthesis
    assert synthesis[0].evidence_count == 2

    failure = FailureLearningService().analyze(
        "GARMENT_DRIFT",
        recurrence_count=2,
    )
    assert failure.likely_category == "preservation"
    assert failure.create_learning_candidate is True


def test_creative_synthesis_produces_cross_principle_directions():
    from fashionos_intelligence.services.creative_synthesis import CreativeSynthesisService

    directions = CreativeSynthesisService().diverge(
        principles=[
            "material contrast",
            "motivated side light",
            "asymmetric hierarchy",
        ],
        councils=["fashion_garment", "lighting", "art_direction"],
        max_directions=3,
    )
    assert len(directions) == 3
    assert all(direction.principles for direction in directions)
    assert all(direction.tension for direction in directions)


def test_extended_internal_intelligence_endpoints(tmp_path: Path):
    _configure(tmp_path)
    from fashionos_intelligence.main import app

    headers = {"X-Internal-Token": "test-secret"}
    with TestClient(app) as client:
        novelty = client.post(
            "/internal/v1/novelty/evaluate",
            headers=headers,
            json={
                "candidate": "soft daylight against raw concrete",
                "references": ["soft daylight against raw concrete"],
            },
        )
        assert novelty.status_code == 200
        assert novelty.json()["label"] == "low"

        contamination = client.post(
            "/internal/v1/contamination/check",
            headers=headers,
            json={
                "origins": ["a", "a", "a", "a", "b"],
                "dominanceThreshold": 0.6,
                "minimumSample": 5,
            },
        )
        assert contamination.status_code == 200
        assert contamination.json()["promotionBlocked"] is True

        background = client.post(
            "/internal/v1/background/synthesize",
            headers=headers,
            json={
                "observations": [
                    "raw concrete contrast garment",
                    "raw concrete contrast garment",
                ]
            },
        )
        assert background.status_code == 200
        assert background.json()

        failure = client.post(
            "/internal/v1/failure/analyze",
            headers=headers,
            json={
                "failureCode": "IDENTITY_DRIFT",
                "recurrenceCount": 2,
            },
        )
        assert failure.status_code == 200
        assert failure.json()["createLearningCandidate"] is True

        creative = client.post(
            "/internal/v1/creative/diverge",
            headers=headers,
            json={
                "principles": [
                    "material contrast",
                    "motivated light",
                    "hierarchy",
                ],
                "councils": ["fashion_garment", "lighting"],
                "maxDirections": 2,
            },
        )
        assert creative.status_code == 200
        assert len(creative.json()) == 2


def test_attention_and_curiosity_services():
    from fashionos_intelligence.services.attention import AttentionService
    from fashionos_intelligence.services.curiosity import CuriosityService

    ranked = AttentionService().rank(
        [
            {
                "item_id": "a",
                "relevance": 0.9,
                "risk": 0.8,
                "uncertainty": 0.7,
                "novelty": 0.2,
                "user_priority": 0.9,
                "cost": 0.2,
            },
            {
                "item_id": "b",
                "relevance": 0.4,
                "risk": 0.1,
                "uncertainty": 0.2,
                "novelty": 0.9,
                "user_priority": 0.1,
                "cost": 0.1,
            },
        ]
    )
    assert ranked[0].item_id == "a"
    assert "HIGH_RELEVANCE" in ranked[0].reasons

    questions = CuriosityService().generate(
        repeated_uncertainties=["fabric sheen under mixed light"],
        recurring_failures=["GARMENT_DRIFT"],
        contradictions=["hard light reads premium vs hard light reads harsh"],
        coverage_gaps=["Pakistani menswear motion references"],
        affected_domains=["lighting", "fashion_garment"],
    )
    assert len(questions) == 4
    assert any(item.reason == "RECURRING_FAILURE" for item in questions)


def test_attention_and_curiosity_endpoints(tmp_path: Path):
    _configure(tmp_path)
    from fashionos_intelligence.main import app

    headers = {"X-Internal-Token": "test-secret"}
    with TestClient(app) as client:
        attention = client.post(
            "/internal/v1/attention/rank",
            headers=headers,
            json={
                "items": [
                    {
                        "itemId": "important",
                        "relevance": 0.95,
                        "risk": 0.8,
                        "uncertainty": 0.7,
                        "novelty": 0.4,
                        "userPriority": 0.9,
                        "cost": 0.2,
                    },
                    {
                        "itemId": "minor",
                        "relevance": 0.2,
                        "risk": 0.1,
                        "uncertainty": 0.1,
                        "novelty": 0.2,
                        "userPriority": 0.1,
                        "cost": 0.1,
                    },
                ]
            },
        )
        assert attention.status_code == 200
        assert attention.json()[0]["itemId"] == "important"

        curiosity = client.post(
            "/internal/v1/curiosity/questions",
            headers=headers,
            json={
                "repeatedUncertainties": ["mixed light fabric response"],
                "recurringFailures": ["GARMENT_DRIFT"],
                "contradictions": [],
                "coverageGaps": [],
                "affectedDomains": ["lighting", "fashion_garment"],
            },
        )
        assert curiosity.status_code == 200
        assert len(curiosity.json()) == 2


def test_memory_and_learning_persist_through_repository(tmp_path: Path):
    from fashionos_intelligence.persistence.db import build_session_factory
    from fashionos_intelligence.persistence.learning import LearningRepository
    from fashionos_intelligence.persistence.memory import MemoryRepository

    db_url = f"sqlite+pysqlite:///{tmp_path / 'organism.db'}"
    sessions = build_session_factory(db_url)

    memory_repo = MemoryRepository(sessions)
    memory_a = MemoryService(memory_repo)
    remembered = memory_a.remember(
        memory_type="episodic",
        scope="campaign_x",
        content="Approved lighting decision.",
        evidence_ids=["decision_1"],
    )

    memory_b = MemoryService(memory_repo)
    recalled = memory_b.retrieve(
        memory_type="episodic",
        scope="campaign_x",
    )
    assert recalled
    assert recalled[0].memory_id == remembered.memory_id

    learning_repo = LearningRepository(sessions)
    learning_a = LearningService(learning_repo)
    candidate = learning_a.create(
        observation="Repeated result across independent tests.",
        proposed_principle="Scoped reusable principle.",
        scope="practice",
        evidence_ids=["e1", "e2"],
        confidence="high",
    )

    learning_b = LearningService(learning_repo)
    restored = learning_b.get(candidate.candidate_id)
    assert restored is not None
    assert restored.decision_status == "pending"
    promoted = learning_b.promote(
        candidate.candidate_id,
        human_approved=True,
    )
    assert promoted.decision_status == "promoted"
