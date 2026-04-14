"""Module `src/document_analyzer_api/domain/models/persistence.py`.

This module belongs to the domain model layer of Document Analyzer.

Purpose:
- Declares domain objects exchanged across business workflows.

Defined symbols:
- Classes: PersistedChunk, DocumentMetadata.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PersistedChunk:
    """PersistedChunk component.
    
    This class is defined in `src/document_analyzer_api/domain/models/persistence.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: document_id, chunk_id, content, embedding, language, metadata.
    """
    document_id: str
    chunk_id: str
    content: str
    embedding: list[float]
    language: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DocumentMetadata:
    """DocumentMetadata component.
    
    This class is defined in `src/document_analyzer_api/domain/models/persistence.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: id, name, description.
    """
    id: str
    name: str
    description: str

