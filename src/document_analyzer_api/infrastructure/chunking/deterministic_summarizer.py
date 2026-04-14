"""Module `src/document_analyzer_api/infrastructure/chunking/deterministic_summarizer.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: DeterministicSummarizer.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from ...domain.ports.text_summarizer import TextSummarizerPort
from ...domain.models.chunking import DEFAULT_CONTEXTUAL_SUMMARY_PROMPT


class DeterministicSummarizer(TextSummarizerPort):
    """DeterministicSummarizer component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/chunking/deterministic_summarizer.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    async def summarize(self, target_text: str, context_text: str, prompt: str) -> str:
        """Asynchronous execution path for `summarize`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/chunking/deterministic_summarizer.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (join, len, split, strip) to satisfy the callable contract.
        
            Args:
                target_text: Input parameter accepted by `summarize`.
                context_text: Input parameter accepted by `summarize`.
                prompt: Input parameter accepted by `summarize`.
        
            Returns:
                A value compatible with `str`.
        """
        normalized = " ".join(target_text.split())
        if not normalized:
            return ""
        words = normalized.split(" ")
        summary_words = words[:40]
        summary = " ".join(summary_words)
        if len(words) > 40:
            summary += " ..."
        custom_prompt = prompt.strip()
        if custom_prompt and custom_prompt != DEFAULT_CONTEXTUAL_SUMMARY_PROMPT:
            summary = f"[{custom_prompt}] {summary}"
        return summary



