"""Detailed module documentation for `src/document_analyzer_api/domain/ports/text_summarizer.py`.

File role:
- Located in the domain port layer.
- Defines logic and symbols for `text_summarizer.py` within Document Analyzer V1.

Purpose:
- Declares abstract contracts implemented by infrastructure adapters.

Exported symbols overview:
- Classes: TextSummarizerPort.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from typing import Protocol


class TextSummarizerPort(Protocol):
    """Detailed class documentation for `TextSummarizerPort`.
    
    This component belongs to `src/document_analyzer_api/domain/ports/text_summarizer.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    async def summarize(self, target_text: str, context_text: str, prompt: str) -> str:
        """Detailed asynchronous function documentation for `summarize`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/text_summarizer.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                target_text: Input parameter for `summarize`.
                context_text: Input parameter for `summarize`.
                prompt: Input parameter for `summarize`.
        
            Returns:
                Value defined by `summarize` contract and consumed by downstream callers.
        """
        ...


