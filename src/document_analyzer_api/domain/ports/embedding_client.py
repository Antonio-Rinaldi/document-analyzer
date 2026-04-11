from typing import Protocol


class EmbeddingClientPort(Protocol):
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        ...

