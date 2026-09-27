import hashlib
import hmac
import time
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import func, select

from fashionos_intelligence.api.collections import router, verified_actor
from fashionos_intelligence.domain.collections import (
    CreateCollection,
    CreateLook,
    UpdateCollection,
    UpdateLook,
)
from fashionos_intelligence.persistence.db import (
    AssetRow,
    CollectionEventRow,
    TaskRow,
    build_session_factory,
)
from fashionos_intelligence.services.collections import CollectionError, CollectionService


@pytest.fixture
def service(tmp_path):
    sessions = build_session_factory(f"sqlite+pysqlite:///{tmp_path / 'collections.db'}")
    result = CollectionService(sessions)
    for workspace in ("one", "two"):
        for role in ("viewer", "contributor", "approver", "admin"):
            result.provision_member(workspace, role, role)
    with sessions.begin() as session:
        assets = (
            ("source", "one", "primary", "authorized"),
            ("foreign", "two", "primary", "authorized"),
            ("global", None, "primary", "authorized"),
            ("unknown", "one", "primary", "unknown"),
            ("reference", "one", "secondary_reference", "reference_only"),
            ("reference-authorized", "one", "secondary_reference", "authorized"),
        )
        for asset_id, workspace, role, rights in assets:
            session.add(
                AssetRow(
                    asset_id=asset_id,
                    workspace_id=workspace,
                    source_type="upload",
                    role=role,
                    rights_status=rights,
                    metadata_json={"provider": "PRIVATE"},
                    storage_uri="SECRET",
                )
            )
        session.add(TaskRow(task_id="task-one", workspace_id="one", objective="task", mode="NEW_GENERATION", status="CREATED"))
        session.add(TaskRow(task_id="task-two", workspace_id="two", objective="task", mode="NEW_GENERATION", status="CREATED"))
    return result


def create_collection(service, **overrides):
    payload = {
        "collectionId": str(uuid4()),
        "name": "Collection",
        "objective": "Preserve tailoring",
        "hardLocks": ["garment"],
        "allowedChanges": ["lighting"],
    }
    payload.update(overrides)
    return service.create("one", "contributor", CreateCollection(**payload))


def create_look(service, collection, **overrides):
    payload = {
        "lookId": str(uuid4()),
        "expectedCollectionRevision": collection["revision"],
        "name": "Look",
        "sourceAssetId": "source",
    }
    payload.update(overrides)
    return service.create_look(
        "one", "contributor", collection["collectionId"], CreateLook(**payload)
    )


def event_count(service):
    with service.sessions() as session:
        return session.scalar(select(func.count()).select_from(CollectionEventRow))


def test_persistence_replay_and_safe_projection(service):
    collection_id = str(uuid4())
    created = create_collection(service, collectionId=collection_id)
    assert create_collection(service, collectionId=collection_id) == created
    assert event_count(service) == 1
    assert CollectionService(service.sessions).get("one", "approver", collection_id) == created

    look = create_look(service, created, taskId="task-one")
    assert service.get_look("one", "admin", collection_id, look["lookId"]) == look
    assert "SECRET" not in str(look) and "provider" not in str(look)
    assert service.get("one", "contributor", collection_id)["revision"] == 2
    with pytest.raises(CollectionError, match="STATE_CONFLICT"):
        create_collection(service, collectionId=collection_id, name="Different")


def test_workspace_viewer_and_source_boundaries(service):
    collection = create_collection(service)
    collection_id = collection["collectionId"]
    with pytest.raises(CollectionError, match="WORKSPACE_ACCESS_DENIED"):
        service.get("one", "outsider", collection_id)
    with pytest.raises(CollectionError, match="COLLECTION_NOT_FOUND"):
        service.get("two", "admin", collection_id)
    assert service.list("one", "viewer") == {"items": [], "nextCursor": None}
    with pytest.raises(CollectionError, match="COLLECTION_NOT_FOUND"):
        service.get("one", "viewer", collection_id)
    with pytest.raises(CollectionError, match="FORBIDDEN"):
        service.update("one", "viewer", collection_id, UpdateCollection(expectedRevision=1, name="No"))

    cases = (
        ("foreign", "SOURCE_NOT_FOUND"),
        ("global", "SOURCE_NOT_FOUND"),
        ("unknown", "SOURCE_RIGHTS_UNKNOWN"),
        ("reference", "SOURCE_REFERENCE_ONLY"),
        ("reference-authorized", "SOURCE_REFERENCE_ONLY"),
        ("missing", "SOURCE_NOT_FOUND"),
    )
    for source, code in cases:
        with pytest.raises(CollectionError, match=code):
            create_look(service, collection, sourceAssetId=source)
        assert service.get("one", "admin", collection_id)["revision"] == 1
    assert event_count(service) == 1


