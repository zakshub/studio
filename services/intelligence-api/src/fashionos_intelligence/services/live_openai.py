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


@dataclass
class OpenAIImageGenerationTransport:
    """Live generation and edit transport backed by the OpenAI Images API."""

    api_key: str
    store: BlobStore
    model: str = "gpt-image-2.5-flare"
    edit_model: str = "gpt-image-2.5-sunburst"
    base_url: str = "https://api.openai.com/v1"
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
            raise LiveProviderError("OPENAI_IMAGE_OPERATION_UNSUPPORTED")
        if is_edit and not source_uris:
            raise LiveProviderError("OPENAI_IMAGE_EDIT_SOURCE_REQUIRED")

        objective = str(payload.get("objective", "")).strip()
        directions = payload.get("creativeDirections", [])
        prompt = self._build_prompt(
            objective=objective,
            directions=directions,
            payload=payload,
            is_edit=is_edit,
        )
        size = str(payload.get("size", "1024x1536"))
        quality = str(payload.get("quality", "medium"))
        output_format = str(payload.get("outputFormat", "png"))
        selected_model = self.edit_model if is_edit else self.model

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                if is_edit:
                    response = self._post_edit(
                        client=client,
                        prompt=prompt,
                        payload=payload,
                        source_uris=source_uris,
                        model=selected_model,
                        size=size,
                        quality=quality,
                        output_format=output_format,
                    )
                else:
                    response = client.post(
                        f"{self.base_url}/images/generations",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": selected_model,
                            "prompt": prompt,
                            "size": size,
                            "quality": quality,
                            "output_format": output_format,
                        },
                    )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:800]
            raise LiveProviderError(
                f"OPENAI_IMAGE_HTTP_{exc.response.status_code}:{detail}"
            ) from exc
        except LiveProviderError:
            raise
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
                "provider": "openai",
                "providerClass": "openai_image",
                "operationClass": "edit" if is_edit else "generation",
                "model": selected_model,
                "size": size,
                "quality": quality,
                "usage": data.get("usage"),
            },
        }

    def _post_edit(
        self,
        *,
        client: httpx.Client,
        prompt: str,
        payload: dict[str, Any],
        source_uris: list[str],
        model: str,
        size: str,
        quality: str,
        output_format: str,
    ) -> httpx.Response:
        mime_types = _source_mime_types(payload, len(source_uris))
        files: list[tuple[str, tuple[str, bytes, str]]] = []
        for index, uri in enumerate(source_uris):
            files.append(
                (
                    "image[]",
                    (f"source_{index}.png", self.store.get(uri), mime_types[index]),
                )
            )

        mask_uri = payload.get("maskStorageUri")
        if isinstance(mask_uri, str) and mask_uri:
            mask_mime = str(payload.get("maskMimeType", "image/png"))
            files.append(("mask", ("mask.png", self.store.get(mask_uri), mask_mime)))

        return client.post(
            f"{self.base_url}/images/edits",
            headers={"Authorization": f"Bearer {self.api_key}"},
            data={
                "model": model,
                "prompt": prompt,
                "size": size,
                "quality": quality,
                "output_format": output_format,
            },
            files=files,
        )

    @staticmethod
    def _build_prompt(
        *,
        objective: str,
        directions: Any,
        payload: dict[str, Any],
        is_edit: bool,
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
        hard_locks = payload.get("hardLocks") or []
        allowed_changes = payload.get("allowedChanges") or []
        preservation_required = bool(payload.get("preservationRequired", False))
        constraint_text = (
            "\n".join(f"- {item}" for item in constraints)
            if constraints
            else "- none beyond the objective"
        )
        lock_text = (
            "\n".join(f"- preserve exactly: {item}" for item in hard_locks)
            if hard_locks
            else "- no additional hard locks supplied"
        )
        allowed_text = (
            "\n".join(f"- may change: {item}" for item in allowed_changes)
            if allowed_changes
            else "- only changes required by the objective"
        )
        action = (
            "Edit the supplied source image or images"
            if is_edit
            else "Create one original, photorealistic fashion image"
        )
        preservation_line = (
            "Preservation is mandatory. Do not redesign or reconstruct locked source details."
            if preservation_required
            else "Preserve supplied source details unless the brief explicitly authorizes a change."
        )

        return (
            f"{action} for the following objective.\n\n"
            f"OBJECTIVE:\n{objective}\n\n"
            "INTERNAL CREATIVE PRINCIPLES TO SYNTHESIZE (do not imitate any named creator):\n"
            + (
                "\n".join(direction_lines)
                if direction_lines
                else "- preserve physical coherence and serve the objective"
            )
            + "\n\nHARD LOCKS:\n"
            + lock_text
            + "\n\nALLOWED CHANGES:\n"
            + allowed_text
            + "\n\nCONSTRAINTS:\n"
            + constraint_text
            + "\n\nPRESERVATION POLICY:\n- "
            + preservation_line
            + "\n\nQUALITY REQUIREMENTS:\n"
            "- believable human anatomy and skin\n"
            "- physically coherent lighting, shadows, reflections and materials\n"
            "- realistic garment structure and fabric behavior\n"
            "- plausible camera, lens and depth of field behavior\n"
            "- no logos, watermarks, text or brand imitation unless explicitly required\n"
            "- avoid plastic skin, impossible hands, random garment details and generic AI gloss\n"
            "- result must be original rather than a reproduction of a known campaign or creator signature"
        )


@dataclass
class OpenAIVisionQCTransport:
    """Separate vision verifier role using a multimodal Responses API model."""

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

        objective = str(payload.get("objective", ""))
        preservation_required = bool(payload.get("preservationRequired", False))
        hard_locks = payload.get("hardLocks") or []
        source_uris = _source_storage_uris(payload)
        source_mimes = _source_mime_types(payload, len(source_uris))

        instruction = (
            "You are an independent visual quality control verifier for a fashion production system. "
            "Evaluate only what is visible and the supplied brief. Return JSON only, with this exact shape: "
            '{"accepted":true,"dimensions":{"brief_adherence":0,"anatomy":0,"garment_material":0,'
            '"identity_preservation":0,"garment_preservation":0,"camera_lens":0,"lighting_realism":0,'
            '"originality":0,"anti_ai_realism":0},'
            '"critical_dimensions":["anatomy","garment_material","anti_ai_realism"],'
            '"reasons":["..."]}. '
            "Scores are 0 to 5. accepted must be false if any critical dimension is 2 or below. "
            "When original source images are supplied and preservation is required, identity preservation and "
            "garment preservation are critical and must be compared directly. When no original source image is "
            "supplied, do not claim source preservation verification and omit those dimensions. "
            f"Brief: {objective}. Preservation required: {preservation_required}. Hard locks: {hard_locks}."
        )

        content_parts: list[dict[str, Any]] = [{"type": "input_text", "text": instruction}]
        for index, uri in enumerate(source_uris):
            source_bytes = self.store.get(uri)
            source_url = (
                f"data:{source_mimes[index]};base64,"
                f"{base64.b64encode(source_bytes).decode('ascii')}"
            )
            content_parts.extend(
                [
                    {"type": "input_text", "text": f"Original source image {index + 1}:"},
                    {"type": "input_image", "image_url": source_url, "detail": "high"},
                ]
            )

        image_bytes = self.store.get(storage_uri)
        mime = str(payload.get("mimeType", "image/png"))
        image_url = f"data:{mime};base64,{base64.b64encode(image_bytes).decode('ascii')}"
        content_parts.extend(
            [
                {"type": "input_text", "text": "Candidate output image:"},
                {"type": "input_image", "image_url": image_url, "detail": "high"},
            ]
        )

        body = {"model": self.model, "input": [{"role": "user", "content": content_parts}]}

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
        if preservation_required and source_uris:
            for dimension in ("identity_preservation", "garment_preservation"):
                if dimension not in critical:
                    critical.append(dimension)

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
                "provider": "openai",
                "providerClass": "openai_vision_qc",
                "model": self.model,
                "responseId": data.get("id"),
                "usage": data.get("usage"),
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
                raise LiveProviderError("OPENAI_VISION_JSON_INVALID")
            try:
                parsed = json.loads(candidate[start : end + 1])
            except json.JSONDecodeError as exc:
                raise LiveProviderError("OPENAI_VISION_JSON_INVALID") from exc

        if not isinstance(parsed, dict):
            raise LiveProviderError("OPENAI_VISION_JSON_NOT_OBJECT")
        return parsed
