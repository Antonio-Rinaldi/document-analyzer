"""Detailed module documentation for `src/document_analyzer_api/infrastructure/embeddings/ollama_embedding_client.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `ollama_embedding_client.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: OllamaEmbeddingClient.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from __future__ import annotations

import httpx

from ...domain.ports.embedding_client import EmbeddingClientPort


class OllamaEmbeddingClient(EmbeddingClientPort):
    """Detailed class documentation for `OllamaEmbeddingClient`.
    
    This component belongs to `src/document_analyzer_api/infrastructure/embeddings/ollama_embedding_client.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, base_url: str, model: str) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/embeddings/ollama_embedding_client.py` and contributes to the module workflow
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

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Detailed asynchronous function documentation for `embed_texts`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/embeddings/ollama_embedding_client.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                texts: Input parameter for `embed_texts`.
        
            Returns:
                Value defined by `embed_texts` contract and consumed by downstream callers.
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

