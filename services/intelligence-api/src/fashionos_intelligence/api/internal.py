import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from fashionos_intelligence.domain.models import (
    AttentionItemOut,
    AttentionRequest,
    BackgroundSynthesisItem,
    BackgroundSynthesisRequest,
    BrainRetrieveRequest,
    BrainRetrieveResponse,
    CognitionRequest,
    CognitionResponse,
    ContaminationRequest,
    ContaminationResponse,
    CreativeDirectionOut,
    CreativeSynthesisRequest,
    FailureLearningRequest,
    FailureLearningResponse,
    KnowledgeUnitOut,
    LearningCandidateCreate,
    LearningCandidateOut,
    LearningPromotionRequest,
    MemoryCreateRequest,
    MemoryOut,
    PracticePlanOut,
    PracticeRequest,
    NoveltyRequest,
    NoveltyResponse,
    CuriosityRequest,
    ResearchQuestionOut,
    SensorySourceCreate,
    SensorySourceOut,
)
from fashionos_intelligence.services.attention import AttentionService
from fashionos_intelligence.services.background_synthesis import BackgroundSynthesisService
from fashionos_intelligence.services.brain import BrainIndex
from fashionos_intelligence.services.cognition import CognitionService
from fashionos_intelligence.services.contamination import ContaminationMonitor
from fashionos_intelligence.services.creative_synthesis import CreativeSynthesisService
from fashionos_intelligence.services.curiosity import CuriosityService
from fashionos_intelligence.services.failure_learning import FailureLearningService
from fashionos_intelligence.services.learning import LearningService
from fashionos_intelligence.services.memory import MemoryService
from fashionos_intelligence.services.novelty import NoveltyService
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


def get_novelty(request: Request) -> NoveltyService:
    return request.app.state.novelty_service


def get_contamination(request: Request) -> ContaminationMonitor:
    return request.app.state.contamination_monitor


def get_background_synthesis(request: Request) -> BackgroundSynthesisService:
    return request.app.state.background_synthesis_service


def get_failure_learning(request: Request) -> FailureLearningService:
    return request.app.state.failure_learning_service


def get_creative_synthesis(request: Request) -> CreativeSynthesisService:
    return request.app.state.creative_synthesis_service


@router.post(
    "/novelty/evaluate",
    response_model=NoveltyResponse,
    response_model_by_alias=True,
    dependencies=[Depends(require_internal_access)],
)
def evaluate_novelty(
    payload: NoveltyRequest,
    service: NoveltyService = Depends(get_novelty),
) -> NoveltyResponse:
    result = service.evaluate(payload.candidate, payload.references)
    return NoveltyResponse(
        score=result.score,
        nearestSimilarity=result.nearest_similarity,
        label=result.label,
    )


@router.post(
    "/contamination/check",
    response_model=ContaminationResponse,
    response_model_by_alias=True,
    dependencies=[Depends(require_internal_access)],
)
def check_contamination(
    payload: ContaminationRequest,
    service: ContaminationMonitor = Depends(get_contamination),
) -> ContaminationResponse:
    result = service.evaluate(
        payload.origins,
        dominance_threshold=payload.dominance_threshold,
        minimum_sample=payload.minimum_sample,
    )
    return ContaminationResponse(
        dominantGroup=result.dominant_group,
        dominantShare=result.dominant_share,
        flags=list(result.flags),
        promotionBlocked=result.promotion_blocked,
    )


@router.post(
    "/background/synthesize",
    response_model=list[BackgroundSynthesisItem],
    response_model_by_alias=True,
    dependencies=[Depends(require_internal_access)],
)
def background_synthesize(
    payload: BackgroundSynthesisRequest,
    service: BackgroundSynthesisService = Depends(get_background_synthesis),
) -> list[BackgroundSynthesisItem]:
    results = service.synthesize(
        payload.observations,
        minimum_repeat=payload.minimum_repeat,
    )
    return [
        BackgroundSynthesisItem(
            clusterKey=item.cluster_key,
            evidenceCount=item.evidence_count,
            observations=list(item.observations),
            proposedAction=item.proposed_action,
        )
        for item in results
    ]


