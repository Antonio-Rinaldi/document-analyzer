from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from ...domain.models.persistence import PersistedChunk
from ...domain.ports.chunk_repository import ChunkRepositoryPort


class Neo4jChunkRepository(ChunkRepositoryPort):
    def __init__(self, uri: str, user: str, password: str) -> None:
        from neo4j import GraphDatabase

        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    async def stage_chunks(self, document_id: str, chunks: list[PersistedChunk], ttl_seconds: int) -> None:
        await asyncio.to_thread(self._stage_sync, document_id, chunks, ttl_seconds)

    async def commit_document(self, document_id: str) -> None:
        await asyncio.to_thread(self._commit_sync, document_id)

    async def rollback_document(self, document_id: str) -> None:
        await asyncio.to_thread(self._rollback_sync, document_id)

    def _stage_sync(self, document_id: str, chunks: list[PersistedChunk], ttl_seconds: int) -> None:
        expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds) if ttl_seconds > 0 else None
        with self._driver.session() as session:
            for chunk in chunks:
                session.run(
                    """
                    MERGE (d:Document {id: $document_id})
                    MERGE (c:Chunk {id: $chunk_id})
                    SET c.content = $content,
                        c.embedding = $embedding,
                        c.language = $language,
                        c.metadata = $metadata,
                        c.status = 'staged',
                        c.expiresAt = $expires_at
                    MERGE (d)-[:HAS_CHUNK]->(c)
                    """,
                    document_id=document_id,
                    chunk_id=chunk.chunk_id,
                    content=chunk.content,
                    embedding=chunk.embedding,
                    language=chunk.language,
                    metadata=chunk.metadata,
                    expires_at=expires_at.isoformat() if expires_at else None,
                )

    def _commit_sync(self, document_id: str) -> None:
        with self._driver.session() as session:
            session.run(
                """
                MATCH (d:Document {id: $document_id})-[:HAS_CHUNK]->(c:Chunk)
                SET c.status = 'committed', c.expiresAt = null
                """,
                document_id=document_id,
            )

    def _rollback_sync(self, document_id: str) -> None:
        with self._driver.session() as session:
            session.run(
                """
                MATCH (d:Document {id: $document_id})-[:HAS_CHUNK]->(c:Chunk)
                DETACH DELETE c
                """,
                document_id=document_id,
            )

