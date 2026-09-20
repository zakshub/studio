from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from hashlib import sha256
from typing import Any

import httpx

from fashionos_intelligence.services.storage import BlobStore


class LiveProviderError(RuntimeError):
    pass


def _extract_response_text(payload: dict[str, Any]) -> str:
    direct = payload.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    texts: list[str] = []
    for item in payload.get("output", []) or []:
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []) or []:
            if not isinstance(content, dict):
                continue
            if content.get("type") in {"output_text", "text"}:
                value = content.get("text")
                if isinstance(value, str):
                    texts.append(value)
    return "\n".join(texts).strip()


@dataclass
class OpenAIImageGenerationTransport:
    """Live image-generation transport backed by the OpenAI Images API."""

    api_key: str
    store: BlobStore
    model: str = "gpt-image-2"
    base_url: str = "https://api.openai.com/v1"
    timeout_seconds: float = 180.0

    def invoke(
        self,
        *,
        operation: str,
        payload: dict[str, Any],
        source_asset_ids: tuple[str, ...],
    ) -> dict[str, Any]:
        if operation not in {
            "NEW_GENERATION",
            "FASHION_EDITORIAL",
            "PORTRAIT",
            "PRODUCT_IMAGE",
            "CINEMATIC_STILL",
            "MOBILE_SOCIAL_REALISM",
            "LIFESTYLE_DOCUMENTARY",
            "generate",
        }:
            raise LiveProviderError("OPENAI_IMAGE_OPERATION_UNSUPPORTED")

        objective = str(payload.get("objective", "")).strip()
        directions = payload.get("creativeDirections", [])
        prompt = self._build_prompt(objective=objective, directions=directions, payload=payload)
        size = str(payload.get("size", "1024x1536"))
        quality = str(payload.get("quality", "medium"))
        output_format = str(payload.get("outputFormat", "png"))

        body = {
            "model": self.model,
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "output_format": output_format,
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    f"{self.base_url}/images/generations",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=body,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:800]
            raise LiveProviderError(
                f"OPENAI_IMAGE_HTTP_{exc.response.status_code}:{detail}"
            ) from exc
        except Exception as exc:
            raise LiveProviderError(f"OPENAI_IMAGE_REQUEST_FAILED:{exc}") from exc

        entries = data.get("data") or []
        if not entries or not isinstance(entries[0], dict):
            raise LiveProviderError("OPENAI_IMAGE_EMPTY_RESPONSE")

        entry = entries[0]
        encoded = entry.get("b64_json") or entry.get("b64")
        if not isinstance(encoded, str) or not encoded:
            raise LiveProviderError("OPENAI_IMAGE_BASE64_MISSING")

        try:
            image_bytes = base64.b64decode(encoded)
        except Exception as exc:
            raise LiveProviderError("OPENAI_IMAGE_BASE64_INVALID") from exc

        suffix = f".{output_format}"
        stored = self.store.put(image_bytes, suffix=suffix)
        asset_id = f"asset_generated_{stored.content_hash[:20]}"

        return {
            "status": "succeeded",
            "output": {
                "assetIds": [asset_id],
                "storageUri": stored.uri,
                "contentHash": stored.content_hash,
                "sizeBytes": stored.size_bytes,
                "mimeType": f"image/{'jpeg' if output_format in {'jpg', 'jpeg'} else output_format}",
                "generationPromptHash": sha256(prompt.encode("utf-8")).hexdigest(),
            },
            "diagnostics": {
                "providerClass": "openai_image",
                "model": self.model,
                "size": size,
                "quality": quality,
                "usage": data.get("usage"),
            },
        }

    @staticmethod
    def _build_prompt(
        *,
        objective: str,
        directions: Any,
        payload: dict[str, Any],
    ) -> str:
        direction_lines: list[str] = []
        if isinstance(directions, list):
            for direction in directions[:4]:
                if not isinstance(direction, dict):
                    continue
                principles = direction.get("principles") or []
                tension = direction.get("tension")
                if principles:
                    direction_lines.append(
                        "- "
                        + "; ".join(str(item) for item in principles[:3])
                        + (f"; creative tension: {tension}" if tension else "")
                    )

        constraints = payload.get("constraints") or []
        constraint_text = "\n".join(f"- {item}" for item in constraints) if constraints else "- none beyond the objective"

        return (
            "Create one original, photorealistic fashion image for the following objective.\n\n"
            f"OBJECTIVE:\n{objective}\n\n"
            "INTERNAL CREATIVE PRINCIPLES TO SYNTHESIZE (do not imitate any named creator):\n"
            + ("\n".join(direction_lines) if direction_lines else "- preserve physical coherence and serve the objective")
            + "\n\nCONSTRAINTS:\n"
            + constraint_text
            + "\n\nQUALITY REQUIREMENTS:\n"
            "- believable human anatomy and skin\n"
            "- physically coherent lighting, shadows, reflections and materials\n"
            "- realistic garment structure and fabric behavior\n"
            "- plausible camera/lens/depth-of-field behavior\n"
            "- no logos, watermarks, text or brand imitation unless explicitly required\n"
            "- avoid plastic skin, impossible hands, random garment details and generic AI gloss\n"
            "- result must be original rather than a reproduction of a known campaign or creator signature"
        )


