"""Module `src/document_analyzer_api/domain/ports/embedding_client.py`.

This module belongs to the domain abstraction layer of Document Analyzer.

Purpose:
- Declares protocol contracts implemented by infrastructure adapters.

Defined symbols:
- Classes: EmbeddingClientPort.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from typing import Protocol


class EmbeddingClientPort(Protocol):
    """EmbeddingClientPort component.
    
    This class is defined in `src/document_analyzer_api/domain/ports/embedding_client.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Return embeddings aligned 1:1 with input texts.

        Implementations must preserve ordering and return exactly one vector per
        input text. Callers rely on this cardinality to persist chunk embeddings
        without ambiguity.
        """
        ...

