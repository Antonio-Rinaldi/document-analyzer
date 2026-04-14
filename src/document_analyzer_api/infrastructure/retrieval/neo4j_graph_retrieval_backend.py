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
        records = await asyncio.to_thread(self._read_committed)
        return _rank_records(records, request, mode="graph")

    def _read_committed(self) -> list[dict[str, Any]]:
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
        query = (
            "MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk) "
            "WHERE c.status = 'committed' "
            "RETURN d.id AS document_id, c.id AS chunk_id, c.content AS content, c.metadata AS metadata"
        )
        with self._driver.session() as session:
            rows = session.run(query)
            records: list[dict[str, Any]] = []
            for row in rows:
                metadata = row.get("metadata")
                if not isinstance(metadata, dict):
                    metadata = {}
                records.append(
                    {
                        "document_id": row.get("document_id", ""),
                        "chunk_id": row.get("chunk_id", ""),
                        "content": row.get("content", ""),
                        "metadata": metadata,
                    }
                )
            return records

