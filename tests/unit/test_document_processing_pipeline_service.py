"""Detailed module documentation for `tests/unit/test_document_processing_pipeline_service.py`.

File role:
- Located in the project layer.
- Defines logic and symbols for `test_document_processing_pipeline_service.py` within Document Analyzer V1.

Purpose:
- Supports a focused concern in the Document Analyzer codebase.

Exported symbols overview:
- Classes: none.
- Functions: test_processing_pipeline_commits_to_both_repositories.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
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
    """Detailed synchronous function documentation for `test_processing_pipeline_commits_to_both_repositories`.
    
    This callable is implemented in `tests/unit/test_document_processing_pipeline_service.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            tmp_path: Input parameter for `test_processing_pipeline_commits_to_both_repositories`.
    
        Returns:
            Value defined by `test_processing_pipeline_commits_to_both_repositories` contract and consumed by downstream callers.
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

