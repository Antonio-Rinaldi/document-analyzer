"""Module `src/document_analyzer_api/domain/models/retrieval.py`.

This module belongs to the domain model layer of Document Analyzer.

Purpose:
- Declares domain objects exchanged across business workflows.

Defined symbols:
- Classes: RetrievalMode, KeywordsMode, RetrievalRequest, RetrievalHit, Citation, RetrievalResult.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RetrievalMode(str, Enum):
    """RetrievalMode component.
    
    This class is defined in `src/document_analyzer_api/domain/models/retrieval.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    vector = "vector"
    graph = "graph"
    hybrid = "hybrid"


class KeywordsMode(str, Enum):
    """KeywordsMode component.
    
    This class is defined in `src/document_analyzer_api/domain/models/retrieval.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    metadata_only = "metadata_only"
    filter = "filter"
    rank_boost = "rank_boost"


@dataclass(slots=True)
class RetrievalRequest:
    """RetrievalRequest transport schema.
    
    This class is defined in `src/document_analyzer_api/domain/models/retrieval.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: query, retrieval_mode, document_ids, keywords, keywords_mode, top_k, min_score, hybrid_alpha.
    """
    query: str
    retrieval_mode: RetrievalMode = RetrievalMode.vector
    document_ids: list[str] | None = None
    keywords: list[str] = field(default_factory=list)
    keywords_mode: KeywordsMode = KeywordsMode.metadata_only
    top_k: int = 8
    min_score: float = 0.2
    hybrid_alpha: float = 0.5
    include_sources: bool = False


@dataclass(slots=True)
class RetrievalHit:
    """RetrievalHit component.
    
    This class is defined in `src/document_analyzer_api/domain/models/retrieval.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: document_id, chunk_id, content, score, metadata.
    """
    document_id: str
    chunk_id: str
    content: str
    score: float
    metadata: dict[str, Any]


@dataclass(slots=True)
class Citation:
    """Citation component.
    
    This class is defined in `src/document_analyzer_api/domain/models/retrieval.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: document_id, chunk_id, chunk_index.
    """
    document_id: str
    chunk_id: str
    chunk_index: int | None = None


@dataclass(slots=True)
class RetrievalResult:
    """RetrievalResult component.
    
    This class is defined in `src/document_analyzer_api/domain/models/retrieval.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: hits, citations.
    """
    hits: list[RetrievalHit]
    citations: list[Citation]

