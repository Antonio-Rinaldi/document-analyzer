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

    @staticmethod
    def _extract_vector(payload: dict) -> list[float]:
        """Extract a single vector from payload variants used by older providers."""
        if isinstance(payload.get("embedding"), list):
            return payload["embedding"]

        embeddings = payload.get("embeddings")
        if isinstance(embeddings, list) and embeddings:
            first = embeddings[0]
            if isinstance(first, list):
                return first
        return []

    @staticmethod
    def _is_embedding_matrix(value: object) -> bool:
        """Return whether a value is a list of numeric vectors."""
        return isinstance(value, list) and all(
            isinstance(vector, list)
            and all(isinstance(number, (int, float)) for number in vector)
            for vector in value
        )

    def _normalize_embeddings(self, payload: dict, expected_count: int) -> list[list[float]]:
        """Normalize provider payloads and enforce one embedding per input text."""
        matrix = payload.get("embeddings")
        if self._is_embedding_matrix(matrix):
            if len(matrix) != expected_count:
                raise RuntimeError(
                    "Ollama embeddings cardinality mismatch at /api/embeddings: "
                    f"expected={expected_count}, received={len(matrix)}"
                )
            return [[float(value) for value in vector] for vector in matrix]

        vector = self._extract_vector(payload)
        if expected_count == 1 and vector:
            return [[float(value) for value in vector]]

        raise RuntimeError(
            "Ollama embeddings response did not contain a valid embeddings array "
            f"for {expected_count} input text(s) at /api/embeddings."
        )

    async def _embed(self, client: httpx.AsyncClient, texts: list[str]) -> list[list[float]]:
        """Call Ollama embeddings endpoint used by runtime ingestion."""
        response = await client.post(
            f"{self._base_url}/api/embeddings",
            json={"model": self._model, "input": texts},
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            body = response.text.strip()
            raise RuntimeError(
                f"Ollama embeddings failed for model '{self._model}' at /api/embeddings: "
                f"HTTP {response.status_code} | body={body}"
            ) from exc

        payload = response.json()
        return self._normalize_embeddings(payload, len(texts))

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
        if not texts:
            return []

        async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
            return await self._embed(client, texts)

