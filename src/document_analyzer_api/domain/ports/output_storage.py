from typing import Protocol


class OutputStoragePort(Protocol):
    async def write_output(self, filename: str, content: str) -> str:
        ...

