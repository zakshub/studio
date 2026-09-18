from pathlib import Path
import os

from fastapi.testclient import TestClient


def test_public_response_does_not_expose_provider(tmp_path: Path):
    (tmp_path / "SKILL.md").write_text(
        "# Constitution\nNeutral brain.",
        encoding="utf-8",
    )
    os.environ["FASHIONOS_BRAIN_ROOT"] = str(tmp_path)

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
        assert body["status"] == "queued"

def test_internal_sync_and_health(tmp_path: Path):
    (tmp_path / "SKILL.md").write_text(
        "# Constitution\nNeutral brain.",
        encoding="utf-8",
    )
    os.environ["FASHIONOS_BRAIN_ROOT"] = str(tmp_path)

    from fashionos_intelligence.main import app

    with TestClient(app) as client:
        sync = client.post("/internal/v1/brain/sync")
        assert sync.status_code == 200
        assert sync.json()["indexUnitCount"] >= 1
        health = client.get("/internal/v1/brain/health")
        assert health.status_code == 200
        assert health.json()["state"] == "healthy"
