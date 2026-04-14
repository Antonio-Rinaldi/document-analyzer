"""Module `tests/unit/test_document_processing_pipeline_service.py`.

This module belongs to the project support layer of Document Analyzer.

Purpose:
- Implements a focused responsibility in the Document Analyzer codebase.

Defined symbols:
- Classes: none.
- Functions: test_processing_pipeline_commits_to_both_repositories.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import asyncio
import json
from pathlib import Path

from document_analyzer_api.application.services.base_chunk_builder_service import BaseChunkBuilderService
from document_analyzer_api.application.services.chunking_service import ChunkingService
from document_analyzer_api.application.services.document_processing_pipeline_service import DocumentProcessingPipelineService
from document_analyzer_api.domain.models.chunking import ChunkingConfig, ChunkingStrategyName
from document_analyzer_api.infrastructure.chunking.deterministic_summarizer import DeterministicSummarizer
from document_analyzer_api.infrastructure.embeddings.deterministic_embedding_client import DeterministicEmbeddingClient
from document_analyzer_api.infrastructure.parsing.simple_epub_parser import SimpleEpubParser
from document_analyzer_api.infrastructure.persistence.local_chunk_repository import LocalChunkRepository
from document_analyzer_api.infrastructure.persistence.local_document_metadata_repository import (
    LocalDocumentMetadataRepository,
)


def test_processing_pipeline_commits_to_both_repositories(tmp_path: Path) -> None:
    """Synchronous execution path for `test_processing_pipeline_commits_to_both_repositories`.
    
    This callable is implemented in `tests/unit/test_document_processing_pipeline_service.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (BaseChunkBuilderService, ChunkingConfig, ChunkingService, DeterministicEmbeddingClient) to satisfy the callable contract.
    
        Args:
            tmp_path: Input parameter accepted by `test_processing_pipeline_commits_to_both_repositories`.
    
        Returns:
            A value compatible with `None`.
    """
    pipeline = DocumentProcessingPipelineService(
        parser=SimpleEpubParser(),
        base_chunk_builder=BaseChunkBuilderService(),
        chunking_service=ChunkingService(summarizer=DeterministicSummarizer()),
        embedding_client=DeterministicEmbeddingClient(),
        repositories=[
            LocalChunkRepository(root_path=str(tmp_path), backend_name="mongo"),
            LocalChunkRepository(root_path=str(tmp_path), backend_name="neo4j"),
        ],
        metadata_repository=LocalDocumentMetadataRepository(root_path=str(tmp_path)),
        temp_ttl_seconds=600,
    )

    document_id = asyncio.run(
        pipeline.process(
            file_name="book.epub",
            content=b"Chapter text with meaningful content.",
            chunking_config=ChunkingConfig(strategy=ChunkingStrategyName.meaningful),
        )
    )

    assert document_id

    mongo_records = json.loads((tmp_path / "mongo_chunks.json").read_text(encoding="utf-8"))
    neo4j_records = json.loads((tmp_path / "neo4j_chunks.json").read_text(encoding="utf-8"))
    docs = json.loads((tmp_path / "documents.json").read_text(encoding="utf-8"))

    assert mongo_records
    assert neo4j_records
    assert mongo_records[0]["status"] == "committed"
    assert neo4j_records[0]["status"] == "committed"
    assert mongo_records[0]["metadata"]["chunkingStrategy"] == "meaningful"
    assert docs[0]["id"] == document_id

