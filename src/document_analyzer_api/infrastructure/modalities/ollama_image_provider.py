"""Module `src/document_analyzer_api/infrastructure/modalities/ollama_image_provider.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: OllamaImageProvider.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from __future__ import annotations

import httpx

from ...domain.ports.image_provider import ImageProviderPort


class OllamaImageProvider(ImageProviderPort):
    """OllamaImageProvider provider adapter.
    
    This class is defined in `src/document_analyzer_api/infrastructure/modalities/ollama_image_provider.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, *, base_url: str, model: str, fallback: ImageProviderPort | None = None) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/modalities/ollama_image_provider.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (rstrip) to satisfy the callable contract.
        
            Args:
                base_url: Input parameter accepted by `__init__`.
                model: Input parameter accepted by `__init__`.
                fallback: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._fallback = fallback

    def generate_from_text(self, text: str) -> dict:
        # Prefer Ollama OpenAI-compatible image route when available.
        """Synchronous execution path for `generate_from_text`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/modalities/ollama_image_provider.py` and contributes to module-level behavior
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
                if response.status_code < 400:
                    payload = response.json()
                    data = payload.get("data", [])
                    if data:
                        item = data[0]
                        if "b64_json" in item:
                            return {
                                "mimeType": "image/png",
                                "dataBase64": item["b64_json"],
                                "promptUsed": text[:200],
                                "provider": "ollama",
                            }
                        if "url" in item:
                            return {
                                "mimeType": "image/url",
                                "url": item["url"],
                                "promptUsed": text[:200],
                                "provider": "ollama",
                            }
        except Exception:
            pass

        if self._fallback is not None:
            fallback_payload = self._fallback.generate_from_text(text)
            fallback_payload.setdefault("provider", "fallback")
            return fallback_payload

        return {
            "mimeType": "image/unsupported",
            "promptUsed": text[:200],
            "provider": "ollama",
            "warning": "Ollama image generation endpoint unavailable",
        }

