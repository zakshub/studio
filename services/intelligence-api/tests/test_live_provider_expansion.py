from __future__ import annotations

import base64

from fashionos_intelligence.services.executors import ExecutionRequest
from fashionos_intelligence.services.live_gemini import GeminiImageTransport
from fashionos_intelligence.services.live_openai import OpenAIImageGenerationTransport
from fashionos_intelligence.services.provider_adapters import (
    CrossProviderVerifierAdapter,
    ProviderExecutorAdapter,
)
from fashionos_intelligence.services.storage import LocalContentAddressedStore


class FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload
        self.text = str(payload)
        self.status_code = 200

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


class FakeClient:
    def __init__(self, response_payload: dict, calls: list[dict], *args, **kwargs):
        self.response_payload = response_payload
        self.calls = calls

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def post(self, url: str, **kwargs):
        self.calls.append({"url": url, **kwargs})
        return FakeResponse(self.response_payload)


class RecordingTransport:
    def __init__(self, label: str, calls: list[str]):
        self.label = label
        self.calls = calls

    def invoke(self, *, operation, payload, source_asset_ids):
        self.calls.append(self.label)
        return {
            "status": "succeeded",
            "output": {
                "accepted": True,
                "dimensions": {"anatomy": 5},
                "criticalDimensions": ["anatomy"],
                "reasons": [],
            },
            "diagnostics": {},
        }


def test_cross_provider_verifier_prefers_different_provider():
    calls: list[str] = []
    openai = ProviderExecutorAdapter(
        name="openai-vision-qc",
        capabilities={"vision_qc"},
        provider="openai",
        transport=RecordingTransport("openai", calls),
    )
    gemini = ProviderExecutorAdapter(
        name="gemini-vision-qc",
        capabilities={"vision_qc"},
        provider="gemini",
        transport=RecordingTransport("gemini", calls),
    )
    verifier = CrossProviderVerifierAdapter((openai, gemini))

    result = verifier.execute(
        ExecutionRequest(
            task_id="task_1",
            capability="vision_qc",
            operation="verify",
            payload={"generatorProvider": "openai"},
        )
    )

    assert calls == ["gemini"]
    assert result.executor_class == "gemini-vision-qc"
    assert result.diagnostics["sameProviderFallback"] is False


def test_openai_image_edit_uses_edit_endpoint_and_source(monkeypatch, tmp_path):
    from fashionos_intelligence.services import live_openai

    store = LocalContentAddressedStore(tmp_path / "objects")
    source = store.put(b"source-image", suffix=".png")
    output_bytes = b"edited-image"
    calls: list[dict] = []
    response_payload = {
        "data": [{"b64_json": base64.b64encode(output_bytes).decode("ascii")}],
        "usage": {"total_tokens": 10},
    }

    monkeypatch.setattr(
        live_openai.httpx,
        "Client",
        lambda *args, **kwargs: FakeClient(response_payload, calls),
    )

    transport = OpenAIImageGenerationTransport(
        api_key="test-key",
        store=store,
        model="generation-model",
        edit_model="edit-model",
    )
    result = transport.invoke(
        operation="STRICT_PRESERVATION_EDIT",
        payload={
            "objective": "Clean the source without changing identity or garment.",
            "sourceStorageUri": source.uri,
            "sourceMimeType": "image/png",
            "hardLocks": ["face identity", "garment"],
            "preservationRequired": True,
        },
        source_asset_ids=("source_1",),
    )

    assert calls[0]["url"].endswith("/images/edits")
    assert calls[0]["data"]["model"] == "edit-model"
    assert calls[0]["files"][0][0] == "image[]"
    assert calls[0]["files"][0][1][1] == b"source-image"
    assert result["diagnostics"]["operationClass"] == "edit"
    assert result["diagnostics"]["provider"] == "openai"
    assert store.get(result["output"]["storageUri"]) == output_bytes


def test_gemini_image_edit_sends_source_inline_and_stores_output(monkeypatch, tmp_path):
    from fashionos_intelligence.services import live_gemini

    store = LocalContentAddressedStore(tmp_path / "objects")
    source = store.put(b"source-image", suffix=".png")
    output_bytes = b"gemini-edited-image"
    calls: list[dict] = []
    response_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "Edited image"},
                        {
                            "inlineData": {
                                "mimeType": "image/png",
                                "data": base64.b64encode(output_bytes).decode("ascii"),
                            }
                        },
                    ]
                }
            }
        ],
        "usageMetadata": {"totalTokenCount": 12},
    }

    monkeypatch.setattr(
        live_gemini.httpx,
        "Client",
        lambda *args, **kwargs: FakeClient(response_payload, calls),
    )

    transport = GeminiImageTransport(
        api_key="test-key",
        store=store,
        model="gemini-image-model",
    )
    result = transport.invoke(
        operation="EXISTING_IMAGE_EDIT",
        payload={
            "objective": "Relight only.",
            "sourceStorageUri": source.uri,
            "sourceMimeType": "image/png",
            "allowedChanges": ["lighting"],
            "hardLocks": ["face identity", "garment"],
            "preservationRequired": True,
        },
        source_asset_ids=("source_1",),
    )

    assert calls[0]["url"].endswith(
        "/models/gemini-image-model:generateContent"
    )
    parts = calls[0]["json"]["contents"][0]["parts"]
    inline_sources = [part["inline_data"] for part in parts if "inline_data" in part]
    assert len(inline_sources) == 1
    assert base64.b64decode(inline_sources[0]["data"]) == b"source-image"
    assert result["diagnostics"]["operationClass"] == "edit"
    assert result["diagnostics"]["provider"] == "gemini"
    assert store.get(result["output"]["storageUri"]) == output_bytes
