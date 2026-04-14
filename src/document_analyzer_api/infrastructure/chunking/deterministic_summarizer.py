"""Detailed module documentation for `src/document_analyzer_api/infrastructure/chunking/deterministic_summarizer.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `deterministic_summarizer.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: DeterministicSummarizer.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from ...domain.ports.text_summarizer import TextSummarizerPort
from ...domain.models.chunking import DEFAULT_CONTEXTUAL_SUMMARY_PROMPT


class DeterministicSummarizer(TextSummarizerPort):
    """Detailed class documentation for `DeterministicSummarizer`.
    
    This component belongs to `src/document_analyzer_api/infrastructure/chunking/deterministic_summarizer.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    async def summarize(self, target_text: str, context_text: str, prompt: str) -> str:
        """Detailed asynchronous function documentation for `summarize`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/chunking/deterministic_summarizer.py` and contributes to the module workflow
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



