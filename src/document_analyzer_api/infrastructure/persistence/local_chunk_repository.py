import asyncio
import json
from dataclasses import asdict
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from ...domain.models.persistence import PersistedChunk
from ...domain.ports.chunk_repository import ChunkRepositoryPort


class LocalChunkRepository(ChunkRepositoryPort):
    def __init__(self, root_path: str, backend_name: str) -> None:
        self._file_path = Path(root_path) / f"{backend_name}_chunks.json"

    async def stage_chunks(self, document_id: str, chunks: list[PersistedChunk], ttl_seconds: int) -> None:
        records = await self._load_records()
        expires_at = (datetime.now(UTC) + timedelta(seconds=ttl_seconds)).isoformat() if ttl_seconds > 0 else None

        for chunk in chunks:
            payload = asdict(chunk)
            payload["status"] = "staged"
            payload["expiresAt"] = expires_at
            records.append(payload)

        await self._save_records(records)

    async def commit_document(self, document_id: str) -> None:
        records = await self._load_records()
        for record in records:
            if record.get("document_id") == document_id:
                record["status"] = "committed"
                record["expiresAt"] = None
        await self._save_records(records)

    async def rollback_document(self, document_id: str) -> None:
        records = await self._load_records()
        filtered = [item for item in records if item.get("document_id") != document_id]
        await self._save_records(filtered)

    async def _load_records(self) -> list[dict[str, Any]]:
        def _read() -> list[dict[str, Any]]:
            if not self._file_path.exists():
                return []
            return json.loads(self._file_path.read_text(encoding="utf-8"))

        return await asyncio.to_thread(_read)

    async def _save_records(self, records: list[dict[str, Any]]) -> None:
        def _write() -> None:
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            self._file_path.write_text(json.dumps(records), encoding="utf-8")

        await asyncio.to_thread(_write)

