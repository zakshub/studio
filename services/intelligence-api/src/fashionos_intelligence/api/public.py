from uuid import uuid4

from fastapi import APIRouter, Depends, Header, Request

from fashionos_intelligence.domain.models import (
    CreateTaskRequest,
    PublicTaskEnvelope,
    ResponseMeta,
)
from fashionos_intelligence.services.orchestrator import OrchestratorService

router = APIRouter(prefix="/api/v1", tags=["public"])


def get_orchestrator() -> OrchestratorService:
    return OrchestratorService()


@router.post(
    "/tasks",
    response_model=PublicTaskEnvelope,
    response_model_by_alias=True,
)
def create_task(
    payload: CreateTaskRequest,
    request: Request,
    x_correlation_id: str | None = Header(default=None),
    orchestrator: OrchestratorService = Depends(get_orchestrator),
) -> PublicTaskEnvelope:
    result = orchestrator.create_task(payload)
    return PublicTaskEnvelope(
        data=result,
        meta=ResponseMeta(
            requestId=f"req_{uuid4().hex[:16]}",
            correlationId=x_correlation_id or f"cor_{uuid4().hex[:16]}",
        ),
    )
