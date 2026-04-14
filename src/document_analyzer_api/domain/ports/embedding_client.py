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
        """Asynchronous execution path for `embed_texts`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/embedding_client.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                texts: Input parameter accepted by `embed_texts`.
        
            Returns:
                A value compatible with `list[list[float]]`.
        """
        ...

