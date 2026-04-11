from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RetrievalMode(str, Enum):
    vector = "vector"
    graph = "graph"
    hybrid = "hybrid"


class KeywordsMode(str, Enum):
    metadata_only = "metadata_only"
    filter = "filter"
    rank_boost = "rank_boost"


@dataclass(slots=True)
class RetrievalRequest:
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
    document_id: str
    chunk_id: str
    content: str
    score: float
    metadata: dict[str, Any]


@dataclass(slots=True)
class Citation:
    document_id: str
    chunk_id: str
    chunk_index: int | None = None


@dataclass(slots=True)
class RetrievalResult:
    hits: list[RetrievalHit]
    citations: list[Citation]

