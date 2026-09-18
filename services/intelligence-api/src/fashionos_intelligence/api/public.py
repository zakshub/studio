from fastapi import APIRouter, Depends

from fashionos_intelligence.domain.models import CreateTaskRequest, PublicTaskResponse
from fashionos_intelligence.services.orchestrator import OrchestratorService

router = APIRouter(prefix="/api/v1", tags=["public"])


def get_orchestrator() -> OrchestratorService:
    return OrchestratorService()


@router.post(
    "/tasks",
    response_model=PublicTaskResponse,
    response_model_by_alias=True,
)
def create_task(
    payload: CreateTaskRequest,
    orchestrator: OrchestratorService = Depends(get_orchestrator),
) -> PublicTaskResponse:
    return orchestrator.create_task(payload)
