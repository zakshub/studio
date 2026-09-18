from __future__ import annotations

from uuid import uuid4

from fashionos_intelligence.domain.models import CreateTaskRequest, PublicTaskResponse
from fashionos_intelligence.domain.enums import PublicJobStatus


class OrchestratorService:
    def create_task(self, request: CreateTaskRequest) -> PublicTaskResponse:
        # MVP contract stub. Persistence and async queue are added in later tasks.
        task_id = f"task_{uuid4().hex[:16]}"
        return PublicTaskResponse(
            taskId=task_id,
            status=PublicJobStatus.QUEUED,
            next="validating",
        )
