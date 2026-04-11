from __future__ import annotations

import asyncio
from typing import Any

from ...domain.models.retrieval import RetrievalHit, RetrievalRequest
from ...domain.ports.retrieval_backend import RetrievalBackendPort
from .local_retrieval_backends import _rank_records


class Neo4jGraphRetrievalBackend(RetrievalBackendPort):
    def __init__(self, uri: str, user: str, password: str) -> None:
        from neo4j import GraphDatabase

        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    async def retrieve(self, request: RetrievalRequest) -> list[RetrievalHit]:
        records = await asyncio.to_thread(self._read_committed)
        return _rank_records(records, request, mode="graph")

    def _read_committed(self) -> list[dict[str, Any]]:
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

