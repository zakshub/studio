from contextlib import asynccontextmanager

from fastapi import FastAPI

from fashionos_intelligence.api.internal import router as internal_router
from fashionos_intelligence.api.public import router as public_router
from fashionos_intelligence.persistence.db import build_session_factory
from fashionos_intelligence.persistence.tasks import TaskRepository
from fashionos_intelligence.services.brain import BrainIndex
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
    yield


app = FastAPI(
    title="FashionOS Intelligence API",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(public_router)
app.include_router(internal_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
