from __future__ import annotations

import asyncio
import importlib
from typing import Any

from ...domain.models.retrieval import KeywordsMode, RetrievalHit, RetrievalRequest
from ...domain.ports.embedding_client import EmbeddingClientPort
from ...domain.ports.retrieval_backend import RetrievalBackendPort
from .local_retrieval_backends import _rank_records


class MongoVectorRetrievalBackend(RetrievalBackendPort):
    def __init__(
        self,
        *,
        uri: str,
        database: str,
        embedding_client: EmbeddingClientPort,
        collection: str = "chunks",
        vector_index_name: str = "chunk_embedding_index",
    ) -> None:
        pymongo = importlib.import_module("pymongo")
        self._client = pymongo.MongoClient(uri)
        self._collection = self._client[database][collection]
        self._embedding_client = embedding_client
        self._vector_index_name = vector_index_name

    async def retrieve(self, request: RetrievalRequest) -> list[RetrievalHit]:
        try:
            query_embedding = (await self._embedding_client.embed_texts([request.query]))[0]
            return await asyncio.to_thread(self._vector_search, request, query_embedding)
        except Exception:
            # Fallback keeps real mode operational when vector search index is not available yet.
            records = await asyncio.to_thread(self._read_committed)
            return _rank_records(records, request, mode="vector")

    def _read_committed(self) -> list[dict[str, Any]]:
        return list(self._collection.find({"status": "committed"}, {"_id": 0}))

    def _vector_search(self, request: RetrievalRequest, query_embedding: list[float]) -> list[RetrievalHit]:
        filter_query: dict[str, Any] = {"status": "committed"}
        if request.document_ids is not None:
            filter_query["document_id"] = {"$in": request.document_ids}

        pipeline: list[dict[str, Any]] = [
            {
                "$vectorSearch": {
                    "index": self._vector_index_name,
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": max(request.top_k * 20, 80),
                    "limit": max(request.top_k * 4, request.top_k),
                    "filter": filter_query,
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "document_id": 1,
                    "chunk_id": 1,
                    "content": 1,
                    "metadata": 1,
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]

        docs = list(self._collection.aggregate(pipeline))
        return self._hits_from_docs(docs, request)

    def _hits_from_docs(self, docs: list[dict[str, Any]], request: RetrievalRequest) -> list[RetrievalHit]:
        hits: list[RetrievalHit] = []
        for doc in docs:
            metadata = doc.get("metadata") if isinstance(doc.get("metadata"), dict) else {}
            content = str(doc.get("content", ""))
            score = float(doc.get("score", 0.0))

            if request.keywords and request.keywords_mode == KeywordsMode.filter:
                if not _contains_all_keywords(content, metadata, request.keywords):
                    continue

            if request.keywords and request.keywords_mode == KeywordsMode.rank_boost:
                score += 0.05 * _keyword_match_count(content, metadata, request.keywords)

            if score < request.min_score:
                continue

            hits.append(
                RetrievalHit(
                    document_id=str(doc.get("document_id", "")),
                    chunk_id=str(doc.get("chunk_id", "")),
                    content=content,
                    score=score,
                    metadata=metadata,
                )
            )

        hits.sort(key=lambda item: item.score, reverse=True)
        return hits[: request.top_k]


def _contains_all_keywords(content: str, metadata: dict[str, Any], keywords: list[str]) -> bool:
    text = (content + " " + str(metadata)).lower()
    return all(keyword.lower() in text for keyword in keywords)


def _keyword_match_count(content: str, metadata: dict[str, Any], keywords: list[str]) -> int:
    text = (content + " " + str(metadata)).lower()
    return sum(1 for keyword in keywords if keyword.lower() in text)

