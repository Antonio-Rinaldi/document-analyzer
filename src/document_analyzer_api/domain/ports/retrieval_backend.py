from typing import Protocol

from ..models.retrieval import RetrievalHit, RetrievalRequest


class RetrievalBackendPort(Protocol):
    async def retrieve(self, request: RetrievalRequest) -> list[RetrievalHit]:
        ...

