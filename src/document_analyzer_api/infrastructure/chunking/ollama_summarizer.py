from __future__ import annotations

import httpx

from ...domain.ports.text_summarizer import TextSummarizerPort


class OllamaSummarizer(TextSummarizerPort):
    def __init__(self, base_url: str, model: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    async def summarize(self, target_text: str, context_text: str, prompt: str) -> str:
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

