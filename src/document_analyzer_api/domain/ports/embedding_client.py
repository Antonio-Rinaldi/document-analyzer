"""Detailed module documentation for `src/document_analyzer_api/domain/ports/embedding_client.py`.

File role:
- Located in the domain port layer.
- Defines logic and symbols for `embedding_client.py` within Document Analyzer V1.

Purpose:
- Declares abstract contracts implemented by infrastructure adapters.

Exported symbols overview:
- Classes: EmbeddingClientPort.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from typing import Protocol


class EmbeddingClientPort(Protocol):
    """Detailed class documentation for `EmbeddingClientPort`.
    
    This component belongs to `src/document_analyzer_api/domain/ports/embedding_client.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Detailed asynchronous function documentation for `embed_texts`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/embedding_client.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                texts: Input parameter for `embed_texts`.
        
            Returns:
                Value defined by `embed_texts` contract and consumed by downstream callers.
        """
        ...

