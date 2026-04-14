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
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{self._base_url}/v1/images/generations",
                json={"model": self._model, "prompt": text},
            )
            response.raise_for_status()
            payload = response.json()
            data = payload.get("data", [])
            if data:
                item = data[0]
                if "b64_json" in item:
                    return {"mimeType": "image/png", "dataBase64": item["b64_json"], "promptUsed": text[:200]}
                if "url" in item:
                    return {"mimeType": "image/url", "url": item["url"], "promptUsed": text[:200]}
            return {"mimeType": "image/unknown", "promptUsed": text[:200]}

