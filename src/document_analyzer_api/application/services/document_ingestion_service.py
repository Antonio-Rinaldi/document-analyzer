"""Module `src/document_analyzer_api/application/services/document_ingestion_service.py`.

This module belongs to the application service layer of Document Analyzer.

Purpose:
- Coordinates use-case workflows over domain ports and adapters.

Defined symbols:
- Classes: IngestionStatus, IngestionResult, DocumentIngestionService.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import hashlib
import logging
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from ...domain.models.chunking import ChunkingConfig
from ...domain.ports.document_storage import DocumentStoragePort, UploadedFileData
from .document_processing_pipeline_service import DocumentProcessingPipelineService


logger = logging.getLogger(__name__)


class IngestionStatus(str, Enum):
    """IngestionStatus component.
    
    This class is defined in `src/document_analyzer_api/application/services/document_ingestion_service.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    processed = "processed"
    already_processed = "already_processed"
    conflict = "conflict"
    unsupported_media_type = "unsupported_media_type"
    failed = "failed"


@dataclass(slots=True)
class IngestionResult:
    """IngestionResult component.
    
    This class is defined in `src/document_analyzer_api/application/services/document_ingestion_service.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: name, status, document_id, error.
    """
    name: str
    status: IngestionStatus
    document_id: str | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        """Synchronous execution path for `ok`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_ingestion_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                None.
        
            Returns:
                A value compatible with `bool`.
        """
        return self.status in {IngestionStatus.processed, IngestionStatus.already_processed}


class DocumentIngestionService:
    """DocumentIngestionService application service.
    
    This class is defined in `src/document_analyzer_api/application/services/document_ingestion_service.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(
        self,
        storage: DocumentStoragePort,
        pipeline: DocumentProcessingPipelineService,
        supported_extensions: tuple[str, ...],
    ) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_ingestion_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (lower, tuple) to satisfy the callable contract.
        
            Args:
                storage: Input parameter accepted by `__init__`.
                pipeline: Input parameter accepted by `__init__`.
                supported_extensions: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._storage = storage
        self._pipeline = pipeline
        self._supported_extensions = tuple(ext.lower() for ext in supported_extensions)

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        """Synchronous execution path for `supported_extensions`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_ingestion_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                None.
        
            Returns:
                A value compatible with `tuple[str, ...]`.
        """
        return self._supported_extensions

    async def ingest_files(
        self,
        files: list[UploadedFileData],
        chunking_config: ChunkingConfig,
    ) -> list[IngestionResult]:
        """Asynchronous execution path for `ingest_files`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_ingestion_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (IngestionResult, _ingest_one, append, str) to satisfy the callable contract.
        
            Args:
                files: Input parameter accepted by `ingest_files`.
                chunking_config: Input parameter accepted by `ingest_files`.
        
            Returns:
                A value compatible with `list[IngestionResult]`.
        """
        results: list[IngestionResult] = []
        for item in files:
            try:
                result = await self._ingest_one(item, chunking_config)
            except Exception as exc:
                logger.exception(
                    "Document ingestion failed | file=%s error=%s",
                    item.name,
                    exc,
                )
                result = IngestionResult(
                    name=item.name,
                    status=IngestionStatus.failed,
                    error=self._format_ingestion_error(exc),
                )
            results.append(result)
        return results

    @staticmethod
    def _format_ingestion_error(exc: Exception) -> str:
        """Build a stable ingestion error message, including a fallback for blank exceptions."""
        message = str(exc).strip()
        return message or exc.__class__.__name__

    async def _ingest_one(self, file_data: UploadedFileData, chunking_config: ChunkingConfig) -> IngestionResult:
        """Process one file with duplicate detection, parse pipeline execution, and done-marker semantics."""
        extension = Path(file_data.name).suffix.lower()
        if extension not in self._supported_extensions:
            return IngestionResult(
                name=file_data.name,
                status=IngestionStatus.unsupported_media_type,
                error=f"Unsupported file extension '{extension or '<none>'}'",
            )

        incoming_hash = hashlib.sha256(memoryview(file_data.content)).hexdigest()
        object_exists = await self._storage.object_exists(file_data.name)

        if object_exists:
            stored_hash = await self._storage.object_hash(file_data.name)
            if stored_hash != incoming_hash:
                return IngestionResult(
                    name=file_data.name,
                    status=IngestionStatus.conflict,
                    error="File name already exists with different content",
                )

            if await self._storage.has_done_marker(file_data.name):
                return IngestionResult(name=file_data.name, status=IngestionStatus.already_processed)

        await self._storage.put_object(file_data.name, file_data.content)
        document_id = await self._pipeline.process(file_data.name, file_data.content, chunking_config)
        await self._storage.write_done_marker(file_data.name)
        return IngestionResult(name=file_data.name, status=IngestionStatus.processed, document_id=document_id)

