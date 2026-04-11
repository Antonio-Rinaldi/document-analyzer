import hashlib

from ...domain.ports.embedding_client import EmbeddingClientPort


class DeterministicEmbeddingClient(EmbeddingClientPort):
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8", errors="ignore")).digest()
            vectors.append([byte / 255.0 for byte in digest[:16]])
        return vectors

