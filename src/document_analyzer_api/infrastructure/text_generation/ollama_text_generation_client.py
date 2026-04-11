from __future__ import annotations

import httpx

from ...domain.ports.text_generation_client import TextGenerationClientPort


class OllamaTextGenerationClient(TextGenerationClientPort):
    def __init__(self, base_url: str, model: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    async def generate_answer(self, question: str, context_chunks: list[str]) -> str:
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

