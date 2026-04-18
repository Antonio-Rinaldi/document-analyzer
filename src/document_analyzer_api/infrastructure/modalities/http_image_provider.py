"""Module `src/document_analyzer_api/infrastructure/modalities/http_image_provider.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: HttpImageProvider.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from __future__ import annotations

import httpx

from ...domain.ports.image_provider import ImageProviderPort


class HttpImageProvider(ImageProviderPort):
    """HttpImageProvider provider adapter.
    
    This class is defined in `src/document_analyzer_api/infrastructure/modalities/http_image_provider.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, *, base_url: str, model: str) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/modalities/http_image_provider.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (rstrip) to satisfy the callable contract.
        
            Args:
                base_url: Input parameter accepted by `__init__`.
                model: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._base_url = base_url.rstrip("/")
        self._model = model

    def generate_from_text(self, text: str) -> dict:
        """Synchronous execution path for `generate_from_text`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/modalities/http_image_provider.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Generates derived output from context, prompts, and generation options.
        
            Args:
                text: Input parameter accepted by `generate_from_text`.
        
            Returns:
                A value compatible with `dict`.
        """
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self._base_url}/v1/images/generations",
                    json={"model": self._model, "prompt": text},
                )
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code if exc.response is not None else "unknown"
            return self._unsupported_payload(text, warning=f"Image provider returned HTTP {status_code}")
        except httpx.HTTPError as exc:
            return self._unsupported_payload(text, warning=f"Image provider call failed: {exc.__class__.__name__}")

        data = payload.get("data", []) if isinstance(payload, dict) else []
        if data:
            item = data[0]
            if isinstance(item, dict) and "b64_json" in item:
                return {
                    "mimeType": "image/png",
                    "dataBase64": item["b64_json"],
                    "promptUsed": text[:200],
                    "provider": "http_image",
                }
            if isinstance(item, dict) and "url" in item:
                return {
                    "mimeType": "image/url",
                    "url": item["url"],
                    "promptUsed": text[:200],
                    "provider": "http_image",
                }
        return {
            "mimeType": "image/unknown",
            "promptUsed": text[:200],
            "provider": "http_image",
        }

    @staticmethod
    def _unsupported_payload(text: str, *, warning: str) -> dict:
        """Build a stable payload when the upstream HTTP image route is unavailable."""
        return {
            "mimeType": "image/unsupported",
            "promptUsed": text[:200],
            "provider": "http_image",
            "warning": warning,
        }