def test_task_scope_archive_stale_writes_and_atomic_audit(service):
    collection = create_collection(service)
    collection_id = collection["collectionId"]
    with pytest.raises(CollectionError, match="TASK_NOT_FOUND"):
        create_look(service, collection, taskId="task-two")

    renamed = service.update(
        "one", "admin", collection_id, UpdateCollection(expectedRevision=1, name="Renamed")
    )
    with pytest.raises(CollectionError, match="STATE_CONFLICT"):
        service.update("one", "admin", collection_id, UpdateCollection(expectedRevision=1, name="Stale"))
    archived = service.update(
        "one", "admin", collection_id, UpdateCollection(expectedRevision=2, archived=True)
    )
    with pytest.raises(CollectionError, match="STATE_CONFLICT"):
        create_look(service, archived)
    restored = service.update(
        "one", "admin", collection_id, UpdateCollection(expectedRevision=3, archived=False)
    )
    look = create_look(service, restored)
    updated = service.update_look(
        "one",
        "admin",
        collection_id,
        look["lookId"],
        UpdateLook(expectedRevision=1, expectedCollectionRevision=5, name="Updated look"),
    )
    assert updated["revision"] == 2
    with pytest.raises(CollectionError, match="STATE_CONFLICT"):
        service.update_look(
            "one",
            "admin",
            collection_id,
            look["lookId"],
            UpdateLook(expectedRevision=1, expectedCollectionRevision=6, name="Stale"),
        )
    assert service.get("one", "admin", collection_id)["revision"] == 6
    assert event_count(service) == 6
    with service.sessions() as session:
        source = session.get(AssetRow, "source")
        assert source.storage_uri == "SECRET"
        assert source.metadata_json == {"provider": "PRIVATE"}


def test_pagination_input_validation_and_fail_closed_api(service):
    for index in range(4):
        create_collection(service, name=f"Collection {index}")
    first = service.list("one", "admin", limit=2)
    second = service.list("one", "admin", limit=2, cursor=first["nextCursor"])
    assert len(first["items"]) == len(second["items"]) == 2
    assert second["nextCursor"] is None
    assert len({item["collectionId"] for item in first["items"] + second["items"]}) == 4

    for invalid in (
        {"name": " "},
        {"objective": ""},
        {"provider": "private"},
        {"hardLocks": ["fabric"], "allowedChanges": ["FABRIC"]},
    ):
        data = {"collectionId": str(uuid4()), "name": "Valid", "objective": "Valid"}
        data.update(invalid)
        with pytest.raises(ValidationError):
            CreateCollection(**data)

    app = FastAPI()
    app.state.collection_service = service
    app.state.settings = SimpleNamespace(workspace_auth_secret="gateway-secret")
    app.include_router(router)
    with TestClient(app) as client:
        response = client.get(
            "/api/v2/workspaces/one/collections",
            headers={"X-User": "admin", "X-Role": "admin", "X-Workspace": "one"},
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "UNAUTHORIZED"

        timestamp = int(time.time())
        path = "/api/v2/workspaces/one/collections"
        message = f"contributor\n{timestamp}\nGET\n{path}".encode()
        signature = hmac.new(b"gateway-secret", message, hashlib.sha256).hexdigest()
        signed = client.get(
            path,
            headers={
                "X-FashionOS-Actor": "contributor",
                "X-FashionOS-Timestamp": str(timestamp),
                "X-FashionOS-Signature": signature,
            },
        )
        assert signed.status_code == 200
        assert signed.json()["data"]["items"]
        stale_timestamp = timestamp - 301
        stale_message = f"contributor\n{stale_timestamp}\nGET\n{path}".encode()
        stale_signature = hmac.new(b"gateway-secret", stale_message, hashlib.sha256).hexdigest()
        stale = client.get(
            path,
            headers={
                "X-FashionOS-Actor": "contributor",
                "X-FashionOS-Timestamp": str(stale_timestamp),
                "X-FashionOS-Signature": stale_signature,
            },
        )
        assert stale.status_code == 401
        bad_path_signature = hmac.new(
            b"gateway-secret",
            f"contributor\n{timestamp}\nGET\n/api/v2/workspaces/two/collections".encode(),
            hashlib.sha256,
        ).hexdigest()
        assert client.get(path, headers={
            "X-FashionOS-Actor": "contributor",
            "X-FashionOS-Timestamp": str(timestamp),
            "X-FashionOS-Signature": bad_path_signature,
        }).status_code == 401

    app.dependency_overrides[verified_actor] = lambda: "contributor"
    with TestClient(app) as client:
        root = "/api/v2/workspaces/one/collections"
        created = client.post(
            root,
            json={"collectionId": str(uuid4()), "name": "API", "objective": "Draft"},
        )
        assert created.status_code == 200
        collection = created.json()["data"]
        path = f"{root}/{collection['collectionId']}"
        assert client.get(path).json()["data"] == collection
        assert client.get(f"/api/v2/workspaces/two/collections/{collection['collectionId']}").status_code == 404
        assert client.patch(path, json={"expectedRevision": 1, "name": "Updated"}).json()["data"]["revision"] == 2
        assert client.patch(path, json={"expectedRevision": 1, "name": "Stale"}).status_code == 409
        invalid = client.post(
            root,
            json={"collectionId": str(uuid4()), "name": "x", "objective": "x", "internalPrompt": "DO NOT ECHO"},
        )
        assert invalid.status_code == 422 and "DO NOT ECHO" not in invalid.text
        assert client.get(f"{root}?limit=100000").status_code == 422
        assert client.delete(path).status_code == 405
