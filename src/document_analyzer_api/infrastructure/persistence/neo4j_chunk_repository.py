"""Module `src/document_analyzer_api/infrastructure/persistence/neo4j_chunk_repository.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: Neo4jChunkRepository.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime, timedelta
from typing import Any

from ...domain.models.persistence import PersistedChunk
from ...domain.ports.chunk_repository import ChunkRepositoryPort


class Neo4jChunkRepository(ChunkRepositoryPort):
    """Neo4jChunkRepository repository adapter.
    
    This class is defined in `src/document_analyzer_api/infrastructure/persistence/neo4j_chunk_repository.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, uri: str, user: str, password: str) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/neo4j_chunk_repository.py` and contributes to module-level behavior
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

    async def stage_chunks(self, document_id: str, chunks: list[PersistedChunk], ttl_seconds: int) -> None:
        """Asynchronous execution path for `stage_chunks`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/neo4j_chunk_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (to_thread) to satisfy the callable contract.
        
            Args:
                document_id: Input parameter accepted by `stage_chunks`.
                chunks: Input parameter accepted by `stage_chunks`.
                ttl_seconds: Input parameter accepted by `stage_chunks`.
        
            Returns:
                A value compatible with `None`.
        """
        await asyncio.to_thread(self._stage_sync, document_id, chunks, ttl_seconds)

    async def commit_document(self, document_id: str) -> None:
        """Asynchronous execution path for `commit_document`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/neo4j_chunk_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (to_thread) to satisfy the callable contract.
        
            Args:
                document_id: Input parameter accepted by `commit_document`.
        
            Returns:
                A value compatible with `None`.
        """
        await asyncio.to_thread(self._commit_sync, document_id)

    async def rollback_document(self, document_id: str) -> None:
        """Asynchronous execution path for `rollback_document`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/neo4j_chunk_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (to_thread) to satisfy the callable contract.
        
            Args:
                document_id: Input parameter accepted by `rollback_document`.
        
            Returns:
                A value compatible with `None`.
        """
        await asyncio.to_thread(self._rollback_sync, document_id)

    def _stage_sync(self, document_id: str, chunks: list[PersistedChunk], ttl_seconds: int) -> None:
        """Synchronous execution path for `_stage_sync`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/neo4j_chunk_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (isoformat, now, run, session) to satisfy the callable contract.
        
            Args:
                document_id: Input parameter accepted by `_stage_sync`.
                chunks: Input parameter accepted by `_stage_sync`.
                ttl_seconds: Input parameter accepted by `_stage_sync`.
        
            Returns:
                A value compatible with `None`.
        """
        expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds) if ttl_seconds > 0 else None
        with self._driver.session() as session:
            for chunk in chunks:
                self._upsert_chunk_hierarchy(
                    session=session,
                    document_id=document_id,
                    chunk=chunk,
                    expires_at=expires_at,
                )
            self._create_next_relationships(session=session, document_id=document_id)

    def _upsert_chunk_hierarchy(
        self,
        *,
        session: Any,
        document_id: str,
        chunk: PersistedChunk,
        expires_at: datetime | None,
    ) -> None:
        """Persist a chunk and its chapter/paragraph hierarchy using deterministic metadata keys."""
        hierarchy = self._extract_hierarchy(chunk=chunk)
        session.run(
            """
            MERGE (d:Document {id: $document_id})
            MERGE (ch:Chapter {id: $chapter_id})
            SET ch.documentId = $document_id,
                ch.title = $chapter_title,
                ch.chapterIndex = $chapter_index
            MERGE (d)-[:HAS_CHAPTER]->(ch)
            MERGE (p:Paragraph {id: $paragraph_id})
            SET p.documentId = $document_id,
                p.chapterId = $chapter_id,
                p.paragraphIndex = $paragraph_index
            MERGE (ch)-[:HAS_PARAGRAPH]->(p)
            MERGE (c:Chunk {id: $chunk_id})
            SET c.documentId = $document_id,
                c.chapterId = $chapter_id,
                c.paragraphId = $paragraph_id,
                c.paragraphChunkIndex = $paragraph_chunk_index,
                c.content = $content,
                c.embedding = $embedding,
                c.language = $language,
                c.metadataJson = $metadata_json,
                c.status = 'staged',
                c.expiresAt = $expires_at
            MERGE (p)-[:HAS_CHUNK]->(c)
            """,
            document_id=document_id,
            chapter_id=hierarchy["chapter_id"],
            chapter_title=hierarchy["chapter_title"],
            chapter_index=hierarchy["chapter_index"],
            paragraph_id=hierarchy["paragraph_id"],
            paragraph_index=hierarchy["paragraph_index"],
            paragraph_chunk_index=hierarchy["paragraph_chunk_index"],
            chunk_id=chunk.chunk_id,
            content=chunk.content,
            embedding=chunk.embedding,
            language=chunk.language,
            metadata_json=self._serialize_metadata(chunk.metadata),
            expires_at=expires_at.isoformat() if expires_at else None,
        )

    def _create_next_relationships(self, *, session: Any, document_id: str) -> None:
        """Create deterministic NEXT edges across chapter, paragraph, and chunk sequences."""
        session.run(
            """
            MATCH (d:Document {id: $document_id})-[:HAS_CHAPTER]->(ch:Chapter)
            WITH ch ORDER BY ch.chapterIndex ASC, ch.id ASC
            WITH collect(ch) AS chapters
            UNWIND range(0, size(chapters) - 2) AS idx
            MERGE (chapters[idx])-[:NEXT]->(chapters[idx + 1])
            """,
            document_id=document_id,
        )
        session.run(
            """
            MATCH (d:Document {id: $document_id})-[:HAS_CHAPTER]->(ch:Chapter)-[:HAS_PARAGRAPH]->(p:Paragraph)
            WITH ch, p ORDER BY p.paragraphIndex ASC, p.id ASC
            WITH ch, collect(p) AS paragraphs
            UNWIND range(0, size(paragraphs) - 2) AS idx
            MERGE (paragraphs[idx])-[:NEXT]->(paragraphs[idx + 1])
            """,
            document_id=document_id,
        )
        session.run(
            """
            MATCH (d:Document {id: $document_id})-[:HAS_CHAPTER]->(:Chapter)-[:HAS_PARAGRAPH]->(p:Paragraph)-[:HAS_CHUNK]->(c:Chunk)
            WITH p, c ORDER BY c.paragraphChunkIndex ASC, c.id ASC
            WITH p, collect(c) AS chunks
            UNWIND range(0, size(chunks) - 2) AS idx
            MERGE (chunks[idx])-[:NEXT]->(chunks[idx + 1])
            """,
            document_id=document_id,
        )

    @staticmethod
    def _serialize_metadata(metadata: dict[str, Any]) -> str:
        """Serialize chunk metadata into a JSON string compatible with Neo4j property storage.

        Neo4j node properties only support primitives and arrays of primitives; nested maps are not valid
        property values. This adapter persists the complete metadata structure as a compact JSON string so
        retrieval backends can reconstruct the original dictionary without losing nested fields.
        """
        return json.dumps(metadata, ensure_ascii=True, separators=(",", ":"), default=str)

    @staticmethod
    def _extract_hierarchy(chunk: PersistedChunk) -> dict[str, str | int]:
        """Resolve hierarchy identifiers from chunk metadata with deterministic defaults."""
        metadata = chunk.metadata if isinstance(chunk.metadata, dict) else {}
        chapter_id = str(metadata.get("chapterId") or metadata.get("sectionId") or chunk.chunk_id.split(":")[0])
        chapter_title = str(metadata.get("chapterTitle") or metadata.get("sectionTitle") or chapter_id)
        paragraph_id = str(metadata.get("paragraphId") or f"{chapter_id}:p0")
        return {
            "chapter_id": chapter_id,
            "chapter_title": chapter_title,
            "chapter_index": Neo4jChunkRepository._to_int(metadata.get("chapterIndex"), default=0),
            "paragraph_id": paragraph_id,
            "paragraph_index": Neo4jChunkRepository._to_int(metadata.get("paragraphIndex"), default=0),
            "paragraph_chunk_index": Neo4jChunkRepository._to_int(metadata.get("paragraphChunkIndex"), default=0),
        }

    @staticmethod
    def _to_int(value: Any, *, default: int) -> int:
        """Convert metadata values to integer while preserving a safe fallback."""
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _commit_sync(self, document_id: str) -> None:
        """Synchronous execution path for `_commit_sync`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/neo4j_chunk_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (run, session) to satisfy the callable contract.
        
            Args:
                document_id: Input parameter accepted by `_commit_sync`.
        
            Returns:
                A value compatible with `None`.
        """
        with self._driver.session() as session:
            session.run(
                """
                MATCH (d:Document {id: $document_id})-[:HAS_CHAPTER]->(:Chapter)-[:HAS_PARAGRAPH]->(:Paragraph)-[:HAS_CHUNK]->(c:Chunk)
                SET c.status = 'committed', c.expiresAt = null
                """,
                document_id=document_id,
            )

    def _rollback_sync(self, document_id: str) -> None:
        """Synchronous execution path for `_rollback_sync`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/neo4j_chunk_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (run, session) to satisfy the callable contract.
        
            Args:
                document_id: Input parameter accepted by `_rollback_sync`.
        
            Returns:
                A value compatible with `None`.
        """
        with self._driver.session() as session:
            session.run(
                """
                MATCH (d:Document {id: $document_id})-[:HAS_CHAPTER]->(:Chapter)-[:HAS_PARAGRAPH]->(:Paragraph)-[:HAS_CHUNK]->(c:Chunk)
                DETACH DELETE c
                """,
                document_id=document_id,
            )
            session.run(
                """
                MATCH (d:Document {id: $document_id})-[:HAS_CHAPTER]->(ch:Chapter)-[:HAS_PARAGRAPH]->(p:Paragraph)
                WHERE NOT (p)-[:HAS_CHUNK]->(:Chunk)
                DETACH DELETE p
                """,
                document_id=document_id,
            )
            session.run(
                """
                MATCH (d:Document {id: $document_id})-[:HAS_CHAPTER]->(ch:Chapter)
                WHERE NOT (ch)-[:HAS_PARAGRAPH]->(:Paragraph)
                DETACH DELETE ch
                """,
                document_id=document_id,
            )
            session.run(
                """
                MATCH (d:Document {id: $document_id})
                WHERE NOT (d)-[:HAS_CHAPTER]->(:Chapter)
                DETACH DELETE d
                """,
                document_id=document_id,
            )

