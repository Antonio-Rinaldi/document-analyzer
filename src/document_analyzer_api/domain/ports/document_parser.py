from typing import Protocol

from ..models.chunking import ParsedDocument


class DocumentParserPort(Protocol):
    def supported_extensions(self) -> tuple[str, ...]:
        ...

    async def parse(self, document_name: str, content: bytes) -> ParsedDocument:
        ...

