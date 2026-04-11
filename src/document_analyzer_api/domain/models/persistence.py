from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PersistedChunk:
    document_id: str
    chunk_id: str
    content: str
    embedding: list[float]
    language: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DocumentMetadata:
    id: str
    name: str
    description: str

