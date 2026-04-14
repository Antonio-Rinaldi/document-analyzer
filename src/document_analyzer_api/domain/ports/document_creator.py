from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class CreatedDocument:
    filename: str
    content: bytes


class DocumentCreatorPort(Protocol):
    def supported_output_formats(self) -> tuple[str, ...]:
        ...

    async def create(self, *, summary_text: str, output_format: str, filename_stem: str) -> CreatedDocument:
        ...

