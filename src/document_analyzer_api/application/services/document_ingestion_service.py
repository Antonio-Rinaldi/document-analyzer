"""Detailed module documentation for `src/document_analyzer_api/application/services/document_ingestion_service.py`.

File role:
- Located in the application service layer.
- Defines logic and symbols for `document_ingestion_service.py` within Document Analyzer V1.

Purpose:
- Implements use-case orchestration across domain ports and infrastructure adapters.

Exported symbols overview:
- Classes: IngestionStatus, IngestionResult, DocumentIngestionService.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

import hashlib
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from ...domain.models.chunking import ChunkingConfig
from ...domain.ports.document_storage import DocumentStoragePort, UploadedFileData
from .document_processing_pipeline_service import DocumentProcessingPipelineService


class IngestionStatus(str, Enum):
    """Detailed class documentation for `IngestionStatus`.
    
    This component belongs to `src/document_analyzer_api/application/services/document_ingestion_service.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    processed = "processed"
    already_processed = "already_processed"
    conflict = "conflict"
    unsupported_media_type = "unsupported_media_type"
    failed = "failed"


@dataclass(slots=True)
class IngestionResult:
    """Detailed class documentation for `IngestionResult`.
    
    This component belongs to `src/document_analyzer_api/application/services/document_ingestion_service.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    name: str
    status: IngestionStatus
    document_id: str | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        """Detailed synchronous function documentation for `ok`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_ingestion_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `ok` contract and consumed by downstream callers.
        """
        return self.status in {IngestionStatus.processed, IngestionStatus.already_processed}


class DocumentIngestionService:
    """Detailed class documentation for `DocumentIngestionService`.
    
    This application service belongs to `src/document_analyzer_api/application/services/document_ingestion_service.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(
        self,
        storage: DocumentStoragePort,
        pipeline: DocumentProcessingPipelineService,
        supported_extensions: tuple[str, ...],
    ) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_ingestion_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                storage: Input parameter for `__init__`.
                pipeline: Input parameter for `__init__`.
                supported_extensions: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._storage = storage
        self._pipeline = pipeline
        self._supported_extensions = tuple(ext.lower() for ext in supported_extensions)

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        """Detailed synchronous function documentation for `supported_extensions`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_ingestion_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `supported_extensions` contract and consumed by downstream callers.
        """
        return self._supported_extensions

    async def ingest_files(
        self,
        files: list[UploadedFileData],
        chunking_config: ChunkingConfig,
    ) -> list[IngestionResult]:
        """Detailed asynchronous function documentation for `ingest_files`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_ingestion_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                files: Input parameter for `ingest_files`.
                chunking_config: Input parameter for `ingest_files`.
        
            Returns:
                Value defined by `ingest_files` contract and consumed by downstream callers.
        """
        results: list[IngestionResult] = []
        for item in files:
            try:
                result = await self._ingest_one(item, chunking_config)
            except Exception as exc:
                result = IngestionResult(name=item.name, status=IngestionStatus.failed, error=str(exc))
            results.append(result)
        return results

    async def _ingest_one(self, file_data: UploadedFileData, chunking_config: ChunkingConfig) -> IngestionResult:
        """Detailed asynchronous function documentation for `_ingest_one`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_ingestion_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                file_data: Input parameter for `_ingest_one`.
                chunking_config: Input parameter for `_ingest_one`.
        
            Returns:
                Value defined by `_ingest_one` contract and consumed by downstream callers.
        """
        extension = Path(file_data.name).suffix.lower()
        if extension not in self._supported_extensions:
            return IngestionResult(
                name=file_data.name,
                status=IngestionStatus.unsupported_media_type,
                error=f"Unsupported file extension '{extension or '<none>'}'",
            )

        incoming_hash = hashlib.sha256(file_data.content).hexdigest()
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

