"""Module `src/document_analyzer_api/infrastructure/chunking/ollama_summarizer.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: OllamaSummarizer.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from __future__ import annotations

import httpx

from ...domain.ports.text_summarizer import TextSummarizerPort


class OllamaSummarizer(TextSummarizerPort):
    """OllamaSummarizer component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/chunking/ollama_summarizer.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, base_url: str, model: str) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/chunking/ollama_summarizer.py` and contributes to module-level behavior
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

    async def summarize(self, target_text: str, context_text: str, prompt: str) -> str:
        """Asynchronous execution path for `summarize`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/chunking/ollama_summarizer.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (AsyncClient, get, json, post) to satisfy the callable contract.
        
            Args:
                target_text: Input parameter accepted by `summarize`.
                context_text: Input parameter accepted by `summarize`.
                prompt: Input parameter accepted by `summarize`.
        
            Returns:
                A value compatible with `str`.
        """
        final_prompt = (
            f"{prompt}\n\n"
            "Use only the provided context. Summarize the target text accordingly.\n\n"
            f"Context:\n{context_text}\n\n"
            f"Target:\n{target_text}\n"
        )
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self._base_url}/api/generate",
                json={"model": self._model, "prompt": final_prompt, "stream": False},
            )
            response.raise_for_status()
            payload = response.json()
            return str(payload.get("response", "")).strip()

