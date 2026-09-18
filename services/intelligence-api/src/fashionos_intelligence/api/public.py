from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException, Request

from fashionos_intelligence.domain.models import (
    CreateTaskRequest,
    PublicTaskEnvelope,
    PublicTaskResponse,
    ResponseMeta,
)
from fashionos_intelligence.persistence.tasks import TaskRepository
from fashionos_intelligence.services.orchestrator import OrchestratorService

router = APIRouter(prefix="/api/v1", tags=["public"])


def _meta(correlation_id: str | None = None) -> ResponseMeta:
    return ResponseMeta(
        requestId=f"req_{uuid4().hex[:16]}",
        correlationId=correlation_id or f"cor_{uuid4().hex[:16]}",
    )


def _repo(request: Request) -> TaskRepository:
    return request.app.state.task_repository


@router.post(
    "/tasks",
    response_model=PublicTaskEnvelope,
    response_model_by_alias=True,
)
def create_task(
    payload: CreateTaskRequest,
    request: Request,
    x_correlation_id: str | None = Header(default=None),
) -> PublicTaskEnvelope:
    orchestrator = OrchestratorService(_repo(request))
    result = orchestrator.create_task(payload)
    return PublicTaskEnvelope(
        data=result,
        meta=_meta(x_correlation_id),
    )


@router.get(
    "/tasks/{task_id}",
    response_model=PublicTaskEnvelope,
    response_model_by_alias=True,
)
def get_task(
    task_id: str,
    request: Request,
    x_correlation_id: str | None = Header(default=None),
) -> PublicTaskEnvelope:
    stored = _repo(request).get(task_id)
    if stored is None:
        raise HTTPException(status_code=404, detail="TASK_NOT_FOUND")
    public_status = "working" if stored.status != "COMPLETED" else "ready"
    return PublicTaskEnvelope(
        data=PublicTaskResponse(
            taskId=stored.task_id,
            status=public_status,
            next="validating" if stored.status == "CREATED" else None,
        ),
        meta=_meta(x_correlation_id),
    )
