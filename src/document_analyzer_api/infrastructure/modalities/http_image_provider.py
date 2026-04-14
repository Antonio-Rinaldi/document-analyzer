"""Detailed module documentation for `src/document_analyzer_api/infrastructure/modalities/http_image_provider.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `http_image_provider.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: HttpImageProvider.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from __future__ import annotations

import httpx

from ...domain.ports.image_provider import ImageProviderPort


class HttpImageProvider(ImageProviderPort):
    """Detailed class documentation for `HttpImageProvider`.
    
    This provider adapter belongs to `src/document_analyzer_api/infrastructure/modalities/http_image_provider.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, *, base_url: str, model: str) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/modalities/http_image_provider.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                base_url: Input parameter for `__init__`.
                model: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._base_url = base_url.rstrip("/")
        self._model = model

    def generate_from_text(self, text: str) -> dict:
        """Detailed synchronous function documentation for `generate_from_text`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/modalities/http_image_provider.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Generates derived output from retrieved context and provided options.
        
            Args:
                text: Input parameter for `generate_from_text`.
        
            Returns:
                Value defined by `generate_from_text` contract and consumed by downstream callers.
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

