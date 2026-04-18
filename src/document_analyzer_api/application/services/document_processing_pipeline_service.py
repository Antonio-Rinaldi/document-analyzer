"""Module `src/document_analyzer_api/application/services/document_processing_pipeline_service.py`.

This module belongs to the application service layer of Document Analyzer.

Purpose:
- Coordinates use-case workflows over domain ports and adapters.

Defined symbols:
- Classes: DocumentProcessingPipelineService.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import uuid

from ...domain.models.chunking import ChunkingConfig, FinalChunk
from ...domain.models.persistence import DocumentMetadata, PersistedChunk
from ...domain.ports.chunk_repository import ChunkRepositoryPort
from ...domain.ports.document_metadata_repository import DocumentMetadataRepositoryPort
from ...domain.ports.document_parser import DocumentParserPort
from ...domain.ports.embedding_client import EmbeddingClientPort
from .base_chunk_builder_service import BaseChunkBuilderService
from .chunking_service import ChunkingService


class DocumentProcessingPipelineService:
    """DocumentProcessingPipelineService application service.
    
    This class is defined in `src/document_analyzer_api/application/services/document_processing_pipeline_service.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(
        self,
        *,
        parser: DocumentParserPort,
        base_chunk_builder: BaseChunkBuilderService,
        chunking_service: ChunkingService,
        embedding_client: EmbeddingClientPort,
        repositories: list[ChunkRepositoryPort],
        metadata_repository: DocumentMetadataRepositoryPort,
        temp_ttl_seconds: int,
    ) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_processing_pipeline_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                parser: Input parameter accepted by `__init__`.
                base_chunk_builder: Input parameter accepted by `__init__`.
                chunking_service: Input parameter accepted by `__init__`.
                embedding_client: Input parameter accepted by `__init__`.
                repositories: Input parameter accepted by `__init__`.
                metadata_repository: Input parameter accepted by `__init__`.
                temp_ttl_seconds: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._parser = parser
        self._base_chunk_builder = base_chunk_builder
        self._chunking_service = chunking_service
        self._embedding_client = embedding_client
        self._repositories = repositories
        self._metadata_repository = metadata_repository
        self._temp_ttl_seconds = temp_ttl_seconds

    async def process(self, file_name: str, content: bytes, chunking_config: ChunkingConfig) -> str:
        """Process one uploaded file through parse, chunk, embed, and dual-store persistence.

        The method validates that embedding cardinality exactly matches the number of
        final chunks so provider payload inconsistencies fail fast with explicit
        context instead of surfacing as index errors.
        """
        document_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, file_name))
        parsed = await self._parser.parse(document_name=file_name, content=content)
        base_chunks = self._base_chunk_builder.build_chunks(parsed, chunking_config)
        final_chunks = await self._chunking_service.apply_strategy(base_chunks, chunking_config)

        texts = [str(chunk.content) for chunk in final_chunks]
        embeddings = await self._embedding_client.embed_texts(texts)
        persisted_chunks = self._build_persisted_chunks(
            document_id=document_id,
            file_name=file_name,
            final_chunks=final_chunks,
            embeddings=embeddings,
            chunking_config=chunking_config,
        )

        staged_repositories: list[ChunkRepositoryPort] = []
        try:
            for repository in self._repositories:
                await repository.stage_chunks(document_id, persisted_chunks, self._temp_ttl_seconds)
                staged_repositories.append(repository)

            for repository in self._repositories:
                await repository.commit_document(document_id)

            description = final_chunks[0].content[:280] if final_chunks else ""
            await self._metadata_repository.upsert(
                DocumentMetadata(id=document_id, name=file_name, description=description)
            )
            return document_id
        except Exception:
            for repository in staged_repositories:
                await repository.rollback_document(document_id)
            raise

    def _build_persisted_chunks(
        self,
        *,
        document_id: str,
        file_name: str,
        final_chunks: list[FinalChunk],
        embeddings: list[list[float]],
        chunking_config: ChunkingConfig,
    ) -> list[PersistedChunk]:
        """Create persisted chunks while enforcing a strict chunk-to-embedding contract."""
        self._validate_embedding_alignment(
            file_name=file_name,
            chunk_count=len(final_chunks),
            embedding_count=len(embeddings),
        )
        return [
            PersistedChunk(
                document_id=document_id,
                chunk_id=chunk.chunk_id,
                content=chunk.content,
                embedding=embedding,
                language="unknown",
                metadata={
                    **chunk.metadata,
                    "chunkingStrategy": chunking_config.strategy.value,
                    "chunkGranularity": chunking_config.granularity.value,
                },
            )
            for chunk, embedding in zip(final_chunks, embeddings)
        ]

    @staticmethod
    def _validate_embedding_alignment(*, file_name: str, chunk_count: int, embedding_count: int) -> None:
        """Raise a deterministic error when provider embeddings do not match chunk count."""
        if chunk_count == embedding_count:
            return
        raise ValueError(
            "Embedding cardinality mismatch during ingestion "
            f"for file '{file_name}': chunks={chunk_count}, embeddings={embedding_count}."
        )

