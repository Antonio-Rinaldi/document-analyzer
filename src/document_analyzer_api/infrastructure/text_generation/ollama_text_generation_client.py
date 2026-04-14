"""Detailed module documentation for `src/document_analyzer_api/infrastructure/text_generation/ollama_text_generation_client.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `ollama_text_generation_client.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: OllamaTextGenerationClient.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from __future__ import annotations

import httpx

from ...domain.ports.text_generation_client import TextGenerationClientPort


class OllamaTextGenerationClient(TextGenerationClientPort):
    """Detailed class documentation for `OllamaTextGenerationClient`.
    
    This component belongs to `src/document_analyzer_api/infrastructure/text_generation/ollama_text_generation_client.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, base_url: str, model: str) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/text_generation/ollama_text_generation_client.py` and contributes to the module workflow
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

    async def generate_answer(self, question: str, context_chunks: list[str]) -> str:
        """Detailed asynchronous function documentation for `generate_answer`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/text_generation/ollama_text_generation_client.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Generates derived output from retrieved context and provided options.
        
            Args:
                question: User question or prompt text to process.
                context_chunks: Input parameter for `generate_answer`.
        
            Returns:
                Value defined by `generate_answer` contract and consumed by downstream callers.
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

