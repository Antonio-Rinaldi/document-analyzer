"""Module `src/document_analyzer_api/infrastructure/retrieval/neo4j_graph_retrieval_backend.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: Neo4jGraphRetrievalBackend.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from ...domain.models.retrieval import RetrievalHit, RetrievalRequest
from ...domain.ports.retrieval_backend import RetrievalBackendPort
from .local_retrieval_backends import _rank_records


class Neo4jGraphRetrievalBackend(RetrievalBackendPort):
    """Neo4jGraphRetrievalBackend component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/retrieval/neo4j_graph_retrieval_backend.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    _MIN_GRAPH_HOPS = 1
    _MAX_GRAPH_HOPS = 32

    def __init__(self, uri: str, user: str, password: str) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/neo4j_graph_retrieval_backend.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (driver) to satisfy the callable contract.
        
            Args:
                uri: Input parameter accepted by `__init__`.
                user: Input parameter accepted by `__init__`.
                password: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        from neo4j import GraphDatabase

        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    async def retrieve(self, request: RetrievalRequest) -> list[RetrievalHit]:
        """Asynchronous execution path for `retrieve`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/neo4j_graph_retrieval_backend.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes retrieval strategy selection and returns ranked evidence chunks.
        
            Args:
                request: Incoming HTTP request carrying route/query/body/context data.
        
            Returns:
                A value compatible with `list[RetrievalHit]`.
        """
        records = await asyncio.to_thread(self._read_committed, request)
        return _rank_records(records, request, mode="graph")

    def _read_committed(self, request: RetrievalRequest) -> list[dict[str, Any]]:
        """Synchronous execution path for `_read_committed`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/neo4j_graph_retrieval_backend.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (append, get, isinstance, run) to satisfy the callable contract.
        
            Args:
                None.
        
            Returns:
                A value compatible with `list[dict[str, Any]]`.
        """
        max_hops = self._normalize_graph_hops(request.graph_max_hops)
        query = self._build_committed_chunks_query(max_hops)
        with self._driver.session() as session:
            rows = session.run(query)
            records: list[dict[str, Any]] = []
            for row in rows:
                metadata = self._decode_metadata(
                    metadata_json=row.get("metadata_json"),
                )
                metadata = self._merge_graph_metadata(metadata=metadata, row=row)
                records.append(
                    {
                        "document_id": row.get("document_id", ""),
                        "chunk_id": row.get("chunk_id", ""),
                        "content": row.get("content", ""),
                        "metadata": metadata,
                    }
                )
            return records

    @classmethod
    def _normalize_graph_hops(cls, value: int) -> int:
        """Clamp traversal depth to a Neo4j-safe positive integer range."""
        return max(cls._MIN_GRAPH_HOPS, min(value, cls._MAX_GRAPH_HOPS))

    @staticmethod
    def _build_committed_chunks_query(max_hops: int) -> str:
        """Build a committed-chunk traversal query with literal hop depth.

        Neo4j does not allow query parameters in variable-length relationship
        ranges (`*1..N`), so the depth must be rendered as a validated literal.
        """
        return (
            "MATCH (d:Document)-[:HAS_CHAPTER]->(ch:Chapter)-[:HAS_PARAGRAPH]->(p:Paragraph)-[:HAS_CHUNK]->(c:Chunk) "
            "WHERE c.status = 'committed' "
            f"OPTIONAL MATCH path = (c)-[:NEXT|HAS_CHUNK|HAS_PARAGRAPH|HAS_CHAPTER*1..{max_hops}]-(neighbor:Chunk) "
            "WHERE neighbor.status = 'committed' AND neighbor.id <> c.id "
            "RETURN d.id AS document_id, c.id AS chunk_id, c.content AS content, c.metadataJson AS metadata_json, "
            "ch.id AS chapter_id, ch.title AS chapter_title, p.id AS paragraph_id, p.paragraphIndex AS paragraph_index, "
            "collect(DISTINCT neighbor.id) AS connections, count(DISTINCT path) AS graph_path_count, "
            "coalesce(min(length(path)), 0) AS graph_min_depth "
        )

    @staticmethod
    def _merge_graph_metadata(metadata: dict[str, Any], row: Any) -> dict[str, Any]:
        """Merge hierarchy and connectivity fields into decoded metadata for graph ranking."""
        merged = {**metadata}
        merged["connections"] = [item for item in row.get("connections", []) if isinstance(item, str)]
        merged["graphPathCount"] = row.get("graph_path_count", 0)
        merged["graphMinDepth"] = row.get("graph_min_depth", 0)
        chapter_id = row.get("chapter_id")
        if chapter_id:
            merged.setdefault("chapterId", chapter_id)
        chapter_title = row.get("chapter_title")
        if chapter_title:
            merged.setdefault("chapterTitle", chapter_title)
            merged.setdefault("sectionTitle", chapter_title)
        paragraph_id = row.get("paragraph_id")
        if paragraph_id:
            merged.setdefault("paragraphId", paragraph_id)
        paragraph_index = row.get("paragraph_index")
        if paragraph_index is not None:
            merged.setdefault("paragraphIndex", paragraph_index)
        return merged

    @staticmethod
    def _decode_metadata(metadata_json: Any) -> dict[str, Any]:
        """Decode metadata from Neo4j row values into a normalized dictionary.

        The modern storage format persists metadata into `metadataJson` as a serialized JSON object.
        Retrieval decodes that payload and always returns a dictionary for downstream ranking/citation logic.
        """
        if isinstance(metadata_json, str) and metadata_json.strip():
            try:
                parsed = json.loads(metadata_json)
            except json.JSONDecodeError:
                return {}
            return parsed if isinstance(parsed, dict) else {}
        return {}

