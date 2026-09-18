from pathlib import Path
import os

from fastapi.testclient import TestClient


def _configure(tmp_path: Path) -> None:
    (tmp_path / "SKILL.md").write_text(
        "# Constitution\nNeutral brain.",
        encoding="utf-8",
    )
    os.environ["FASHIONOS_BRAIN_ROOT"] = str(tmp_path)
    os.environ["FASHIONOS_INTERNAL_TOKEN"] = "test-secret"
    os.environ["FASHIONOS_DATABASE_URL"] = "sqlite+pysqlite:///:memory:"


def test_public_response_does_not_expose_provider(tmp_path: Path):
    _configure(tmp_path)

    from fashionos_intelligence.main import app

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/tasks",
            json={
                "workspaceId": "ws_1",
                "objective": "Enhance source",
                "mode": "STRICT_PRESERVATION_EDIT",
                "sourceAssetIds": ["asset_1"],
                "locks": {
                    "hard": ["identity", "garment"],
                    "soft": [],
                },
                "allowedChanges": ["denoise"],
                "target": {
                    "type": "image",
                    "aspectRatio": "4:5",
                },
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert "provider" not in str(body).lower()
        assert body["data"]["status"] == "queued"
        assert body["meta"]["requestId"].startswith("req_")
        assert body["meta"]["correlationId"].startswith("cor_")


def test_internal_endpoints_require_secret(tmp_path: Path):
    _configure(tmp_path)

    from fashionos_intelligence.main import app

    with TestClient(app) as client:
        denied = client.get("/internal/v1/brain/health")
        assert denied.status_code == 403
        allowed = client.get(
            "/internal/v1/brain/health",
            headers={"X-Internal-Token": "test-secret"},
        )
        assert allowed.status_code == 200


def test_internal_sync_and_health(tmp_path: Path):
    _configure(tmp_path)

    from fashionos_intelligence.main import app

    headers = {"X-Internal-Token": "test-secret"}
    with TestClient(app) as client:
        sync = client.post("/internal/v1/brain/sync", headers=headers)
        assert sync.status_code == 200
        assert sync.json()["indexUnitCount"] >= 1
        health = client.get("/internal/v1/brain/health", headers=headers)
        assert health.status_code == 200
        assert health.json()["state"] == "healthy"


def test_created_task_is_persisted_and_retrievable(tmp_path: Path):
    _configure(tmp_path)

    from fashionos_intelligence.main import app

    with TestClient(app) as client:
        created = client.post(
            "/api/v1/tasks",
            json={
                "workspaceId": "ws_1",
                "objective": "Create a test task",
                "mode": "NEW_GENERATION",
                "target": {"type": "image"},
            },
        )
        assert created.status_code == 200
        task_id = created.json()["data"]["taskId"]
        fetched = client.get(f"/api/v1/tasks/{task_id}")
        assert fetched.status_code == 200
        assert fetched.json()["data"]["taskId"] == task_id

def test_internal_retrieval_is_traceable(tmp_path: Path):
    _configure(tmp_path)
    p = tmp_path / "knowledge" / "source-preservation"
    p.mkdir(parents=True)
    (p / "source-preservation.md").write_text(
        "# Preservation\nIdentity and garment are hard locks.",
        encoding="utf-8",
    )
    q = tmp_path / "qc"
    q.mkdir(parents=True)
    (q / "forensic-reality-qc.md").write_text(
        "# QC\nPreservation failures require rework.",
        encoding="utf-8",
    )

    from fashionos_intelligence.main import app

    headers = {"X-Internal-Token": "test-secret"}
    with TestClient(app) as client:
        client.post("/internal/v1/brain/sync", headers=headers)
        response = client.post(
            "/internal/v1/brain/retrieve",
            headers=headers,
            json={
                "taskId": "task_1",
                "mode": "STRICT_PRESERVATION_EDIT",
                "sourceRoles": ["primary"],
                "realityClass": "professional_lifestyle",
                "requiredCapabilities": ["preservation", "qc"],
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["brainRevision"]
        assert "source_preservation" in body["domains"]
        assert body["rules"]
        assert all(rule["unitId"] for rule in body["rules"])

def test_public_docs_are_disabled(tmp_path: Path):
    _configure(tmp_path)

    from fashionos_intelligence.main import app

    with TestClient(app) as client:
        assert client.get("/docs").status_code == 404
        assert client.get("/openapi.json").status_code == 404
