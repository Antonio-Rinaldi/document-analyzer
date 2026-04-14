"""Detailed module documentation for `src/document_analyzer_api/application/services/document_processing_pipeline_service.py`.

File role:
- Located in the application service layer.
- Defines logic and symbols for `document_processing_pipeline_service.py` within Document Analyzer V1.

Purpose:
- Implements use-case orchestration across domain ports and infrastructure adapters.

Exported symbols overview:
- Classes: DocumentProcessingPipelineService.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

import uuid

from ...domain.models.chunking import ChunkingConfig
from ...domain.models.persistence import DocumentMetadata, PersistedChunk
from ...domain.ports.chunk_repository import ChunkRepositoryPort
from ...domain.ports.document_metadata_repository import DocumentMetadataRepositoryPort
from ...domain.ports.document_parser import DocumentParserPort
from ...domain.ports.embedding_client import EmbeddingClientPort
from .base_chunk_builder_service import BaseChunkBuilderService
from .chunking_service import ChunkingService


class DocumentProcessingPipelineService:
    """Detailed class documentation for `DocumentProcessingPipelineService`.
    
    This application service belongs to `src/document_analyzer_api/application/services/document_processing_pipeline_service.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
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
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_processing_pipeline_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                parser: Input parameter for `__init__`.
                base_chunk_builder: Input parameter for `__init__`.
                chunking_service: Input parameter for `__init__`.
                embedding_client: Input parameter for `__init__`.
                repositories: Input parameter for `__init__`.
                metadata_repository: Input parameter for `__init__`.
                temp_ttl_seconds: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._parser = parser
        self._base_chunk_builder = base_chunk_builder
        self._chunking_service = chunking_service
        self._embedding_client = embedding_client
        self._repositories = repositories
        self._metadata_repository = metadata_repository
        self._temp_ttl_seconds = temp_ttl_seconds

    async def process(self, file_name: str, content: bytes, chunking_config: ChunkingConfig) -> str:
        """Detailed asynchronous function documentation for `process`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_processing_pipeline_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                file_name: Input parameter for `process`.
                content: Raw payload bytes or text handled by the callable.
                chunking_config: Input parameter for `process`.
        
            Returns:
                Value defined by `process` contract and consumed by downstream callers.
        """
        document_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, file_name))
        parsed = await self._parser.parse(document_name=file_name, content=content)
        base_chunks = self._base_chunk_builder.build_chunks(parsed, chunking_config)
        final_chunks = await self._chunking_service.apply_strategy(base_chunks, chunking_config)

        texts = [chunk.content for chunk in final_chunks]
        embeddings = await self._embedding_client.embed_texts(texts)

        persisted_chunks = [
            PersistedChunk(
                document_id=document_id,
                chunk_id=chunk.chunk_id,
                content=chunk.content,
                embedding=embeddings[idx],
                language="unknown",
                metadata={
                    **chunk.metadata,
                    "chunkingStrategy": chunking_config.strategy.value,
                    "chunkGranularity": chunking_config.granularity.value,
                },
            )
            for idx, chunk in enumerate(final_chunks)
        ]

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

