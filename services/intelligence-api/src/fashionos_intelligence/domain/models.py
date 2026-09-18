from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from .enums import PublicJobStatus, TaskMode


class Locks(BaseModel):
    hard: list[str] = Field(default_factory=list)
    soft: list[str] = Field(default_factory=list)


class TargetSpec(BaseModel):
    type: str = "image"
    aspect_ratio: str | None = Field(default=None, alias="aspectRatio")
    platform: str | None = None

    model_config = {"populate_by_name": True}


class CreateTaskRequest(BaseModel):
    workspace_id: str = Field(alias="workspaceId")
    objective: str = Field(min_length=1)
    mode: TaskMode
    source_asset_ids: list[str] = Field(default_factory=list, alias="sourceAssetIds")
    reference_asset_ids: list[str] = Field(default_factory=list, alias="referenceAssetIds")
    locks: Locks = Field(default_factory=Locks)
    allowed_changes: list[str] = Field(default_factory=list, alias="allowedChanges")
    target: TargetSpec = Field(default_factory=TargetSpec)

    model_config = {"populate_by_name": True}


class PublicTaskResponse(BaseModel):
    task_id: str = Field(alias="taskId")
    status: PublicJobStatus
    next: str | None = None

    model_config = {"populate_by_name": True}


class BrainRetrieveRequest(BaseModel):
    task_id: str = Field(alias="taskId")
    mode: TaskMode
    source_roles: list[str] = Field(default_factory=list, alias="sourceRoles")
    reality_class: str | None = Field(default=None, alias="realityClass")
    required_capabilities: list[str] = Field(default_factory=list, alias="requiredCapabilities")

    model_config = {"populate_by_name": True}


class KnowledgeUnitOut(BaseModel):
    unit_id: str = Field(alias="unitId")
    domain: str
    section: str
    authority: int
    text: str

    model_config = {"populate_by_name": True}


class BrainRetrieveResponse(BaseModel):
    brain_revision: str = Field(alias="brainRevision")
    domains: list[str]
    rules: list[KnowledgeUnitOut]
    conflicts: list[dict[str, Any]] = Field(default_factory=list)

    model_config = {"populate_by_name": True}
