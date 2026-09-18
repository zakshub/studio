import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from fashionos_intelligence.domain.models import (
    BrainRetrieveRequest,
    BrainRetrieveResponse,
    CognitionRequest,
    CognitionResponse,
    KnowledgeUnitOut,
    LearningCandidateCreate,
    LearningCandidateOut,
    LearningPromotionRequest,
    MemoryCreateRequest,
    MemoryOut,
    PracticePlanOut,
    PracticeRequest,
    SensorySourceCreate,
    SensorySourceOut,
)
from fashionos_intelligence.services.brain import BrainIndex
from fashionos_intelligence.services.cognition import CognitionService
from fashionos_intelligence.services.learning import LearningService
from fashionos_intelligence.services.memory import MemoryService
from fashionos_intelligence.services.practice import PracticeService
from fashionos_intelligence.services.sensory import SensoryRegistry
from fashionos_intelligence.settings import Settings

router = APIRouter(prefix="/internal/v1", tags=["internal"])


def require_internal_access(
    request: Request,
    x_internal_token: str | None = Header(default=None),
) -> None:
    settings: Settings = request.app.state.settings
    expected = settings.internal_token
    if not expected:
        raise HTTPException(status_code=503, detail="INTERNAL_AUTH_NOT_CONFIGURED")
    if not x_internal_token or not hmac.compare_digest(x_internal_token, expected):
        raise HTTPException(status_code=403, detail="INTERNAL_ENDPOINT_FORBIDDEN")


def get_brain(request: Request) -> BrainIndex:
    brain = getattr(request.app.state, "brain", None)
    if brain is None:
        raise HTTPException(status_code=503, detail="BRAIN_UNAVAILABLE")
    return brain


@router.get("/brain/health", dependencies=[Depends(require_internal_access)])
def brain_health(brain: BrainIndex = Depends(get_brain)) -> dict[str, object]:
    return brain.health()


@router.post("/brain/sync", dependencies=[Depends(require_internal_access)])
def brain_sync(brain: BrainIndex = Depends(get_brain)) -> dict[str, object]:
    brain.sync_local()
    return brain.health()


@router.post(
    "/brain/retrieve",
    response_model=BrainRetrieveResponse,
    response_model_by_alias=True,
    dependencies=[Depends(require_internal_access)],
)
def retrieve_brain(
    payload: BrainRetrieveRequest,
    brain: BrainIndex = Depends(get_brain),
) -> BrainRetrieveResponse:
    units = brain.retrieve(payload)
    return BrainRetrieveResponse(
        brainRevision=brain.revision,
        domains=sorted({u.domain for u in units}),
        rules=[
            KnowledgeUnitOut(
                unitId=u.unit_id,
                domain=u.domain,
                section=u.section,
                authority=u.authority,
                text=u.text,
            )
            for u in units
        ],
        conflicts=[],
    )


def get_cognition(request: Request) -> CognitionService:
    return request.app.state.cognition_service


def get_learning(request: Request) -> LearningService:
    return request.app.state.learning_service


def get_memory(request: Request) -> MemoryService:
    return request.app.state.memory_service


def get_practice(request: Request) -> PracticeService:
    return request.app.state.practice_service


def get_sensory(request: Request) -> SensoryRegistry:
    return request.app.state.sensory_registry


@router.post(
    "/cognition/plan",
    response_model=CognitionResponse,
    response_model_by_alias=True,
    dependencies=[Depends(require_internal_access)],
)
def cognition_plan(
    payload: CognitionRequest,
    service: CognitionService = Depends(get_cognition),
) -> CognitionResponse:
    plan = service.plan(
        mode=payload.mode,
        capabilities=payload.capabilities,
        rights_statuses=payload.rights_statuses,
        hard_locks=payload.hard_locks,
        requested_changes=payload.requested_changes,
        preservation_required=payload.preservation_required,
        evidence_count=payload.evidence_count,
        independent_source_count=payload.independent_source_count,
        contradiction_count=payload.contradiction_count,
        unknown_count=payload.unknown_count,
        high_risk=payload.high_risk,
    )
    return CognitionResponse(
        stages=list(plan.stages),
        councils=list(plan.councils),
        valueAllowed=plan.value_allowed,
        blockers=list(plan.blockers),
        warnings=list(plan.warnings),
        confidence=plan.confidence,
        metacognitiveFlags=list(plan.metacognitive_flags),
        researchQuestions=list(plan.research_questions),
        humanReviewRequired=plan.human_review_required,
    )


