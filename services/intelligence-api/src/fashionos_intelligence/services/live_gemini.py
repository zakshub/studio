from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from hashlib import sha256
from typing import Any

import httpx

from fashionos_intelligence.services.storage import BlobStore


class GeminiProviderError(RuntimeError):
    pass


def _source_storage_uris(payload: dict[str, Any]) -> list[str]:
    values = payload.get("sourceStorageUris")
    if isinstance(values, list):
        return [str(item) for item in values if isinstance(item, str) and item]
    single = payload.get("sourceStorageUri")
    if isinstance(single, str) and single:
        return [single]
    return []


def _source_mime_types(payload: dict[str, Any], count: int) -> list[str]:
    values = payload.get("sourceMimeTypes")
    if isinstance(values, list):
        clean = [str(item) for item in values if isinstance(item, str) and item]
    else:
        single = payload.get("sourceMimeType")
        clean = [single] if isinstance(single, str) and single else []
    clean.extend(["image/png"] * max(0, count - len(clean)))
    return clean[:count]


def _candidate_parts(payload: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = payload.get("candidates") or []
    if not isinstance(candidates, list) or not candidates:
        return []
    first = candidates[0]
    if not isinstance(first, dict):
        return []
    content = first.get("content") or {}
    if not isinstance(content, dict):
        return []
    parts = content.get("parts") or []
    return [part for part in parts if isinstance(part, dict)]


def _extract_text(payload: dict[str, Any]) -> str:
    texts: list[str] = []
    for part in _candidate_parts(payload):
        value = part.get("text")
        if isinstance(value, str) and value.strip():
            texts.append(value.strip())
    return "\n".join(texts)


def _extract_image(payload: dict[str, Any]) -> tuple[bytes, str]:
    for part in reversed(_candidate_parts(payload)):
        inline = part.get("inlineData") or part.get("inline_data")
        if not isinstance(inline, dict):
            continue
        encoded = inline.get("data")
        mime = inline.get("mimeType") or inline.get("mime_type") or "image/png"
        if isinstance(encoded, str) and encoded:
            try:
                return base64.b64decode(encoded), str(mime)
            except Exception as exc:
                raise GeminiProviderError("GEMINI_IMAGE_BASE64_INVALID") from exc
    raise GeminiProviderError("GEMINI_IMAGE_MISSING")


@dataclass
class GeminiImageTransport:
    """Gemini native image generation and editing transport."""

    api_key: str
    store: BlobStore
    model: str = "gemini-3.1-flash-image"
    base_url: str = "https://generativelanguage.googleapis.com/v1"
    timeout_seconds: float = 180.0

    GENERATION_OPERATIONS = {
        "NEW_GENERATION",
        "FASHION_EDITORIAL",
        "PORTRAIT",
        "PRODUCT_IMAGE",
        "CINEMATIC_STILL",
        "MOBILE_SOCIAL_REALISM",
        "LIFESTYLE_DOCUMENTARY",
        "CREATIVE_REGENERATION",
        "generate",
    }
    EDIT_OPERATIONS = {
        "EXISTING_IMAGE_EDIT",
        "STRICT_PRESERVATION_EDIT",
        "SELECTIVE_EDIT",
        "RETOUCH_ONLY",
        "RELIGHT",
        "COLOR_GRADE",
        "LUT_LOOK_APPLICATION",
        "SOURCE_WEBSITE_TREATMENT",
        "edit",
    }

    def invoke(
        self,
        *,
        operation: str,
        payload: dict[str, Any],
        source_asset_ids: tuple[str, ...],
    ) -> dict[str, Any]:
        source_uris = _source_storage_uris(payload)
        is_edit = operation in self.EDIT_OPERATIONS or bool(source_uris)
        if operation not in self.GENERATION_OPERATIONS | self.EDIT_OPERATIONS:
            raise GeminiProviderError("GEMINI_IMAGE_OPERATION_UNSUPPORTED")
        if is_edit and not source_uris:
            raise GeminiProviderError("GEMINI_IMAGE_EDIT_SOURCE_REQUIRED")

        prompt = self._build_prompt(payload=payload, is_edit=is_edit)
        parts: list[dict[str, Any]] = [{"text": prompt}]
        source_mimes = _source_mime_types(payload, len(source_uris))
        for index, uri in enumerate(source_uris):
            parts.append(
                {
                    "inline_data": {
                        "mime_type": source_mimes[index],
                        "data": base64.b64encode(self.store.get(uri)).decode("ascii"),
                    }
                }
            )

        body: dict[str, Any] = {
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    f"{self.base_url}/models/{self.model}:generateContent",
                    headers={
                        "x-goog-api-key": self.api_key,
                        "Content-Type": "application/json",
                    },
                    json=body,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:800]
            raise GeminiProviderError(
                f"GEMINI_IMAGE_HTTP_{exc.response.status_code}:{detail}"
            ) from exc
        except Exception as exc:
            raise GeminiProviderError(f"GEMINI_IMAGE_REQUEST_FAILED:{exc}") from exc

        image_bytes, mime = _extract_image(data)
        suffix = ".jpg" if mime in {"image/jpeg", "image/jpg"} else ".webp" if mime == "image/webp" else ".png"
        stored = self.store.put(image_bytes, suffix=suffix)
        asset_id = f"asset_generated_{stored.content_hash[:20]}"

        return {
            "status": "succeeded",
            "output": {
                "assetIds": [asset_id],
                "storageUri": stored.uri,
                "contentHash": stored.content_hash,
                "sizeBytes": stored.size_bytes,
                "mimeType": mime,
                "generationPromptHash": sha256(prompt.encode("utf-8")).hexdigest(),
            },
            "diagnostics": {
                "provider": "gemini",
                "providerClass": "gemini_image",
                "operationClass": "edit" if is_edit else "generation",
                "model": self.model,
                "usage": data.get("usageMetadata"),
            },
        }

    @staticmethod
    def _build_prompt(*, payload: dict[str, Any], is_edit: bool) -> str:
        objective = str(payload.get("objective", "")).strip()
        directions = payload.get("creativeDirections") or []
        principles: list[str] = []
        if isinstance(directions, list):
            for direction in directions[:4]:
                if not isinstance(direction, dict):
                    continue
                for principle in direction.get("principles") or []:
                    principles.append(str(principle))

        hard_locks = [str(item) for item in payload.get("hardLocks") or []]
        allowed_changes = [str(item) for item in payload.get("allowedChanges") or []]
        constraints = [str(item) for item in payload.get("constraints") or []]
        preservation_required = bool(payload.get("preservationRequired", False))
        action = "Edit the supplied source image" if is_edit else "Create one original fashion image"

        return (
            f"{action}.\n\n"
            f"OBJECTIVE:\n{objective}\n\n"
            "TRANSFERABLE CREATIVE PRINCIPLES:\n"
            + ("\n".join(f"- {item}" for item in principles[:12]) or "- Serve the objective with physical coherence")
            + "\n\nHARD LOCKS:\n"
            + ("\n".join(f"- preserve exactly: {item}" for item in hard_locks) or "- none supplied")
            + "\n\nALLOWED CHANGES:\n"
            + ("\n".join(f"- {item}" for item in allowed_changes) or "- only changes required by the objective")
            + "\n\nCONSTRAINTS:\n"
            + ("\n".join(f"- {item}" for item in constraints) or "- none beyond the objective")
            + "\n\nPRESERVATION:\n"
            + (
                "Preservation is mandatory. Do not redesign locked identity or garment details."
                if preservation_required
                else "Preserve supplied source details unless change is explicitly authorized."
            )
            + "\n\nQUALITY:\n"
            "- photorealistic skin, anatomy, fabric and construction\n"
            "- coherent camera, optics, lighting, shadows and reflections\n"
            "- no generic AI gloss, random garment changes or pasted cutout appearance\n"
            "- do not imitate a named living creator or reproduce a known campaign"
        )


@dataclass
class GeminiVisionQCTransport:
    """Gemini multimodal verifier with optional source to candidate comparison."""

    api_key: str
    store: BlobStore
    model: str = "gemini-3.8-flash"
    base_url: str = "https://generativelanguage.googleapis.com/v1"
    timeout_seconds: float = 120.0

    def invoke(
        self,
        *,
        operation: str,
        payload: dict[str, Any],
        source_asset_ids: tuple[str, ...],
    ) -> dict[str, Any]:
        if operation not in {"verify", "vision_qc"}:
            raise GeminiProviderError("GEMINI_VISION_OPERATION_UNSUPPORTED")

        candidate_uri = payload.get("candidateStorageUri")
        if not isinstance(candidate_uri, str) or not candidate_uri:
            raise GeminiProviderError("VERIFIER_CANDIDATE_URI_REQUIRED")

        source_uris = _source_storage_uris(payload)
        source_mimes = _source_mime_types(payload, len(source_uris))
        preservation_required = bool(payload.get("preservationRequired", False))
        hard_locks = payload.get("hardLocks") or []
        objective = str(payload.get("objective", ""))

        instruction = (
            "Act as an independent visual quality control verifier for fashion production. Return JSON only. "
            "Use this shape: "
            '{"accepted":true,"dimensions":{"brief_adherence":0,"anatomy":0,"garment_material":0,'
            '"identity_preservation":0,"garment_preservation":0,"camera_lens":0,"lighting_realism":0,'
            '"originality":0,"anti_ai_realism":0},'
            '"critical_dimensions":["anatomy","garment_material","anti_ai_realism"],"reasons":["..."]}. '
            "All scores are 0 to 5. Reject if any critical score is 2 or below. If original source images are "
            "supplied and preservation is required, directly compare identity and garment details and mark those "
            "dimensions critical. If originals are absent, omit preservation dimensions rather than guessing. "
            f"Brief: {objective}. Preservation required: {preservation_required}. Hard locks: {hard_locks}."
        )

        parts: list[dict[str, Any]] = [{"text": instruction}]
        for index, uri in enumerate(source_uris):
            parts.extend(
                [
                    {"text": f"Original source image {index + 1}:"},
                    {
                        "inline_data": {
                            "mime_type": source_mimes[index],
                            "data": base64.b64encode(self.store.get(uri)).decode("ascii"),
                        }
                    },
                ]
            )

        candidate_mime = str(payload.get("mimeType", "image/png"))
        parts.extend(
            [
                {"text": "Candidate output image:"},
                {
                    "inline_data": {
                        "mime_type": candidate_mime,
                        "data": base64.b64encode(self.store.get(candidate_uri)).decode("ascii"),
                    }
                },
            ]
        )

        body = {"contents": [{"role": "user", "parts": parts}]}
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    f"{self.base_url}/models/{self.model}:generateContent",
                    headers={
                        "x-goog-api-key": self.api_key,
                        "Content-Type": "application/json",
                    },
                    json=body,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:800]
            raise GeminiProviderError(
                f"GEMINI_VISION_HTTP_{exc.response.status_code}:{detail}"
            ) from exc
        except Exception as exc:
            raise GeminiProviderError(f"GEMINI_VISION_REQUEST_FAILED:{exc}") from exc

        text = _extract_text(data)
        if not text:
            raise GeminiProviderError("GEMINI_VISION_EMPTY_RESPONSE")
        parsed = self._parse_json(text)
        raw_dimensions = parsed.get("dimensions")
        if not isinstance(raw_dimensions, dict):
            raise GeminiProviderError("GEMINI_VISION_DIMENSIONS_MISSING")

        dimensions: dict[str, float] = {}
        for name, value in raw_dimensions.items():
            try:
                dimensions[str(name)] = max(0.0, min(5.0, float(value)))
            except (TypeError, ValueError):
                continue

        critical = [
            str(item)
            for item in parsed.get("critical_dimensions", [])
            if isinstance(item, str)
        ]
        if preservation_required and source_uris:
            for dimension in ("identity_preservation", "garment_preservation"):
                if dimension not in critical:
                    critical.append(dimension)
        reasons = [str(item) for item in parsed.get("reasons", [])]
        accepted = bool(parsed.get("accepted", False))
        if any(dimensions.get(name, 5.0) <= 2.0 for name in critical):
            accepted = False

        return {
            "status": "succeeded",
            "output": {
                "accepted": accepted,
                "dimensions": dimensions,
                "criticalDimensions": critical,
                "reasons": reasons,
            },
            "diagnostics": {
                "provider": "gemini",
                "providerClass": "gemini_vision_qc",
                "model": self.model,
                "usage": data.get("usageMetadata"),
                "sourceComparisonCount": len(source_uris),
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
                raise GeminiProviderError("GEMINI_VISION_JSON_INVALID")
            try:
                parsed = json.loads(candidate[start : end + 1])
            except json.JSONDecodeError as exc:
                raise GeminiProviderError("GEMINI_VISION_JSON_INVALID") from exc
        if not isinstance(parsed, dict):
            raise GeminiProviderError("GEMINI_VISION_JSON_NOT_OBJECT")
        return parsed
