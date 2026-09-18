from contextlib import asynccontextmanager

from fastapi import FastAPI

from fashionos_intelligence.api.internal import router as internal_router
from fashionos_intelligence.api.public import router as public_router
from fashionos_intelligence.persistence.db import build_session_factory
from fashionos_intelligence.persistence.tasks import TaskRepository
from fashionos_intelligence.services.brain import BrainIndex
from fashionos_intelligence.services.cognition import CognitionService
from fashionos_intelligence.services.learning import LearningService
from fashionos_intelligence.services.memory import MemoryService
from fashionos_intelligence.services.practice import PracticeService
from fashionos_intelligence.services.sensory import SensoryRegistry
from fashionos_intelligence.settings import Settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings.from_env()
    brain = BrainIndex(
        settings.brain_root,
        stale_after_seconds=settings.stale_after_seconds,
    )
    brain.sync_local()
    sessions = build_session_factory(settings.database_url)
    app.state.settings = settings
    app.state.brain = brain
    app.state.task_repository = TaskRepository(sessions)
    app.state.cognition_service = CognitionService()
    app.state.learning_service = LearningService()
    app.state.memory_service = MemoryService()
    app.state.practice_service = PracticeService()
    app.state.sensory_registry = SensoryRegistry()
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