@dataclass
class OpenAIVisionQCTransport:
    """Separate vision-verifier role using a multimodal Responses API model."""

    api_key: str
    store: BlobStore
    model: str = "gpt-5.6-luna"
    base_url: str = "https://api.openai.com/v1"
    timeout_seconds: float = 120.0

    def invoke(
        self,
        *,
        operation: str,
        payload: dict[str, Any],
        source_asset_ids: tuple[str, ...],
    ) -> dict[str, Any]:
        if operation not in {"verify", "vision_qc"}:
            raise LiveProviderError("OPENAI_VISION_OPERATION_UNSUPPORTED")

        storage_uri = payload.get("candidateStorageUri")
        if not isinstance(storage_uri, str) or not storage_uri:
            raise LiveProviderError("VERIFIER_CANDIDATE_URI_REQUIRED")

        image_bytes = self.store.get(storage_uri)
        mime = str(payload.get("mimeType", "image/png"))
        image_url = f"data:{mime};base64,{base64.b64encode(image_bytes).decode('ascii')}"

        objective = str(payload.get("objective", ""))
        preservation_required = bool(payload.get("preservationRequired", False))
        hard_locks = payload.get("hardLocks") or []

        instruction = (
            "You are an independent visual quality-control verifier for a fashion production system. "
            "Evaluate only what is visible and the supplied brief. Return JSON only, with this exact shape: "
            '{"accepted":true,"dimensions":{"brief_adherence":0,"anatomy":0,"garment_material":0,'
            '"camera_lens":0,"lighting_realism":0,"originality":0,"anti_ai_realism":0},'
            '"critical_dimensions":["anatomy","garment_material","anti_ai_realism"],'
            '"reasons":["..."]}. '
            "Scores are 0 to 5. accepted must be false if any critical dimension is 2 or below. "
            "Do not claim source-preservation verification unless an original comparison image is supplied. "
            f"Brief: {objective}. Preservation required: {preservation_required}. Hard locks: {hard_locks}."
        )

        body = {
            "model": self.model,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": instruction},
                        {"type": "input_image", "image_url": image_url, "detail": "high"},
                    ],
                }
            ],
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    f"{self.base_url}/responses",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=body,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:800]
            raise LiveProviderError(
                f"OPENAI_VISION_HTTP_{exc.response.status_code}:{detail}"
            ) from exc
        except Exception as exc:
            raise LiveProviderError(f"OPENAI_VISION_REQUEST_FAILED:{exc}") from exc

        text = _extract_response_text(data)
        if not text:
            raise LiveProviderError("OPENAI_VISION_EMPTY_RESPONSE")

        parsed = self._parse_json(text)
        dimensions = parsed.get("dimensions")
        if not isinstance(dimensions, dict):
            raise LiveProviderError("OPENAI_VISION_DIMENSIONS_MISSING")

        clean_dimensions: dict[str, float] = {}
        for name, value in dimensions.items():
            try:
                clean_dimensions[str(name)] = max(0.0, min(5.0, float(value)))
            except (TypeError, ValueError):
                continue

        critical = [
            str(item)
            for item in parsed.get("critical_dimensions", [])
            if isinstance(item, str)
        ]
        reasons = [
            str(item)
            for item in parsed.get("reasons", [])
            if isinstance(item, (str, int, float))
        ]
        accepted = bool(parsed.get("accepted", False))
        if any(clean_dimensions.get(name, 5.0) <= 2.0 for name in critical):
            accepted = False

        return {
            "status": "succeeded",
            "output": {
                "accepted": accepted,
                "dimensions": clean_dimensions,
                "criticalDimensions": critical,
                "reasons": reasons,
            },
            "diagnostics": {
                "providerClass": "openai_vision_qc",
                "model": self.model,
                "responseId": data.get("id"),
                "usage": data.get("usage"),
            },
        }

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:
        candidate = text.strip()
        fence = chr(96) * 3
        if candidate.startswith(fence):
            candidate = candidate[len(fence):].lstrip()
            if candidate.lower().startswith("json"):
                candidate = candidate[4:].lstrip()
            if candidate.endswith(fence):
                candidate = candidate[:-len(fence)].rstrip()
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            start = candidate.find("{")
            end = candidate.rfind("}")
            if start < 0 or end <= start:
                raise LiveProviderError("OPENAI_VISION_JSON_INVALID")
            try:
                parsed = json.loads(candidate[start : end + 1])
            except json.JSONDecodeError as exc:
                raise LiveProviderError("OPENAI_VISION_JSON_INVALID") from exc

        if not isinstance(parsed, dict):
            raise LiveProviderError("OPENAI_VISION_JSON_NOT_OBJECT")
        return parsed
