"""Detailed module documentation for `src/document_analyzer_api/infrastructure/modalities/http_tts_provider.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `http_tts_provider.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: HttpTTSProvider.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from __future__ import annotations

import httpx

from ...domain.ports.tts_provider import TTSProviderPort


class HttpTTSProvider(TTSProviderPort):
    """Detailed class documentation for `HttpTTSProvider`.
    
    This provider adapter belongs to `src/document_analyzer_api/infrastructure/modalities/http_tts_provider.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, *, base_url: str, model: str, voice: str) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/modalities/http_tts_provider.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                base_url: Input parameter for `__init__`.
                model: Input parameter for `__init__`.
                voice: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._voice = voice

    def synthesize(self, text: str, audio_format: str) -> bytes:
        """Detailed synchronous function documentation for `synthesize`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/modalities/http_tts_provider.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                text: Input parameter for `synthesize`.
                audio_format: Input parameter for `synthesize`.
        
            Returns:
                Value defined by `synthesize` contract and consumed by downstream callers.
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

