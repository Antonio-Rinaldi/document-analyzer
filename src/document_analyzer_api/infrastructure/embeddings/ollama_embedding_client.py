from __future__ import annotations

import httpx

from ...domain.ports.embedding_client import EmbeddingClientPort


class OllamaEmbeddingClient(EmbeddingClientPort):
    def __init__(self, base_url: str, model: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for text in texts:
                response = await client.post(
                    f"{self._base_url}/api/embeddings",
                    json={"model": self._model, "prompt": text},
                )
                response.raise_for_status()
                payload = response.json()
                vectors.append(payload.get("embedding", []))
        return vectors

