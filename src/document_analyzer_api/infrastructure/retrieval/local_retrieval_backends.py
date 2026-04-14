"""Detailed module documentation for `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `local_retrieval_backends.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: LocalVectorRetrievalBackend, LocalGraphRetrievalBackend, LocalHybridRetrievalBackend.
- Functions: _load_records, _rank_records, _contains_all_keywords, _keyword_match_count, _similarity, _graphish_connectivity_bonus, _tokenize.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

import asyncio
import json
import math
from pathlib import Path
from typing import Any

from ...domain.models.retrieval import KeywordsMode, RetrievalHit, RetrievalRequest
from ...domain.ports.retrieval_backend import RetrievalBackendPort


class LocalVectorRetrievalBackend(RetrievalBackendPort):
    """Detailed class documentation for `LocalVectorRetrievalBackend`.
    
    This component belongs to `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, root_path: str, source_file: str = "mongo_chunks.json") -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                root_path: Input parameter for `__init__`.
                source_file: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._path = Path(root_path) / source_file

    async def retrieve(self, request: RetrievalRequest) -> list[RetrievalHit]:
        """Detailed asynchronous function documentation for `retrieve`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes retrieval strategy selection and returns matching evidence chunks.
        
            Args:
                request: Incoming request object carrying path/query/body/context information.
        
            Returns:
                Value defined by `retrieve` contract and consumed by downstream callers.
        """
        records = await _load_records(self._path)
        return _rank_records(records, request, mode="vector")


class LocalGraphRetrievalBackend(RetrievalBackendPort):
    """Detailed class documentation for `LocalGraphRetrievalBackend`.
    
    This component belongs to `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, root_path: str, source_file: str = "neo4j_chunks.json") -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                root_path: Input parameter for `__init__`.
                source_file: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._path = Path(root_path) / source_file

    async def retrieve(self, request: RetrievalRequest) -> list[RetrievalHit]:
        """Detailed asynchronous function documentation for `retrieve`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes retrieval strategy selection and returns matching evidence chunks.
        
            Args:
                request: Incoming request object carrying path/query/body/context information.
        
            Returns:
                Value defined by `retrieve` contract and consumed by downstream callers.
        """
        records = await _load_records(self._path)
        return _rank_records(records, request, mode="graph")


