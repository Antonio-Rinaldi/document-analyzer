"""Module `src/document_analyzer_api/infrastructure/modalities/http_tts_provider.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: HttpTTSProvider.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from __future__ import annotations

import httpx

from ...domain.ports.tts_provider import TTSProviderPort


class HttpTTSProvider(TTSProviderPort):
    """HttpTTSProvider provider adapter.
    
    This class is defined in `src/document_analyzer_api/infrastructure/modalities/http_tts_provider.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, *, base_url: str, model: str, voice: str) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/modalities/http_tts_provider.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (rstrip) to satisfy the callable contract.
        
            Args:
                base_url: Input parameter accepted by `__init__`.
                model: Input parameter accepted by `__init__`.
                voice: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._voice = voice

    def synthesize(self, text: str, audio_format: str) -> bytes:
        """Synchronous execution path for `synthesize`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/modalities/http_tts_provider.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (Client, post, raise_for_status) to satisfy the callable contract.
        
            Args:
                text: Input parameter accepted by `synthesize`.
                audio_format: Input parameter accepted by `synthesize`.
        
            Returns:
                A value compatible with `bytes`.
        """
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{self._base_url}/v1/audio/speech",
                json={
                    "model": self._model,
                    "voice": self._voice,
                    "input": text,
                    "format": audio_format,
                },
            )
            response.raise_for_status()
            return response.content

