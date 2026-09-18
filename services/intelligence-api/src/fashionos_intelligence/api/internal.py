from fastapi import APIRouter, Depends, HTTPException, Request

from fashionos_intelligence.domain.models import (
    BrainRetrieveRequest,
    BrainRetrieveResponse,
    KnowledgeUnitOut,
)
from fashionos_intelligence.services.brain import BrainIndex

router = APIRouter(prefix="/internal/v1", tags=["internal"])


def get_brain(request: Request) -> BrainIndex:
    brain = getattr(request.app.state, "brain", None)
    if brain is None:
        raise HTTPException(status_code=503, detail="BRAIN_UNAVAILABLE")
    return brain


@router.get("/brain/health")
def brain_health(brain: BrainIndex = Depends(get_brain)) -> dict[str, object]:
    return {
        "state": "healthy" if brain.units else "degraded",
        "activeRevision": brain.revision,
        "indexUnitCount": len(brain.units),
    }


@router.post(
    "/brain/retrieve",
    response_model=BrainRetrieveResponse,
    response_model_by_alias=True,
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
