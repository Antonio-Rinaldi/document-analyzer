"""Module `src/document_analyzer_api/domain/ports/text_summarizer.py`.

This module belongs to the domain abstraction layer of Document Analyzer.

Purpose:
- Declares protocol contracts implemented by infrastructure adapters.

Defined symbols:
- Classes: TextSummarizerPort.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from typing import Protocol


class TextSummarizerPort(Protocol):
    """TextSummarizerPort component.
    
    This class is defined in `src/document_analyzer_api/domain/ports/text_summarizer.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    async def summarize(self, target_text: str, context_text: str, prompt: str) -> str:
        """Asynchronous execution path for `summarize`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/text_summarizer.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                target_text: Input parameter accepted by `summarize`.
                context_text: Input parameter accepted by `summarize`.
                prompt: Input parameter accepted by `summarize`.
        
            Returns:
                A value compatible with `str`.
        """
        ...


