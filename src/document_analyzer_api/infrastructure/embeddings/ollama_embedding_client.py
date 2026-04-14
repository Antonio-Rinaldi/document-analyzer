"""Module `src/document_analyzer_api/infrastructure/embeddings/ollama_embedding_client.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: OllamaEmbeddingClient.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from __future__ import annotations

import httpx

from ...domain.ports.embedding_client import EmbeddingClientPort


class OllamaEmbeddingClient(EmbeddingClientPort):
    """OllamaEmbeddingClient component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/embeddings/ollama_embedding_client.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, base_url: str, model: str) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/embeddings/ollama_embedding_client.py` and contributes to module-level behavior
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

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Asynchronous execution path for `embed_texts`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/embeddings/ollama_embedding_client.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (AsyncClient, append, get, json) to satisfy the callable contract.
        
            Args:
                texts: Input parameter accepted by `embed_texts`.
        
            Returns:
                A value compatible with `list[list[float]]`.
        """
        vectors: list[list[float]] = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for text in texts:
                response = await client.post(
                    f"{self._base_url}/api/embeddings",
                    json={"model": self._model, "prompt": text},
                )
                response.raise_for_status()
                payload = response.json()
                vectors.append(payload.get("embedding", []))
        return vectors

