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
