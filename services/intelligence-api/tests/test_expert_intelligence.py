from pathlib import Path

from fashionos_intelligence.services.expert_profiles import ExpertProfileLoader
from fashionos_intelligence.services.expert_intelligence import ExpertIntelligenceService


PROFILE = """# Expert Intelligence — Test Expert

Expert ID: EXP-T01
Status: SYNTHESIZED / NOT YET VALIDATED
Primary domains: photography
Primary councils: Photography, Lighting

## Documented decision principles

### Light follows the subject
Type: stated_by_expert
Evidence: TE-001, TE-002
Principle:
Use lighting in response to the subject rather than as decoration.

### Meaning before ornament
Type: observed
Evidence: TE-003
Principle:
Prefer a clear visual idea over decorative complexity.

## Problem-solving model
1. observe
2. decide
"""


def test_expert_profile_loader_extracts_councils_and_principles(tmp_path: Path):
    root = tmp_path / "profiles"
    root.mkdir()
    path = root / "test-expert.md"
    path.write_text(PROFILE, encoding="utf-8")

    profile = ExpertProfileLoader(root).load_all()[0]
    assert profile.expert_id == "EXP-T01"
    assert "photography" in profile.councils
    assert "lighting" in profile.councils
    assert len(profile.principles) == 2
    assert profile.principles[0].evidence == ("TE-001", "TE-002")


def test_expert_intelligence_consults_only_relevant_councils(tmp_path: Path):
    root = tmp_path / "profiles"
    root.mkdir()
    (root / "test-expert.md").write_text(PROFILE, encoding="utf-8")
    profiles = ExpertProfileLoader(root).load_all()

    consultation = ExpertIntelligenceService(profiles).consult(
        councils=["lighting"],
    )
    assert consultation.selected_experts == ("EXP-T01",)
    assert consultation.insights
    assert consultation.insights[0].council == "lighting"
    assert consultation.insights[0].principles
