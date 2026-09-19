from pathlib import Path

from fashionos_intelligence.domain.enums import TaskMode
from fashionos_intelligence.domain.models import BrainRetrieveRequest
from fashionos_intelligence.persistence.assets import AssetRepository, StoredAsset
from fashionos_intelligence.persistence.cognition_records import (
    ObservationRepository,
    PracticeRepository,
)
from fashionos_intelligence.persistence.db import build_session_factory
from fashionos_intelligence.persistence.runtime_records import (
    ApprovalRepository,
    ExecutionRepository,
    ProvenanceRepository,
    QCRepository,
    StoredApproval,
    StoredExecution,
    StoredProvenance,
    StoredQC,
)
from fashionos_intelligence.services.brain import BrainIndex
from fashionos_intelligence.services.brain_snapshots import BrainSnapshotStore
from fashionos_intelligence.services.observations import ObservationService
from fashionos_intelligence.services.practice import PracticeService
from fashionos_intelligence.services.source_harvester import WebsiteHarvester


def _brain_root(tmp_path: Path) -> Path:
    root = tmp_path / "brain"
    root.mkdir()
    (root / "SKILL.md").write_text(
        "# Constitution\nPreserve source truth and keep unknowns unknown.",
        encoding="utf-8",
    )
    p = root / "knowledge" / "source-preservation"
    p.mkdir(parents=True)
    (p / "source-preservation.md").write_text(
        "# Preservation\nLocked garment elements must not change.",
        encoding="utf-8",
    )
    return root


def test_durable_revision_snapshot_can_reload_after_new_instance(tmp_path: Path):
    root = _brain_root(tmp_path)
    store = BrainSnapshotStore(tmp_path / "snapshots")
    first = BrainIndex(root, snapshot_store=store)
    revision = first.sync_local()

    second = BrainIndex(root, snapshot_store=BrainSnapshotStore(tmp_path / "snapshots"))
    assert revision in second.available_revisions()
    second.rollback(revision)
    assert second.revision == revision
    assert second.units


def test_brain_structured_rules_resolve_hard_lock_conflict(tmp_path: Path):
    root = _brain_root(tmp_path)
    brain = BrainIndex(root)
    brain.sync_local()
    request = BrainRetrieveRequest(
        taskId="task_1",
        mode=TaskMode.STRICT_PRESERVATION_EDIT,
        rightsStatuses=["authorized"],
        hardLocks=["garment"],
        allowedChanges=["garment"],
        preservationRequired=True,
    )
    conflicts = brain.conflicts_for(request)
    change = next(item for item in conflicts if item["subject"] == "change:garment")
    assert change["selectedRuleId"] == "HARD_LOCK_FORBIDS_GARMENT"
    assert change["reason"] == "HIGHER_AUTHORITY_OR_SPECIFICITY"


def test_website_harvester_discovers_and_deduplicates_media():
    html = """
    <html><body>
      <img src="/a.jpg" alt="look">
      <img src="/a.jpg" alt="duplicate">
      <video src="/campaign.mp4"></video>
      <source src="/campaign-2.mp4" type="video/mp4">
    </body></html>
    """
    items = WebsiteHarvester().discover(
        page_url="https://example.com/collection",
        html=html,
    )
    assert len(items) == 3
    assert items[0].url == "https://example.com/a.jpg"
    assert any(item.media_type == "video" for item in items)


def test_core_runtime_records_persist_in_sqlite():
    sessions = build_session_factory("sqlite+pysqlite:///:memory:")

    assets = AssetRepository(sessions)
    assets.upsert(
        StoredAsset(
            asset_id="asset_1",
            workspace_id="ws_1",
            source_type="upload",
            source_url=None,
            role="primary",
            rights_status="authorized",
            content_hash="abc",
            storage_uri="memory://asset_1",
            metadata={"kind": "image"},
        )
    )
    assert assets.get("asset_1") is not None

    executions = ExecutionRepository(sessions)
    executions.upsert(
        StoredExecution(
            execution_id="exec_1",
            task_id="task_1",
            brain_revision="rev_1",
            source_asset_ids=["asset_1"],
            output_asset_ids=["asset_2"],
            knowledge_unit_ids=["unit_1"],
            executor_class="deterministic",
            status="succeeded",
            payload={},
        )
    )
    assert executions.get("exec_1") is not None

    QCRepository(sessions).upsert(
        StoredQC(
            qc_id="qc_1",
            execution_id="exec_1",
            status="pass",
            dimensions={"preservation": 5},
            critical_failures=[],
            requires_rework=False,
            human_review_required=False,
        )
    )
    ApprovalRepository(sessions).upsert(
        StoredApproval(
            approval_id="approval_1",
            workspace_id="ws_1",
            task_id="task_1",
            subject_type="execution",
            subject_id="exec_1",
            status="approved",
        )
    )
    ProvenanceRepository(sessions).upsert(
        StoredProvenance(
            provenance_id="prov_1",
            execution_id="exec_1",
            task_id="task_1",
            brain_revision="rev_1",
            source_asset_ids=["asset_1"],
            output_asset_ids=["asset_2"],
            knowledge_unit_ids=["unit_1"],
            qc_status="pass",
            lineage=[{"parent": "asset_1", "child": "asset_2"}],
        )
    )


def test_practice_and_observation_persistence():
    sessions = build_session_factory("sqlite+pysqlite:///:memory:")

    practice = PracticeService(PracticeRepository(sessions))
    plan = practice.plan(
        target_principle="motivated light",
        mode="FASHION_EDITORIAL",
        fixed_variables=["garment"],
        controlled_variables=["light_direction"],
    )
    assert plan.session_id.startswith("practice_")

    observations = ObservationService(ObservationRepository(sessions))
    result = observations.normalize(
        source_id="source_1",
        media_type="image",
        raw=[
            {
                "dimension": "lighting",
                "value": "soft side light",
                "confidence": "high",
                "interpretation": False,
            }
        ],
    )
    assert len(result) == 1
