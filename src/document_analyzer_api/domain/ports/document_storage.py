from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class UploadedFileData:
    name: str
    content: bytes


class DocumentStoragePort(Protocol):
    async def object_exists(self, name: str) -> bool:
        ...

    async def object_hash(self, name: str) -> str:
        ...

    async def put_object(self, name: str, content: bytes) -> None:
        ...

    async def has_done_marker(self, name: str) -> bool:
        ...

    async def write_done_marker(self, name: str) -> None:
        ...

