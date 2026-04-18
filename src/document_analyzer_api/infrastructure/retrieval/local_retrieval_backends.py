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
        hit = _rank_record(record=record, request=request, mode=mode)
        if hit is not None:
            ranked.append(hit)

    ranked.sort(key=lambda item: item.score, reverse=True)
    return ranked[: request.top_k]


def _rank_record(record: dict[str, Any], request: RetrievalRequest, mode: str) -> RetrievalHit | None:
    """Rank one retrieval record and return a hit only when all filters and score thresholds pass."""
    if not _record_matches_document_scope(record=record, request=request):
        return None
    content = str(record.get("content", ""))
    metadata = _normalize_metadata(record.get("metadata"))
    if _is_filtered_by_keywords(content=content, metadata=metadata, request=request):
        return None
    score = _score_record(content=content, metadata=metadata, request=request, mode=mode)
    if score < request.min_score:
        return None
    return RetrievalHit(
        document_id=str(record.get("document_id", "")),
        chunk_id=str(record.get("chunk_id", "")),
        content=content,
        score=score,
        metadata=metadata,
    )


def _record_matches_document_scope(record: dict[str, Any], request: RetrievalRequest) -> bool:
    """Check whether a record belongs to the caller-selected document scope."""
    if request.document_ids is None:
        return True
    return record.get("document_id") in request.document_ids


def _normalize_metadata(raw_metadata: Any) -> dict[str, Any]:
    """Normalize arbitrary metadata payloads to dictionaries expected by ranking helpers."""
    return raw_metadata if isinstance(raw_metadata, dict) else {}


def _is_filtered_by_keywords(content: str, metadata: dict[str, Any], request: RetrievalRequest) -> bool:
    """Apply strict keyword filter mode semantics."""
    if not request.keywords or request.keywords_mode != KeywordsMode.filter:
        return False
    return not _contains_all_keywords(content, metadata, request.keywords)


def _score_record(content: str, metadata: dict[str, Any], request: RetrievalRequest, mode: str) -> float:
    """Compute ranking score from lexical similarity plus mode-specific and keyword boosts."""
    score = _similarity(request.query, content)
    if mode == "graph":
        score += _graph_mode_score_boost(metadata=metadata, query=request.query)
    if request.keywords and request.keywords_mode == KeywordsMode.rank_boost:
        score += 0.05 * _keyword_match_count(content, metadata, request.keywords)
    return score


def _graph_mode_score_boost(*, metadata: dict[str, Any], query: str) -> float:
    """Return graph-specific ranking boost derived from section title and connectivity metadata."""
    section_title = str(metadata.get("sectionTitle", "")).lower()
    section_title_boost = 0.25 if section_title and section_title in query.lower() else 0.0
    connectivity_boost = 0.05 * _graphish_connectivity_bonus(metadata)
    return section_title_boost + connectivity_boost


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


def _graphish_connectivity_bonus(metadata: dict[str, Any]) -> float:
    """Synchronous execution path for `_graphish_connectivity_bonus`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/local_retrieval_backends.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (float, get, isinstance, len, min) to satisfy the callable contract.
    
        Args:
            metadata: Input parameter accepted by `_graphish_connectivity_bonus`.
    
        Returns:
            A value compatible with `float`.
    """
    connections = metadata.get("connections")
    connection_count = len(connections) if isinstance(connections, list) else 0
    graph_path_count = min(_to_non_negative_int(metadata.get("graphPathCount")), 20)
    graph_min_depth = _to_non_negative_int(metadata.get("graphMinDepth"))
    depth_bonus = 0.5 if graph_min_depth <= 0 else 1.0 / float(graph_min_depth)
    return float(connection_count) + (0.5 * float(graph_path_count)) + depth_bonus


def _to_non_negative_int(value: Any) -> int:
    """Convert arbitrary metadata values into a non-negative integer."""
    try:
        return max(int(value), 0)
    except (TypeError, ValueError):
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

