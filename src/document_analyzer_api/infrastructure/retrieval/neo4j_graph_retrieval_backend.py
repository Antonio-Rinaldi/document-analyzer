"""Detailed module documentation for `src/document_analyzer_api/infrastructure/retrieval/neo4j_graph_retrieval_backend.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `neo4j_graph_retrieval_backend.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: Neo4jGraphRetrievalBackend.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from __future__ import annotations

import asyncio
from typing import Any

from ...domain.models.retrieval import RetrievalHit, RetrievalRequest
from ...domain.ports.retrieval_backend import RetrievalBackendPort
from .local_retrieval_backends import _rank_records


class Neo4jGraphRetrievalBackend(RetrievalBackendPort):
    """Detailed class documentation for `Neo4jGraphRetrievalBackend`.
    
    This component belongs to `src/document_analyzer_api/infrastructure/retrieval/neo4j_graph_retrieval_backend.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, uri: str, user: str, password: str) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/neo4j_graph_retrieval_backend.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                uri: Input parameter for `__init__`.
                user: Input parameter for `__init__`.
                password: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        from neo4j import GraphDatabase

        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    async def retrieve(self, request: RetrievalRequest) -> list[RetrievalHit]:
        """Detailed asynchronous function documentation for `retrieve`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/neo4j_graph_retrieval_backend.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes retrieval strategy selection and returns matching evidence chunks.
        
            Args:
                request: Incoming request object carrying path/query/body/context information.
        
            Returns:
                Value defined by `retrieve` contract and consumed by downstream callers.
        """
        records = await asyncio.to_thread(self._read_committed)
        return _rank_records(records, request, mode="graph")

    def _read_committed(self) -> list[dict[str, Any]]:
        """Detailed synchronous function documentation for `_read_committed`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/neo4j_graph_retrieval_backend.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `_read_committed` contract and consumed by downstream callers.
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

