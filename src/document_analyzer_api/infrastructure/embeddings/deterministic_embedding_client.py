"""Module `src/document_analyzer_api/infrastructure/embeddings/deterministic_embedding_client.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: DeterministicEmbeddingClient.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import hashlib

from ...domain.ports.embedding_client import EmbeddingClientPort


class DeterministicEmbeddingClient(EmbeddingClientPort):
    """DeterministicEmbeddingClient component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/embeddings/deterministic_embedding_client.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Asynchronous execution path for `embed_texts`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/embeddings/deterministic_embedding_client.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (append, digest, encode, sha256) to satisfy the callable contract.
        
            Args:
                texts: Input parameter accepted by `embed_texts`.
        
            Returns:
                A value compatible with `list[list[float]]`.
        """
        vectors: list[list[float]] = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8", errors="ignore")).digest()
            vectors.append([byte / 255.0 for byte in digest[:16]])
        return vectors

