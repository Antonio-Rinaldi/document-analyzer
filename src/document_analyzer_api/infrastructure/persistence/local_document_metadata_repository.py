import asyncio
import json
from dataclasses import asdict
from pathlib import Path

from ...domain.models.persistence import DocumentMetadata
from ...domain.ports.document_metadata_repository import DocumentMetadataRepositoryPort


class LocalDocumentMetadataRepository(DocumentMetadataRepositoryPort):
    def __init__(self, root_path: str) -> None:
        self._file_path = Path(root_path) / "documents.json"

    async def upsert(self, document: DocumentMetadata) -> None:
        records = await self._load_records()
        data = asdict(document)
        idx = next((i for i, item in enumerate(records) if item.get("id") == document.id), None)
        if idx is None:
            records.append(data)
        else:
            records[idx] = data
        await self._save_records(records)

    async def list_paginated(self, offset: int, limit: int) -> tuple[list[DocumentMetadata], int]:
        records = await self._load_records()
        total = len(records)
        items = [DocumentMetadata(**item) for item in records[offset : offset + limit]]
        return items, total

    async def _load_records(self) -> list[dict]:
        def _read() -> list[dict]:
            if not self._file_path.exists():
                return []
            return json.loads(self._file_path.read_text(encoding="utf-8"))

        return await asyncio.to_thread(_read)

    async def _save_records(self, records: list[dict]) -> None:
        def _write() -> None:
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            self._file_path.write_text(json.dumps(records), encoding="utf-8")

        await asyncio.to_thread(_write)

