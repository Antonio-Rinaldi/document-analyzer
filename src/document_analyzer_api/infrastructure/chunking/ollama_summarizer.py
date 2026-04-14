"""Detailed module documentation for `src/document_analyzer_api/infrastructure/chunking/ollama_summarizer.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `ollama_summarizer.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: OllamaSummarizer.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from __future__ import annotations

import httpx

from ...domain.ports.text_summarizer import TextSummarizerPort


class OllamaSummarizer(TextSummarizerPort):
    """Detailed class documentation for `OllamaSummarizer`.
    
    This component belongs to `src/document_analyzer_api/infrastructure/chunking/ollama_summarizer.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, base_url: str, model: str) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/chunking/ollama_summarizer.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                base_url: Input parameter for `__init__`.
                model: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._base_url = base_url.rstrip("/")
        self._model = model

    async def summarize(self, target_text: str, context_text: str, prompt: str) -> str:
        """Detailed asynchronous function documentation for `summarize`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/chunking/ollama_summarizer.py` and contributes to the module workflow
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

