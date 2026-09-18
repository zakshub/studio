import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from fashionos_intelligence.domain.models import (
    BrainRetrieveRequest,
    BrainRetrieveResponse,
    KnowledgeUnitOut,
)
from fashionos_intelligence.services.brain import BrainIndex
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
