"""Detailed module documentation for `src/document_analyzer_api/domain/models/retrieval.py`.

File role:
- Located in the domain model layer.
- Defines logic and symbols for `retrieval.py` within Document Analyzer V1.

Purpose:
- Declares domain-level structures exchanged by services and adapters.

Exported symbols overview:
- Classes: RetrievalMode, KeywordsMode, RetrievalRequest, RetrievalHit, Citation, RetrievalResult.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RetrievalMode(str, Enum):
    """Detailed class documentation for `RetrievalMode`.
    
    This component belongs to `src/document_analyzer_api/domain/models/retrieval.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    vector = "vector"
    graph = "graph"
    hybrid = "hybrid"


class KeywordsMode(str, Enum):
    """Detailed class documentation for `KeywordsMode`.
    
    This component belongs to `src/document_analyzer_api/domain/models/retrieval.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    metadata_only = "metadata_only"
    filter = "filter"
    rank_boost = "rank_boost"


@dataclass(slots=True)
class RetrievalRequest:
    """Detailed class documentation for `RetrievalRequest`.
    
    This transport schema model belongs to `src/document_analyzer_api/domain/models/retrieval.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
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
    """Detailed class documentation for `RetrievalHit`.
    
    This component belongs to `src/document_analyzer_api/domain/models/retrieval.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    document_id: str
    chunk_id: str
    content: str
    score: float
    metadata: dict[str, Any]


@dataclass(slots=True)
class Citation:
    """Detailed class documentation for `Citation`.
    
    This component belongs to `src/document_analyzer_api/domain/models/retrieval.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    document_id: str
    chunk_id: str
    chunk_index: int | None = None


@dataclass(slots=True)
class RetrievalResult:
    """Detailed class documentation for `RetrievalResult`.
    
    This component belongs to `src/document_analyzer_api/domain/models/retrieval.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    hits: list[RetrievalHit]
    citations: list[Citation]

