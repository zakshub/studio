from __future__ import annotations

import json
import os
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
from fashionos_intelligence.services.expert_profiles import ExpertProfileLoader
from fashionos_intelligence.services.learning import LearningService
from fashionos_intelligence.services.live_openai import (
    OpenAIImageGenerationTransport,
    OpenAIVisionQCTransport,
)
from fashionos_intelligence.services.memory import MemoryService
from fashionos_intelligence.services.organism_loop import CreativeOrganismLoop, OrganismTask
from fashionos_intelligence.services.provider_adapters import (
    OpenAIExecutorAdapter,
    ProviderExecutorAdapter,
)
from fashionos_intelligence.services.provenance import ProvenanceService
from fashionos_intelligence.services.qc_runtime import QCRuntime
from fashionos_intelligence.services.storage import LocalContentAddressedStore


def main() -> int:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("LIVE_PROVIDER_CREDENTIAL_NOT_CONFIGURED")

    service_root = Path(__file__).resolve().parents[1]
    repo_root = service_root.parents[1]
    output_root = Path(
        os.getenv(
            "FASHIONOS_LIVE_OUTPUT_DIR",
            str(service_root / "live-artifacts"),
        )
    ).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    store = LocalContentAddressedStore(output_root / "objects")
    db_url = f"sqlite+pysqlite:///{output_root / 'live-smoke.db'}"
    sessions = build_session_factory(db_url)

    brain = BrainIndex(repo_root)
    brain.sync_local()

    profiles = ExpertProfileLoader(
        repo_root / "expert-intelligence" / "profiles"
    ).load_all()

    image_model = os.getenv("FASHIONOS_OPENAI_IMAGE_MODEL", "gpt-image-2")
    vision_model = os.getenv("FASHIONOS_OPENAI_VISION_MODEL", "gpt-5.6-luna")

    generator = OpenAIExecutorAdapter(
        name="openai-image",
        capabilities={"image_generation"},
        transport=OpenAIImageGenerationTransport(
            api_key=api_key,
            store=store,
            model=image_model,
        ),
    )
    verifier = ProviderExecutorAdapter(
        name="openai-vision-qc",
        capabilities={"vision_qc"},
        transport=OpenAIVisionQCTransport(
            api_key=api_key,
            store=store,
            model=vision_model,
        ),
    )

    loop = CreativeOrganismLoop(
        brain=brain,
        cognition=CognitionService(),
        experts=ExpertIntelligenceService(profiles),
        creativity=CreativeSynthesisService(),
        benchmarks=BenchmarkService(BenchmarkRepository(sessions)),
        executors=ExecutorGateway([generator]),
        qc=QCRuntime(),
        provenance=ProvenanceService(ProvenanceRepository(sessions)),
        memory=MemoryService(MemoryRepository(sessions)),
        learning=LearningService(LearningRepository(sessions)),
        execution_repository=ExecutionRepository(sessions),
        qc_repository=QCRepository(sessions),
        visual_verifier=verifier,
    )

    objective = (
        "Create an original Pakistani fashion editorial photograph of an anonymous adult model "
        "wearing a modest contemporary embroidered ensemble. Place the model in a believable raw "
        "concrete architectural environment with restrained soft daylight. The garment must remain "
        "the visual priority. Skin, anatomy, fabric, shadows, depth of field and camera behavior "
        "must feel like a real premium fashion production. No logos, no text, no brand imitation, "
        "and no imitation of any named photographer or artist."
    )

    result = loop.run(
        OrganismTask(
            task_id="live_image_smoke_001",
            objective=objective,
            mode=TaskMode.FASHION_EDITORIAL,
            capability="image_generation",
            rights_statuses=("authorized",),
            independent_source_count=3,
            high_value=False,
            execution_payload={
                "size": "1024x1536",
                "quality": "medium",
                "outputFormat": "png",
                "constraints": [
                    "adult model",
                    "modest fully covered fashion styling",
                    "no logos or text",
                    "no named-creator imitation",
                    "photorealistic production logic",
                ],
            },
        ),
        qc_evaluator=lambda _: [],
    )

    files = [
        str(path.relative_to(output_root))
        for path in output_root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    ]

    summary = {
        "taskId": result.task_id,
        "status": result.status,
        "brainRevision": result.brain_revision,
        "knowledgeUnits": len(result.knowledge_unit_ids),
        "selectedExperts": list(result.selected_experts),
        "creativeDirections": list(result.creative_direction_ids),
        "executors": list(result.executor_classes),
        "verifier": result.verifier_class,
        "qcStatus": result.qc_status,
        "provenanceId": result.provenance_id,
        "blockers": list(result.blockers),
        "warnings": list(result.warnings),
        "humanReviewRequired": result.human_review_required,
        "generatedFiles": files,
        "imageModel": image_model,
        "visionModel": vision_model,
        "verifierRoleIndependent": True,
        "crossProviderVerification": False,
    }
    (output_root / "result.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))

    # Integration succeeded if generation, verification and provenance all ran.
    if not result.executor_classes:
        return 10
    if result.verifier_class is None:
        return 11
    if result.provenance_id is None:
        return 12
    if not files:
        return 13
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
