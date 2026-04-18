"""Unit tests for ingestion error logging behavior."""

import asyncio
import logging

import pytest

from document_analyzer_api.application.services.document_ingestion_service import (
    DocumentIngestionService,
    IngestionStatus,
)
from document_analyzer_api.domain.models.chunking import ChunkingConfig, ChunkGranularity, ChunkingStrategyName
from document_analyzer_api.domain.ports.document_storage import UploadedFileData


class _NoopStorage:
    """Storage test double that always reports missing objects."""

    async def object_exists(self, name: str) -> bool:
        _ = name
        await asyncio.sleep(0)
        return False

    async def object_hash(self, name: str) -> str:
        _ = name
        await asyncio.sleep(0)
        return ""

    async def has_done_marker(self, name: str) -> bool:
        _ = name
        await asyncio.sleep(0)
        return False

    async def put_object(self, name: str, content: bytes) -> None:
        _ = name
        _ = content
        await asyncio.sleep(0)

    async def write_done_marker(self, name: str) -> None:
        _ = name
        await asyncio.sleep(0)


class _FailingPipeline:
    """Pipeline test double that raises a deterministic processing error."""

    async def process(self, file_name: str, content: bytes, chunking_config: ChunkingConfig) -> str:
        _ = file_name
        _ = content
        _ = chunking_config
        await asyncio.sleep(0)
        raise RuntimeError("boom")


@pytest.mark.asyncio
async def test_ingest_files_logs_stack_trace_on_failure(caplog: pytest.LogCaptureFixture) -> None:
    """Ensure per-file ingestion failures are logged with exception traceback."""
    service = DocumentIngestionService(
        storage=_NoopStorage(),
        pipeline=_FailingPipeline(),
        supported_extensions=(".epub",),
    )
    chunking_config = ChunkingConfig(
        strategy=ChunkingStrategyName.meaningful,
        granularity=ChunkGranularity.paragraph,
        target_tokens=350,
        overlap_tokens=60,
        contextual_summary_prompt="",
    )

    with caplog.at_level(logging.ERROR):
        results = await service.ingest_files(
            files=[UploadedFileData(name="book.epub", content=b"fake")],
            chunking_config=chunking_config,
        )

    assert results[0].status == IngestionStatus.failed
    assert results[0].error == "boom"
    assert any(record.exc_info is not None for record in caplog.records)


