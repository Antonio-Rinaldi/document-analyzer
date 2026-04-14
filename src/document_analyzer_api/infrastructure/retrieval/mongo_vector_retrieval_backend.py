"""Detailed module documentation for `src/document_analyzer_api/infrastructure/retrieval/mongo_vector_retrieval_backend.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `mongo_vector_retrieval_backend.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: MongoVectorRetrievalBackend.
- Functions: _contains_all_keywords, _keyword_match_count.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from __future__ import annotations

import asyncio
import importlib
from typing import Any

from ...domain.models.retrieval import KeywordsMode, RetrievalHit, RetrievalRequest
from ...domain.ports.embedding_client import EmbeddingClientPort
from ...domain.ports.retrieval_backend import RetrievalBackendPort
from .local_retrieval_backends import _rank_records


class MongoVectorRetrievalBackend(RetrievalBackendPort):
    """Detailed class documentation for `MongoVectorRetrievalBackend`.
    
    This component belongs to `src/document_analyzer_api/infrastructure/retrieval/mongo_vector_retrieval_backend.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(
        self,
        *,
        uri: str,
        database: str,
        embedding_client: EmbeddingClientPort,
        collection: str = "chunks",
        vector_index_name: str = "chunk_embedding_index",
    ) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/mongo_vector_retrieval_backend.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                uri: Input parameter for `__init__`.
                database: Input parameter for `__init__`.
                embedding_client: Input parameter for `__init__`.
                collection: Input parameter for `__init__`.
                vector_index_name: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        pymongo = importlib.import_module("pymongo")
        self._client = pymongo.MongoClient(uri)
        self._collection = self._client[database][collection]
        self._embedding_client = embedding_client
        self._vector_index_name = vector_index_name

    async def retrieve(self, request: RetrievalRequest) -> list[RetrievalHit]:
        """Detailed asynchronous function documentation for `retrieve`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/mongo_vector_retrieval_backend.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes retrieval strategy selection and returns matching evidence chunks.
        
            Args:
                request: Incoming request object carrying path/query/body/context information.
        
            Returns:
                Value defined by `retrieve` contract and consumed by downstream callers.
        """
        try:
            query_embedding = (await self._embedding_client.embed_texts([request.query]))[0]
            return await asyncio.to_thread(self._vector_search, request, query_embedding)
        except Exception:
            # Fallback keeps real mode operational when vector search index is not available yet.
            records = await asyncio.to_thread(self._read_committed)
            return _rank_records(records, request, mode="vector")

    def _read_committed(self) -> list[dict[str, Any]]:
        """Detailed synchronous function documentation for `_read_committed`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/mongo_vector_retrieval_backend.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `_read_committed` contract and consumed by downstream callers.
        """
        return list(self._collection.find({"status": "committed"}, {"_id": 0}))

    def _vector_search(self, request: RetrievalRequest, query_embedding: list[float]) -> list[RetrievalHit]:
        """Detailed synchronous function documentation for `_vector_search`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/mongo_vector_retrieval_backend.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                request: Incoming request object carrying path/query/body/context information.
                query_embedding: Input parameter for `_vector_search`.
        
            Returns:
                Value defined by `_vector_search` contract and consumed by downstream callers.
        """
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
        """Detailed synchronous function documentation for `_hits_from_docs`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/mongo_vector_retrieval_backend.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                docs: Input parameter for `_hits_from_docs`.
                request: Incoming request object carrying path/query/body/context information.
        
            Returns:
                Value defined by `_hits_from_docs` contract and consumed by downstream callers.
        """
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
    """Detailed synchronous function documentation for `_contains_all_keywords`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/mongo_vector_retrieval_backend.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            content: Raw payload bytes or text handled by the callable.
            metadata: Input parameter for `_contains_all_keywords`.
            keywords: Optional keyword list used by retrieval behavior.
    
        Returns:
            Value defined by `_contains_all_keywords` contract and consumed by downstream callers.
    """
    text = (content + " " + str(metadata)).lower()
    return all(keyword.lower() in text for keyword in keywords)


def _keyword_match_count(content: str, metadata: dict[str, Any], keywords: list[str]) -> int:
    """Detailed synchronous function documentation for `_keyword_match_count`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/mongo_vector_retrieval_backend.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            content: Raw payload bytes or text handled by the callable.
            metadata: Input parameter for `_keyword_match_count`.
            keywords: Optional keyword list used by retrieval behavior.
    
        Returns:
            Value defined by `_keyword_match_count` contract and consumed by downstream callers.
    """
    text = (content + " " + str(metadata)).lower()
    return sum(1 for keyword in keywords if keyword.lower() in text)

