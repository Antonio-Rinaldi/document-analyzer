"""Detailed module documentation for `src/document_analyzer_api/domain/models/persistence.py`.

File role:
- Located in the domain model layer.
- Defines logic and symbols for `persistence.py` within Document Analyzer V1.

Purpose:
- Declares domain-level structures exchanged by services and adapters.

Exported symbols overview:
- Classes: PersistedChunk, DocumentMetadata.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PersistedChunk:
    """Detailed class documentation for `PersistedChunk`.
    
    This component belongs to `src/document_analyzer_api/domain/models/persistence.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    document_id: str
    chunk_id: str
    content: str
    embedding: list[float]
    language: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DocumentMetadata:
    """Detailed class documentation for `DocumentMetadata`.
    
    This component belongs to `src/document_analyzer_api/domain/models/persistence.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    id: str
    name: str
    description: str

