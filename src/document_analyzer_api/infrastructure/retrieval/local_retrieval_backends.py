"""Module `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: LocalVectorRetrievalBackend, LocalGraphRetrievalBackend, LocalHybridRetrievalBackend.
- Functions: _rank_records, _contains_all_keywords, _keyword_match_count, _similarity, _graphish_connectivity_bonus, _tokenize, _load_records.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import asyncio
import json
import math
from pathlib import Path
from typing import Any

from ...domain.models.retrieval import KeywordsMode, RetrievalHit, RetrievalRequest
from ...domain.ports.retrieval_backend import RetrievalBackendPort


class LocalVectorRetrievalBackend(RetrievalBackendPort):
    """LocalVectorRetrievalBackend component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, root_path: str, source_file: str = "mongo_chunks.json") -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (Path) to satisfy the callable contract.
        
            Args:
                root_path: Input parameter accepted by `__init__`.
                source_file: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._path = Path(root_path) / source_file

    async def retrieve(self, request: RetrievalRequest) -> list[RetrievalHit]:
        """Asynchronous execution path for `retrieve`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes retrieval strategy selection and returns ranked evidence chunks.
        
            Args:
                request: Incoming HTTP request carrying route/query/body/context data.
        
            Returns:
                A value compatible with `list[RetrievalHit]`.
        """
        records = await _load_records(self._path)
        return _rank_records(records, request, mode="vector")


class LocalGraphRetrievalBackend(RetrievalBackendPort):
    """LocalGraphRetrievalBackend component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, root_path: str, source_file: str = "neo4j_chunks.json") -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (Path) to satisfy the callable contract.
        
            Args:
                root_path: Input parameter accepted by `__init__`.
                source_file: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._path = Path(root_path) / source_file

    async def retrieve(self, request: RetrievalRequest) -> list[RetrievalHit]:
        """Asynchronous execution path for `retrieve`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes retrieval strategy selection and returns ranked evidence chunks.
        
            Args:
                request: Incoming HTTP request carrying route/query/body/context data.
        
            Returns:
                A value compatible with `list[RetrievalHit]`.
        """
        records = await _load_records(self._path)
        return _rank_records(records, request, mode="graph")


class LocalHybridRetrievalBackend(RetrievalBackendPort):
    """LocalHybridRetrievalBackend component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, root_path: str) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (LocalGraphRetrievalBackend, LocalVectorRetrievalBackend) to satisfy the callable contract.
        
            Args:
                root_path: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._vector = LocalVectorRetrievalBackend(root_path=root_path, source_file="mongo_chunks.json")
        self._graph = LocalGraphRetrievalBackend(root_path=root_path, source_file="neo4j_chunks.json")

    async def retrieve(self, request: RetrievalRequest) -> list[RetrievalHit]:
        """Asynchronous execution path for `retrieve`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes retrieval strategy selection and returns ranked evidence chunks.
        
            Args:
                request: Incoming HTTP request carrying route/query/body/context data.
        
            Returns:
                A value compatible with `list[RetrievalHit]`.
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
    """Asynchronous execution path for `_load_records`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (exists, get, loads, read_text) to satisfy the callable contract.
    
        Args:
            path: Filesystem path handled by this callable.
    
        Returns:
            A value compatible with `list[dict[str, Any]]`.
    """
    def _read() -> list[dict[str, Any]]:
        """Synchronous execution path for `_read`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (exists, get, loads, read_text) to satisfy the callable contract.
        
            Args:
                None.
        
            Returns:
                A value compatible with `list[dict[str, Any]]`.
        """
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        return [item for item in data if item.get("status") == "committed"]

    return await asyncio.to_thread(_read)


def _rank_records(records: list[dict[str, Any]], request: RetrievalRequest, mode: str) -> list[RetrievalHit]:
    """Synchronous execution path for `_rank_records`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (RetrievalHit, _contains_all_keywords, _graphish_connectivity_bonus, _keyword_match_count) to satisfy the callable contract.
    
        Args:
            records: Input parameter accepted by `_rank_records`.
            request: Incoming HTTP request carrying route/query/body/context data.
            mode: Input parameter accepted by `_rank_records`.
    
        Returns:
            A value compatible with `list[RetrievalHit]`.
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
    """Synchronous execution path for `_contains_all_keywords`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (all, dumps, lower) to satisfy the callable contract.
    
        Args:
            content: Raw payload bytes/text processed or transformed by this callable.
            metadata: Input parameter accepted by `_contains_all_keywords`.
            keywords: Optional keyword list used for retrieval metadata/filtering/boosting.
    
        Returns:
            A value compatible with `bool`.
    """
    text = (content + " " + json.dumps(metadata)).lower()
    return all(keyword.lower() in text for keyword in keywords)


def _keyword_match_count(content: str, metadata: dict[str, Any], keywords: list[str]) -> int:
    """Synchronous execution path for `_keyword_match_count`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (dumps, lower, sum) to satisfy the callable contract.
    
        Args:
            content: Raw payload bytes/text processed or transformed by this callable.
            metadata: Input parameter accepted by `_keyword_match_count`.
            keywords: Optional keyword list used for retrieval metadata/filtering/boosting.
    
        Returns:
            A value compatible with `int`.
    """
    text = (content + " " + json.dumps(metadata)).lower()
    return sum(1 for keyword in keywords if keyword.lower() in text)


def _similarity(query: str, content: str) -> float:
    """Synchronous execution path for `_similarity`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (_tokenize, intersection, len, sqrt) to satisfy the callable contract.
    
        Args:
            query: Input parameter accepted by `_similarity`.
            content: Raw payload bytes/text processed or transformed by this callable.
    
        Returns:
            A value compatible with `float`.
    """
    query_tokens = _tokenize(query)
    content_tokens = _tokenize(content)
    if not query_tokens or not content_tokens:
        return 0.0

    overlap = len(query_tokens.intersection(content_tokens))
    # Slightly softened cosine-like normalization for short chunks.
    return overlap / math.sqrt(len(query_tokens) * len(content_tokens))


def _graphish_connectivity_bonus(metadata: dict[str, Any]) -> int:
    """Synchronous execution path for `_graphish_connectivity_bonus`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (get, isinstance, len) to satisfy the callable contract.
    
        Args:
            metadata: Input parameter accepted by `_graphish_connectivity_bonus`.
    
        Returns:
            A value compatible with `int`.
    """
    connections = metadata.get("connections")
    if isinstance(connections, list):
        return len(connections)
    return 0


def _tokenize(text: str) -> set[str]:
    """Synchronous execution path for `_tokenize`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (lower, replace, split) to satisfy the callable contract.
    
        Args:
            text: Input parameter accepted by `_tokenize`.
    
        Returns:
            A value compatible with `set[str]`.
    """
    return {item for item in text.lower().replace("\n", " ").split(" ") if item}