@router.post(
    "/learning/candidates",
    response_model=LearningCandidateOut,
    response_model_by_alias=True,
    dependencies=[Depends(require_internal_access)],
)
def create_learning_candidate(
    payload: LearningCandidateCreate,
    service: LearningService = Depends(get_learning),
) -> LearningCandidateOut:
    candidate = service.create(
        observation=payload.observation,
        proposed_principle=payload.proposed_principle,
        scope=payload.scope,
        evidence_ids=payload.evidence_ids,
        confidence=payload.confidence,
    )
    return LearningCandidateOut(
        candidateId=candidate.candidate_id,
        observation=candidate.observation,
        proposedPrinciple=candidate.proposed_principle,
        scope=candidate.scope,
        evidenceIds=candidate.evidence_ids,
        confidence=candidate.confidence,
        decisionStatus=candidate.decision_status,
        createdAt=candidate.created_at,
        decidedAt=candidate.decided_at,
    )


@router.post(
    "/learning/candidates/{candidate_id}/promote",
    response_model=LearningCandidateOut,
    response_model_by_alias=True,
    dependencies=[Depends(require_internal_access)],
)
def promote_learning_candidate(
    candidate_id: str,
    payload: LearningPromotionRequest,
    service: LearningService = Depends(get_learning),
) -> LearningCandidateOut:
    try:
        candidate = service.promote(
            candidate_id,
            human_approved=payload.human_approved,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return LearningCandidateOut(
        candidateId=candidate.candidate_id,
        observation=candidate.observation,
        proposedPrinciple=candidate.proposed_principle,
        scope=candidate.scope,
        evidenceIds=candidate.evidence_ids,
        confidence=candidate.confidence,
        decisionStatus=candidate.decision_status,
        createdAt=candidate.created_at,
        decidedAt=candidate.decided_at,
    )


@router.post(
    "/practice/plan",
    response_model=PracticePlanOut,
    response_model_by_alias=True,
    dependencies=[Depends(require_internal_access)],
)
def practice_plan(
    payload: PracticeRequest,
    service: PracticeService = Depends(get_practice),
) -> PracticePlanOut:
    plan = service.plan(
        target_principle=payload.target_principle,
        mode=payload.mode,
        fixed_variables=payload.fixed_variables,
        controlled_variables=payload.controlled_variables,
        candidate_count=payload.candidate_count,
    )
    return PracticePlanOut(
        sessionId=plan.session_id,
        targetPrinciple=plan.target_principle,
        mode=plan.mode,
        fixedVariables=list(plan.fixed_variables),
        controlledVariables=list(plan.controlled_variables),
        candidateCount=plan.candidate_count,
        evaluationDimensions=list(plan.evaluation_dimensions),
        publicAsset=plan.public_asset,
    )


@router.post(
    "/memory",
    response_model=MemoryOut,
    response_model_by_alias=True,
    dependencies=[Depends(require_internal_access)],
)
def create_memory(
    payload: MemoryCreateRequest,
    service: MemoryService = Depends(get_memory),
) -> MemoryOut:
    record = service.remember(
        memory_type=payload.memory_type,
        scope=payload.scope,
        content=payload.content,
        evidence_ids=payload.evidence_ids,
        weight=payload.weight,
    )
    return MemoryOut(
        memoryId=record.memory_id,
        memoryType=record.memory_type,
        scope=record.scope,
        content=record.content,
        evidenceIds=record.evidence_ids,
        status=record.status,
        weight=record.weight,
        createdAt=record.created_at,
        updatedAt=record.updated_at,
    )


@router.post(
    "/sensory/sources",
    response_model=SensorySourceOut,
    response_model_by_alias=True,
    dependencies=[Depends(require_internal_access)],
)
def register_sensory_source(
    payload: SensorySourceCreate,
    service: SensoryRegistry = Depends(get_sensory),
) -> SensorySourceOut:
    source = service.register(
        url=payload.url,
        source_class=payload.source_class,
        authority=payload.authority,
        rights_status=payload.rights_status,
    )
    return SensorySourceOut(
        sourceId=source.source_id,
        url=source.url,
        sourceClass=source.source_class,
        authority=source.authority,
        rightsStatus=source.rights_status,
        lastFingerprint=source.last_fingerprint,
    )
