from contextlib import asynccontextmanager

from fastapi import FastAPI

from fashionos_intelligence.api.internal import router as internal_router
from fashionos_intelligence.api.public import router as public_router
from fashionos_intelligence.persistence.db import build_session_factory
from fashionos_intelligence.persistence.benchmarks import BenchmarkRepository
from fashionos_intelligence.persistence.cognition_records import (
    DecisionRepository,
    ObservationRepository,
    PracticeRepository,
)
from fashionos_intelligence.persistence.learning import LearningRepository
from fashionos_intelligence.persistence.memory import MemoryRepository
from fashionos_intelligence.persistence.runtime_records import (
    ExecutionRepository,
    ProvenanceRepository,
    QCRepository,
)
from fashionos_intelligence.persistence.tasks import TaskRepository
from fashionos_intelligence.services.attention import AttentionService
from fashionos_intelligence.services.background_synthesis import BackgroundSynthesisService
from fashionos_intelligence.services.benchmarks import BenchmarkService
from fashionos_intelligence.services.brain import BrainIndex
from fashionos_intelligence.services.brain_snapshots import BrainSnapshotStore
from fashionos_intelligence.services.cognition import CognitionService
from fashionos_intelligence.services.contamination import ContaminationMonitor
from fashionos_intelligence.services.creative_synthesis import CreativeSynthesisService
from fashionos_intelligence.services.decision_records import DecisionRecordService
from fashionos_intelligence.services.curiosity import CuriosityService
from fashionos_intelligence.services.failure_learning import FailureLearningService
from fashionos_intelligence.services.expert_profiles import ExpertProfileLoader
from fashionos_intelligence.services.expert_intelligence import ExpertIntelligenceService
from fashionos_intelligence.services.executors import ExecutorGateway
from fashionos_intelligence.services.live_gemini import (
    GeminiImageTransport,
    GeminiVisionQCTransport,
)
from fashionos_intelligence.services.live_openai import (
    OpenAIImageGenerationTransport,
    OpenAIVisionQCTransport,
)
from fashionos_intelligence.services.provider_adapters import (
    CrossProviderVerifierAdapter,
    GeminiExecutorAdapter,
    OpenAIExecutorAdapter,
    ProviderExecutorAdapter,
)
from fashionos_intelligence.services.learning import LearningService
from fashionos_intelligence.services.memory import MemoryService
from fashionos_intelligence.services.novelty import NoveltyService
from fashionos_intelligence.services.observations import ObservationService
from fashionos_intelligence.services.organism_loop import CreativeOrganismLoop
from fashionos_intelligence.services.practice import PracticeService
from fashionos_intelligence.services.provenance import ProvenanceService
from fashionos_intelligence.services.qc_runtime import QCRuntime
from fashionos_intelligence.services.remote_brain import (
    GitHubRepositoryTransport,
    RemoteBrainRefresher,
)
from fashionos_intelligence.services.sensory import SensoryRegistry
from fashionos_intelligence.services.storage import LocalContentAddressedStore
from fashionos_intelligence.settings import Settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings.from_env()
    brain_root = settings.brain_root
    if settings.brain_remote_repo and settings.brain_remote_mirror_root:
        owner, repository = settings.brain_remote_repo.split("/", 1)
        refresher = RemoteBrainRefresher(
            settings.brain_remote_mirror_root,
            GitHubRepositoryTransport(
                owner=owner,
                repository=repository,
                ref=settings.brain_remote_ref,
                token=settings.github_token,
            ),
        )
        try:
            brain_root = refresher.refresh()
        except Exception:
            current = refresher.current()
            if current is None:
                raise
            brain_root = current

    brain = BrainIndex(
        brain_root,
        stale_after_seconds=settings.stale_after_seconds,
        snapshot_store=BrainSnapshotStore(settings.brain_snapshot_root),
    )
    brain.sync_local()
    sessions = build_session_factory(settings.database_url)
    app.state.settings = settings
    app.state.brain = brain
    app.state.task_repository = TaskRepository(sessions)
    app.state.cognition_service = CognitionService()
    app.state.learning_service = LearningService(LearningRepository(sessions))
    app.state.memory_service = MemoryService(MemoryRepository(sessions))
    app.state.practice_service = PracticeService(PracticeRepository(sessions))
    app.state.sensory_registry = SensoryRegistry()
    app.state.novelty_service = NoveltyService()
    app.state.contamination_monitor = ContaminationMonitor()
    app.state.background_synthesis_service = BackgroundSynthesisService()
    app.state.failure_learning_service = FailureLearningService()
    app.state.creative_synthesis_service = CreativeSynthesisService()
    app.state.attention_service = AttentionService()
    app.state.curiosity_service = CuriosityService()
    app.state.observation_service = ObservationService(ObservationRepository(sessions))
    app.state.decision_record_service = DecisionRecordService(DecisionRepository(sessions))
    expert_profiles = ExpertProfileLoader(
        brain_root / "expert-intelligence" / "profiles"
    ).load_all()
    app.state.expert_intelligence_service = ExpertIntelligenceService(expert_profiles)
    app.state.benchmark_service = BenchmarkService(BenchmarkRepository(sessions))

    executor_gateway = ExecutorGateway()
    verifier_candidates: list[ProviderExecutorAdapter] = []
    asset_store = None

    if settings.openai_api_key or settings.gemini_api_key:
        asset_store = LocalContentAddressedStore(
            settings.generated_asset_root
            or (brain_root / ".fashionos-cache" / "generated-assets")
        )
        app.state.generated_asset_store = asset_store

    if settings.openai_api_key and asset_store is not None:
        executor_gateway.register(
            OpenAIExecutorAdapter(
                name="openai-image",
                capabilities={"image_generation", "image_edit"},
                provider="openai",
                transport=OpenAIImageGenerationTransport(
                    api_key=settings.openai_api_key,
                    store=asset_store,
                    model=settings.openai_image_model,
                    edit_model=settings.openai_image_edit_model,
                ),
            )
        )
        verifier_candidates.append(
            ProviderExecutorAdapter(
                name="openai-vision-qc",
                capabilities={"vision_qc"},
                provider="openai",
                transport=OpenAIVisionQCTransport(
                    api_key=settings.openai_api_key,
                    store=asset_store,
                    model=settings.openai_vision_model,
                ),
            )
        )

    if settings.gemini_api_key and asset_store is not None:
        executor_gateway.register(
            GeminiExecutorAdapter(
                name="gemini-image",
                capabilities={"image_generation", "image_edit"},
                provider="gemini",
                transport=GeminiImageTransport(
                    api_key=settings.gemini_api_key,
                    store=asset_store,
                    model=settings.gemini_image_model,
                ),
            )
        )
        verifier_candidates.append(
            ProviderExecutorAdapter(
                name="gemini-vision-qc",
                capabilities={"vision_qc"},
                provider="gemini",
                transport=GeminiVisionQCTransport(
                    api_key=settings.gemini_api_key,
                    store=asset_store,
                    model=settings.gemini_vision_model,
                ),
            )
        )

    visual_verifier = (
        CrossProviderVerifierAdapter(tuple(verifier_candidates))
        if verifier_candidates
        else None
    )

    app.state.executor_gateway = executor_gateway
    app.state.visual_verifier = visual_verifier
    app.state.qc_runtime = QCRuntime()
    app.state.provenance_service = ProvenanceService(ProvenanceRepository(sessions))
    app.state.organism_loop = CreativeOrganismLoop(
        brain=brain,
        cognition=app.state.cognition_service,
        experts=app.state.expert_intelligence_service,
        creativity=app.state.creative_synthesis_service,
        benchmarks=app.state.benchmark_service,
        executors=app.state.executor_gateway,
        qc=app.state.qc_runtime,
        provenance=app.state.provenance_service,
        memory=app.state.memory_service,
        learning=app.state.learning_service,
        execution_repository=ExecutionRepository(sessions),
        qc_repository=QCRepository(sessions),
        visual_verifier=visual_verifier,
    )
    yield


app = FastAPI(
    title="FashionOS Intelligence API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.include_router(public_router)
app.include_router(internal_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
