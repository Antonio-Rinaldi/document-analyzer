import hashlib
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from ...domain.models.chunking import ChunkingConfig
from ...domain.ports.document_storage import DocumentStoragePort, UploadedFileData
from .document_processing_pipeline_service import DocumentProcessingPipelineService


class IngestionStatus(str, Enum):
    processed = "processed"
    already_processed = "already_processed"
    conflict = "conflict"
    unsupported_media_type = "unsupported_media_type"
    failed = "failed"


@dataclass(slots=True)
class IngestionResult:
    name: str
    status: IngestionStatus
    document_id: str | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.status in {IngestionStatus.processed, IngestionStatus.already_processed}


class DocumentIngestionService:
    def __init__(
        self,
        storage: DocumentStoragePort,
        pipeline: DocumentProcessingPipelineService,
        supported_extensions: tuple[str, ...],
    ) -> None:
        self._storage = storage
        self._pipeline = pipeline
        self._supported_extensions = tuple(ext.lower() for ext in supported_extensions)

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        return self._supported_extensions

    async def ingest_files(
        self,
        files: list[UploadedFileData],
        chunking_config: ChunkingConfig,
    ) -> list[IngestionResult]:
        results: list[IngestionResult] = []
        for item in files:
            try:
                result = await self._ingest_one(item, chunking_config)
            except Exception as exc:
                result = IngestionResult(name=item.name, status=IngestionStatus.failed, error=str(exc))
            results.append(result)
        return results

    async def _ingest_one(self, file_data: UploadedFileData, chunking_config: ChunkingConfig) -> IngestionResult:
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

