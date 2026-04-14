"""Module `src/document_analyzer_api/infrastructure/text_generation/ollama_text_generation_client.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: OllamaTextGenerationClient.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from __future__ import annotations

import httpx

from ...domain.ports.text_generation_client import TextGenerationClientPort


class OllamaTextGenerationClient(TextGenerationClientPort):
    """OllamaTextGenerationClient component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/text_generation/ollama_text_generation_client.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, base_url: str, model: str) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/text_generation/ollama_text_generation_client.py` and contributes to module-level behavior
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

    async def generate_answer(self, question: str, context_chunks: list[str]) -> str:
        """Asynchronous execution path for `generate_answer`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/text_generation/ollama_text_generation_client.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Generates derived output from context, prompts, and generation options.
        
            Args:
                question: User prompt processed by retrieval and generation workflows.
                context_chunks: Input parameter accepted by `generate_answer`.
        
            Returns:
                A value compatible with `str`.
        """
        context = "\n\n".join(context_chunks[:8])
        prompt = (
            "Answer the question using only the provided context. "
            "If evidence is insufficient, answer exactly: "
            "I cannot find enough support in selected documents.\n\n"
            f"Question:\n{question}\n\n"
            f"Context:\n{context}\n"
        )
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self._base_url}/api/generate",
                json={"model": self._model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            payload = response.json()
            return str(payload.get("response", "")).strip()

