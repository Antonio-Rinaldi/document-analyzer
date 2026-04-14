"""Detailed module documentation for `src/document_analyzer_api/domain/ports/text_generation_client.py`.

File role:
- Located in the domain port layer.
- Defines logic and symbols for `text_generation_client.py` within Document Analyzer V1.

Purpose:
- Declares abstract contracts implemented by infrastructure adapters.

Exported symbols overview:
- Classes: TextGenerationClientPort.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from typing import Protocol


class TextGenerationClientPort(Protocol):
    """Detailed class documentation for `TextGenerationClientPort`.
    
    This component belongs to `src/document_analyzer_api/domain/ports/text_generation_client.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    async def generate_answer(self, question: str, context_chunks: list[str]) -> str:
        """Detailed asynchronous function documentation for `generate_answer`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/text_generation_client.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Generates derived output from retrieved context and provided options.
        
            Args:
                question: User question or prompt text to process.
                context_chunks: Input parameter for `generate_answer`.
        
            Returns:
                Value defined by `generate_answer` contract and consumed by downstream callers.
        """
        ...

