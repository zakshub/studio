from __future__ import annotations

from dataclasses import dataclass
from sqlalchemy.orm import Session, sessionmaker

from fashionos_intelligence.persistence.db import TaskRow


@dataclass(frozen=True)
class StoredTask:
    task_id: str
    workspace_id: str
    objective: str
    mode: str
    status: str


class TaskRepository:
    def __init__(self, sessions: sessionmaker[Session]):
        self.sessions = sessions

    def create(
        self,
        *,
        task_id: str,
        workspace_id: str,
        objective: str,
        mode: str,
        status: str,
    ) -> StoredTask:
        row = TaskRow(
            task_id=task_id,
            workspace_id=workspace_id,
            objective=objective,
            mode=mode,
            status=status,
        )
        with self.sessions() as session:
            session.add(row)
            session.commit()
        return StoredTask(task_id, workspace_id, objective, mode, status)

    def get(self, task_id: str) -> StoredTask | None:
        with self.sessions() as session:
            row = session.get(TaskRow, task_id)
            if row is None:
                return None
            return StoredTask(
                row.task_id,
                row.workspace_id,
                row.objective,
                row.mode,
                row.status,
            )