@router.post(
    "/failure/analyze",
    response_model=FailureLearningResponse,
    response_model_by_alias=True,
    dependencies=[Depends(require_internal_access)],
)
def analyze_failure(
    payload: FailureLearningRequest,
    service: FailureLearningService = Depends(get_failure_learning),
) -> FailureLearningResponse:
    result = service.analyze(
        payload.failure_code,
        recurrence_count=payload.recurrence_count,
    )
    return FailureLearningResponse(
        failureCode=result.failure_code,
        likelyCategory=result.likely_category,
        remediationQuestions=list(result.remediation_questions),
        createLearningCandidate=result.create_learning_candidate,
    )


@router.post(
    "/creative/diverge",
    response_model=list[CreativeDirectionOut],
    response_model_by_alias=True,
    dependencies=[Depends(require_internal_access)],
)
def creative_diverge(
    payload: CreativeSynthesisRequest,
    service: CreativeSynthesisService = Depends(get_creative_synthesis),
) -> list[CreativeDirectionOut]:
    directions = service.diverge(
        principles=payload.principles,
        councils=payload.councils,
        max_directions=payload.max_directions,
    )
    return [
        CreativeDirectionOut(
            directionId=item.direction_id,
            principles=list(item.principles),
            tension=item.tension,
            councils=list(item.councils),
        )
        for item in directions
    ]


def get_attention(request: Request) -> AttentionService:
    return request.app.state.attention_service


def get_curiosity(request: Request) -> CuriosityService:
    return request.app.state.curiosity_service


@router.post(
    "/attention/rank",
    response_model=list[AttentionItemOut],
    response_model_by_alias=True,
    dependencies=[Depends(require_internal_access)],
)
def rank_attention(
    payload: AttentionRequest,
    service: AttentionService = Depends(get_attention),
) -> list[AttentionItemOut]:
    items = [
        {
            "item_id": item.item_id,
            "relevance": item.relevance,
            "risk": item.risk,
            "uncertainty": item.uncertainty,
            "novelty": item.novelty,
            "user_priority": item.user_priority,
            "cost": item.cost,
        }
        for item in payload.items
    ]
    ranked = service.rank(items)
    return [
        AttentionItemOut(
            itemId=item.item_id,
            score=item.score,
            reasons=list(item.reasons),
        )
        for item in ranked
    ]


@router.post(
    "/curiosity/questions",
    response_model=list[ResearchQuestionOut],
    response_model_by_alias=True,
    dependencies=[Depends(require_internal_access)],
)
def generate_curiosity_questions(
    payload: CuriosityRequest,
    service: CuriosityService = Depends(get_curiosity),
) -> list[ResearchQuestionOut]:
    questions = service.generate(
        repeated_uncertainties=payload.repeated_uncertainties,
        recurring_failures=payload.recurring_failures,
        contradictions=payload.contradictions,
        coverage_gaps=payload.coverage_gaps,
        affected_domains=payload.affected_domains,
    )
    return [
        ResearchQuestionOut(
            questionId=item.question_id,
            question=item.question,
            reason=item.reason,
            affectedDomains=list(item.affected_domains),
            urgency=item.urgency,
            evidenceNeeded=list(item.evidence_needed),
        )
        for item in questions
    ]

@router.get("/brain/revisions", dependencies=[Depends(require_internal_access)])
def brain_revisions(brain: BrainIndex = Depends(get_brain)) -> dict[str, object]:
    return {
        "activeRevision": brain.revision,
        "availableRevisions": list(brain.available_revisions()),
    }


@router.post("/brain/rollback/{revision}", dependencies=[Depends(require_internal_access)])
def brain_rollback(
    revision: str,
    brain: BrainIndex = Depends(get_brain),
) -> dict[str, object]:
    try:
        active = brain.rollback(revision)
    except KeyError:
        raise HTTPException(status_code=404, detail="BRAIN_REVISION_NOT_FOUND")
    return {
        "activeRevision": active,
        "state": brain.health()["state"],
    }
