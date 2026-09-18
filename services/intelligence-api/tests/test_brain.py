from pathlib import Path

from fashionos_intelligence.domain.enums import TaskMode
from fashionos_intelligence.domain.models import BrainRetrieveRequest
from fashionos_intelligence.services.brain import BrainIndex


def test_preservation_retrieval_includes_preservation_domain(tmp_path: Path):
    (tmp_path / "SKILL.md").write_text(
        "# Constitution\nPreserve source truth.",
        encoding="utf-8",
    )
    p = tmp_path / "knowledge" / "source-preservation"
    p.mkdir(parents=True)
    (p / "source-preservation.md").write_text(
        "# Preservation\nIdentity and garment are hard locks.",
        encoding="utf-8",
    )
    q = tmp_path / "qc"
    q.mkdir(parents=True)
    (q / "forensic-reality-qc.md").write_text(
        "# QC\nPreservation failure requires rework.",
        encoding="utf-8",
    )

    brain = BrainIndex(tmp_path)
    revision = brain.sync_local()
    assert revision != "uninitialized"

    result = brain.retrieve(
        BrainRetrieveRequest(
            taskId="task_1",
            mode=TaskMode.STRICT_PRESERVATION_EDIT,
            sourceRoles=["primary"],
            realityClass="professional_lifestyle",
            requiredCapabilities=["preservation", "garment", "qc"],
        )
    )
    domains = {unit.domain for unit in result}
    assert "source_preservation" in domains
    assert "qc" in domains
