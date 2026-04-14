"""Detailed module documentation for `src/document_analyzer_api/domain/models/chunking.py`.

File role:
- Located in the domain model layer.
- Defines logic and symbols for `chunking.py` within Document Analyzer V1.

Purpose:
- Declares domain-level structures exchanged by services and adapters.

Exported symbols overview:
- Classes: ChunkingStrategyName, ChunkGranularity, ChunkingConfig, ParsedSection, ParsedDocument, BaseChunk, FinalChunk.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ChunkingStrategyName(str, Enum):
    """Detailed class documentation for `ChunkingStrategyName`.
    
    This component belongs to `src/document_analyzer_api/domain/models/chunking.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    meaningful = "meaningful"
    contextual_summary = "contextual_summary"


class ChunkGranularity(str, Enum):
    """Detailed class documentation for `ChunkGranularity`.
    
    This component belongs to `src/document_analyzer_api/domain/models/chunking.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    chapter = "chapter"
    paragraph = "paragraph"
    sub_paragraph_tokens = "sub_paragraph_tokens"


DEFAULT_CONTEXTUAL_SUMMARY_PROMPT = "Write a concise neutral summary of the target chunk."


@dataclass(slots=True)
class ChunkingConfig:
    """Detailed class documentation for `ChunkingConfig`.
    
    This component belongs to `src/document_analyzer_api/domain/models/chunking.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    strategy: ChunkingStrategyName = ChunkingStrategyName.meaningful
    granularity: ChunkGranularity = ChunkGranularity.paragraph
    target_tokens: int = 350
    overlap_tokens: int = 60
    contextual_summary_prompt: str = DEFAULT_CONTEXTUAL_SUMMARY_PROMPT


@dataclass(slots=True)
class ParsedSection:
    """Detailed class documentation for `ParsedSection`.
    
    This component belongs to `src/document_analyzer_api/domain/models/chunking.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    section_id: str
    title: str
    text: str


@dataclass(slots=True)
class ParsedDocument:
    """Detailed class documentation for `ParsedDocument`.
    
    This component belongs to `src/document_analyzer_api/domain/models/chunking.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    document_name: str
    sections: list[ParsedSection] = field(default_factory=list)


@dataclass(slots=True)
class BaseChunk:
    """Detailed class documentation for `BaseChunk`.
    
    This component belongs to `src/document_analyzer_api/domain/models/chunking.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    chunk_id: str
    section_id: str
    text: str
    context_text: str
    metadata: dict[str, Any]


@dataclass(slots=True)
class FinalChunk:
    """Detailed class documentation for `FinalChunk`.
    
    This component belongs to `src/document_analyzer_api/domain/models/chunking.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    chunk_id: str
    content: str
    metadata: dict[str, Any]



