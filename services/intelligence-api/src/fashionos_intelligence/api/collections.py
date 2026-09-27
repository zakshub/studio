"""V2 draft organization API with fail-closed trusted-host authentication."""
import hashlib
import hmac
import time
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from fashionos_intelligence.domain.collections import CreateCollection, CreateLook, UpdateCollection, UpdateLook
from fashionos_intelligence.services.collections import CollectionError, CollectionService
from fashionos_intelligence.settings import Settings


def envelope(data=None, error=None):
    return {"data": data, "meta": {"requestId": f"req_{uuid4().hex}", "correlationId": f"cor_{uuid4().hex}"}, "error": error}


class SafeCollectionRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handler(request):
            try:
                return await original(request)
            except RequestValidationError:
                return JSONResponse(envelope(error={"code": "INVALID_REQUEST", "message": "Check the supplied fields.", "retryable": False}), status_code=422)
            except CollectionError as exc:
                messages = {"UNAUTHORIZED": "Sign in to continue.", "WORKSPACE_ACCESS_DENIED": "Workspace access is unavailable.",
                            "FORBIDDEN": "Your role does not allow this action.", "STATE_CONFLICT": "This item changed. Reload before trying again.",
                            "SOURCE_RIGHTS_UNKNOWN": "Confirm source usage rights before continuing.",
                            "SOURCE_REFERENCE_ONLY": "This source cannot be used as a production source."}
                return JSONResponse(envelope(error={"code": exc.code,
                                    "message": messages.get(exc.code, "The requested item is unavailable or invalid."),
                                    "retryable": False}), status_code=exc.status)
        return handler


def verified_actor(
    request: Request,
    x_fashionos_actor: str | None = Header(default=None),
    x_fashionos_timestamp: str | None = Header(default=None),
    x_fashionos_signature: str | None = Header(default=None),
) -> str:
    actor = getattr(request.state, "workspace_actor_id", None)
    if isinstance(actor, str) and actor.strip() and len(actor) <= 64:
        return actor

    settings: Settings | None = getattr(request.app.state, "settings", None)
    secret = settings.workspace_auth_secret if settings else None
    if not secret or not x_fashionos_actor or not x_fashionos_timestamp or not x_fashionos_signature:
        raise CollectionError("UNAUTHORIZED", 401)
    actor = x_fashionos_actor.strip()
    if not actor or len(actor) > 64:
        raise CollectionError("UNAUTHORIZED", 401)
    try:
        timestamp = int(x_fashionos_timestamp)
    except ValueError as exc:
        raise CollectionError("UNAUTHORIZED", 401) from exc
    if abs(int(time.time()) - timestamp) > 300:
        raise CollectionError("UNAUTHORIZED", 401)
    message = f"{actor}\n{timestamp}\n{request.method.upper()}\n{request.url.path}".encode()
    expected = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(x_fashionos_signature.lower(), expected):
        raise CollectionError("UNAUTHORIZED", 401)
    return actor


def service(request: Request) -> CollectionService:
    return request.app.state.collection_service


router = APIRouter(prefix="/api/v2/workspaces/{workspace_id}/collections", route_class=SafeCollectionRoute, tags=["collections"])


@router.post("")
def create_collection(workspace_id: str, payload: CreateCollection, actor=Depends(verified_actor), svc=Depends(service)):
    return envelope(svc.create(workspace_id, actor, payload))


@router.get("")
def list_collections(workspace_id: str, cursor: UUID | None = None, limit: int = Query(50, ge=1, le=100), actor=Depends(verified_actor), svc=Depends(service)):
    return envelope(svc.list(workspace_id, actor, cursor=str(cursor) if cursor else None, limit=limit))


@router.get("/{collection_id}")
def get_collection(workspace_id: str, collection_id: UUID, actor=Depends(verified_actor), svc=Depends(service)):
    return envelope(svc.get(workspace_id, actor, str(collection_id)))


@router.patch("/{collection_id}")
def update_collection(workspace_id: str, collection_id: UUID, payload: UpdateCollection, actor=Depends(verified_actor), svc=Depends(service)):
    return envelope(svc.update(workspace_id, actor, str(collection_id), payload))


@router.post("/{collection_id}/looks")
def create_look(workspace_id: str, collection_id: UUID, payload: CreateLook, actor=Depends(verified_actor), svc=Depends(service)):
    return envelope(svc.create_look(workspace_id, actor, str(collection_id), payload))


@router.get("/{collection_id}/looks")
def list_looks(workspace_id: str, collection_id: UUID, cursor: UUID | None = None, limit: int = Query(50, ge=1, le=100), actor=Depends(verified_actor), svc=Depends(service)):
    return envelope(svc.looks(workspace_id, actor, str(collection_id), cursor=str(cursor) if cursor else None, limit=limit))


@router.get("/{collection_id}/looks/{look_id}")
def get_look(workspace_id: str, collection_id: UUID, look_id: UUID, actor=Depends(verified_actor), svc=Depends(service)):
    return envelope(svc.get_look(workspace_id, actor, str(collection_id), str(look_id)))


@router.patch("/{collection_id}/looks/{look_id}")
def update_look(workspace_id: str, collection_id: UUID, look_id: UUID, payload: UpdateLook, actor=Depends(verified_actor), svc=Depends(service)):
    return envelope(svc.update_look(workspace_id, actor, str(collection_id), str(look_id), payload))
