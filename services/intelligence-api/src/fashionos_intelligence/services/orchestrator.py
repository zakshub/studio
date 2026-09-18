from __future__ import annotations

from uuid import uuid4

from fashionos_intelligence.domain.enums import PublicJobStatus
from fashionos_intelligence.domain.models import CreateTaskRequest, PublicTaskResponse
from fashionos_intelligence.persistence.tasks import TaskRepository


class OrchestratorService:
    def __init__(self, tasks: TaskRepository):
        self.tasks = tasks

    def create_task(self, request: CreateTaskRequest) -> PublicTaskResponse:
        task_id = f"task_{uuid4().hex[:16]}"
        self.tasks.create(
            task_id=task_id,
            workspace_id=request.workspace_id,
            objective=request.objective,
            mode=request.mode.value,
            status="CREATED",
        )
        return PublicTaskResponse(
            taskId=task_id,
            status=PublicJobStatus.QUEUED,
            next="validating",
        )
