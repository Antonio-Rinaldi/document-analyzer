from typing import Protocol

from ..models.chunking import ParsedDocument


class DocumentParserPort(Protocol):
    async def parse(self, document_name: str, content: bytes) -> ParsedDocument:
        ...

