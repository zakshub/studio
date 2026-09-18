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


class ResponseMeta(BaseModel):
    request_id: str = Field(alias="requestId")
    correlation_id: str = Field(alias="correlationId")

    model_config = {"populate_by_name": True}


class PublicTaskEnvelope(BaseModel):
    data: PublicTaskResponse
    meta: ResponseMeta
    error: None = None


class CognitionRequest(BaseModel):
    mode: str
    capabilities: list[str] = Field(default_factory=list)
    rights_statuses: list[str] = Field(default_factory=list, alias="rightsStatuses")
    hard_locks: list[str] = Field(default_factory=list, alias="hardLocks")
    requested_changes: list[str] = Field(default_factory=list, alias="requestedChanges")
    preservation_required: bool = Field(default=False, alias="preservationRequired")
    evidence_count: int = Field(default=0, alias="evidenceCount", ge=0)
    independent_source_count: int = Field(default=0, alias="independentSourceCount", ge=0)
    contradiction_count: int = Field(default=0, alias="contradictionCount", ge=0)
    unknown_count: int = Field(default=0, alias="unknownCount", ge=0)
    high_risk: bool = Field(default=False, alias="highRisk")

    model_config = {"populate_by_name": True}


class CognitionResponse(BaseModel):
    stages: list[str]
    councils: list[str]
    value_allowed: bool = Field(alias="valueAllowed")
    blockers: list[str]
    warnings: list[str]
    confidence: str
    metacognitive_flags: list[str] = Field(alias="metacognitiveFlags")
    research_questions: list[str] = Field(alias="researchQuestions")
    human_review_required: bool = Field(alias="humanReviewRequired")

    model_config = {"populate_by_name": True}


class LearningCandidateCreate(BaseModel):
    observation: str = Field(min_length=1)
    proposed_principle: str = Field(alias="proposedPrinciple", min_length=1)
    scope: str
    evidence_ids: list[str] = Field(default_factory=list, alias="evidenceIds")
    confidence: str

    model_config = {"populate_by_name": True}


class LearningCandidateOut(BaseModel):
    candidate_id: str = Field(alias="candidateId")
    observation: str
    proposed_principle: str = Field(alias="proposedPrinciple")
    scope: str
    evidence_ids: list[str] = Field(alias="evidenceIds")
    confidence: str
    decision_status: str = Field(alias="decisionStatus")
    created_at: str = Field(alias="createdAt")
    decided_at: str | None = Field(default=None, alias="decidedAt")

    model_config = {"populate_by_name": True}


class LearningPromotionRequest(BaseModel):
    human_approved: bool = Field(alias="humanApproved")

    model_config = {"populate_by_name": True}


class PracticeRequest(BaseModel):
    target_principle: str = Field(alias="targetPrinciple", min_length=1)
    mode: str
    fixed_variables: list[str] = Field(default_factory=list, alias="fixedVariables")
    controlled_variables: list[str] = Field(default_factory=list, alias="controlledVariables")
    candidate_count: int = Field(default=3, alias="candidateCount", ge=2, le=12)

    model_config = {"populate_by_name": True}


class PracticePlanOut(BaseModel):
    session_id: str = Field(alias="sessionId")
    target_principle: str = Field(alias="targetPrinciple")
    mode: str
    fixed_variables: list[str] = Field(alias="fixedVariables")
    controlled_variables: list[str] = Field(alias="controlledVariables")
    candidate_count: int = Field(alias="candidateCount")
    evaluation_dimensions: list[str] = Field(alias="evaluationDimensions")
    public_asset: bool = Field(alias="publicAsset")

    model_config = {"populate_by_name": True}


class MemoryCreateRequest(BaseModel):
    memory_type: str = Field(alias="memoryType")
    scope: str
    content: str = Field(min_length=1)
    evidence_ids: list[str] = Field(default_factory=list, alias="evidenceIds")
    weight: float = Field(default=1.0, ge=0.0, le=1.0)

    model_config = {"populate_by_name": True}


class MemoryOut(BaseModel):
    memory_id: str = Field(alias="memoryId")
    memory_type: str = Field(alias="memoryType")
    scope: str
    content: str
    evidence_ids: list[str] = Field(alias="evidenceIds")
    status: str
    weight: float
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class SensorySourceCreate(BaseModel):
    url: str
    source_class: str = Field(alias="sourceClass")
    authority: str
    rights_status: str = Field(alias="rightsStatus")

    model_config = {"populate_by_name": True}


class SensorySourceOut(BaseModel):
    source_id: str = Field(alias="sourceId")
    url: str
    source_class: str = Field(alias="sourceClass")
    authority: str
    rights_status: str = Field(alias="rightsStatus")
    last_fingerprint: str | None = Field(default=None, alias="lastFingerprint")

    model_config = {"populate_by_name": True}
