import asyncio
import hashlib
from pathlib import Path


class LocalDocumentStorage:
    def __init__(self, root_path: str, done_extension: str = ".done") -> None:
        self._root_path = Path(root_path)
        self._done_extension = done_extension

    async def object_exists(self, name: str) -> bool:
        path = self._object_path(name)
        return await asyncio.to_thread(path.exists)

    async def object_hash(self, name: str) -> str:
        path = self._object_path(name)

        def _read_hash() -> str:
            hasher = hashlib.sha256()
            with path.open("rb") as handle:
                while chunk := handle.read(1024 * 1024):
                    hasher.update(chunk)
            return hasher.hexdigest()

        return await asyncio.to_thread(_read_hash)

    async def put_object(self, name: str, content: bytes) -> None:
        path = self._object_path(name)

        def _write() -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)

        await asyncio.to_thread(_write)

    async def has_done_marker(self, name: str) -> bool:
        marker = self._done_path(name)
        return await asyncio.to_thread(marker.exists)

    async def write_done_marker(self, name: str) -> None:
        marker = self._done_path(name)

        def _write() -> None:
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_text("", encoding="utf-8")

        await asyncio.to_thread(_write)

    def _object_path(self, name: str) -> Path:
        safe_name = Path(name).name
        if safe_name != name:
            raise ValueError("File name must not include directory segments")
        return self._root_path / safe_name

    def _done_path(self, name: str) -> Path:
        return self._root_path / f"{Path(name).name}{self._done_extension}"