class LocalHybridRetrievalBackend(RetrievalBackendPort):
    """Detailed class documentation for `LocalHybridRetrievalBackend`.
    
    This component belongs to `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, root_path: str) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                root_path: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._vector = LocalVectorRetrievalBackend(root_path=root_path, source_file="mongo_chunks.json")
        self._graph = LocalGraphRetrievalBackend(root_path=root_path, source_file="neo4j_chunks.json")

    async def retrieve(self, request: RetrievalRequest) -> list[RetrievalHit]:
        """Detailed asynchronous function documentation for `retrieve`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes retrieval strategy selection and returns matching evidence chunks.
        
            Args:
                request: Incoming request object carrying path/query/body/context information.
        
            Returns:
                Value defined by `retrieve` contract and consumed by downstream callers.
        """
        vector_hits = await self._vector.retrieve(request)
        graph_hits = await self._graph.retrieve(request)

        fused: dict[tuple[str, str], RetrievalHit] = {}
        for hit in vector_hits:
            fused[(hit.document_id, hit.chunk_id)] = RetrievalHit(
                document_id=hit.document_id,
                chunk_id=hit.chunk_id,
                content=hit.content,
                score=request.hybrid_alpha * hit.score,
                metadata={**hit.metadata},
            )

        for hit in graph_hits:
            key = (hit.document_id, hit.chunk_id)
            if key in fused:
                fused[key].score += (1.0 - request.hybrid_alpha) * hit.score
            else:
                fused[key] = RetrievalHit(
                    document_id=hit.document_id,
                    chunk_id=hit.chunk_id,
                    content=hit.content,
                    score=(1.0 - request.hybrid_alpha) * hit.score,
                    metadata={**hit.metadata},
                )

        result = sorted(fused.values(), key=lambda item: item.score, reverse=True)
        return result[: request.top_k]


async def _load_records(path: Path) -> list[dict[str, Any]]:
    """Detailed asynchronous function documentation for `_load_records`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            path: Filesystem path argument used by the callable.
    
        Returns:
            Value defined by `_load_records` contract and consumed by downstream callers.
    """
    def _read() -> list[dict[str, Any]]:
        """Detailed synchronous function documentation for `_read`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `_read` contract and consumed by downstream callers.
        """
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        return [item for item in data if item.get("status") == "committed"]

    return await asyncio.to_thread(_read)


def _rank_records(records: list[dict[str, Any]], request: RetrievalRequest, mode: str) -> list[RetrievalHit]:
    """Detailed synchronous function documentation for `_rank_records`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            records: Input parameter for `_rank_records`.
            request: Incoming request object carrying path/query/body/context information.
            mode: Input parameter for `_rank_records`.
    
        Returns:
            Value defined by `_rank_records` contract and consumed by downstream callers.
    """
    ranked: list[RetrievalHit] = []
    for record in records:
        if request.document_ids is not None and record.get("document_id") not in request.document_ids:
            continue

        content = record.get("content", "")
        metadata = record.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}

        if request.keywords and request.keywords_mode == KeywordsMode.filter:
            if not _contains_all_keywords(content, metadata, request.keywords):
                continue

        score = _similarity(request.query, content)
        if mode == "graph":
            section_title = str(metadata.get("sectionTitle", "")).lower()
            if section_title and section_title in request.query.lower():
                score += 0.25
            score += 0.05 * _graphish_connectivity_bonus(metadata)

        if request.keywords and request.keywords_mode == KeywordsMode.rank_boost:
            score += 0.05 * _keyword_match_count(content, metadata, request.keywords)

        if score < request.min_score:
            continue

        ranked.append(
            RetrievalHit(
                document_id=record.get("document_id", ""),
                chunk_id=record.get("chunk_id", ""),
                content=content,
                score=score,
                metadata=metadata,
            )
        )

    ranked.sort(key=lambda item: item.score, reverse=True)
    return ranked[: request.top_k]


def _contains_all_keywords(content: str, metadata: dict[str, Any], keywords: list[str]) -> bool:
    """Detailed synchronous function documentation for `_contains_all_keywords`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to the module workflow
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
    text = (content + " " + json.dumps(metadata)).lower()
    return all(keyword.lower() in text for keyword in keywords)


def _keyword_match_count(content: str, metadata: dict[str, Any], keywords: list[str]) -> int:
    """Detailed synchronous function documentation for `_keyword_match_count`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to the module workflow
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
    text = (content + " " + json.dumps(metadata)).lower()
    return sum(1 for keyword in keywords if keyword.lower() in text)


def _similarity(query: str, content: str) -> float:
    """Detailed synchronous function documentation for `_similarity`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            query: Input parameter for `_similarity`.
            content: Raw payload bytes or text handled by the callable.
    
        Returns:
            Value defined by `_similarity` contract and consumed by downstream callers.
    """
    query_tokens = _tokenize(query)
    content_tokens = _tokenize(content)
    if not query_tokens or not content_tokens:
        return 0.0

    overlap = len(query_tokens.intersection(content_tokens))
    # Slightly softened cosine-like normalization for short chunks.
    return overlap / math.sqrt(len(query_tokens) * len(content_tokens))


def _graphish_connectivity_bonus(metadata: dict[str, Any]) -> int:
    """Detailed synchronous function documentation for `_graphish_connectivity_bonus`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            metadata: Input parameter for `_graphish_connectivity_bonus`.
    
        Returns:
            Value defined by `_graphish_connectivity_bonus` contract and consumed by downstream callers.
    """
    connections = metadata.get("connections")
    if isinstance(connections, list):
        return len(connections)
    return 0


def _tokenize(text: str) -> set[str]:
    """Detailed synchronous function documentation for `_tokenize`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            text: Input parameter for `_tokenize`.
    
        Returns:
            Value defined by `_tokenize` contract and consumed by downstream callers.
    """
    return {item for item in text.lower().replace("\n", " ").split(" ") if item}

