"""Module `src/document_analyzer_api/domain/models/chunking.py`.

This module belongs to the domain model layer of Document Analyzer.

Purpose:
- Declares domain objects exchanged across business workflows.

Defined symbols:
- Classes: ChunkingStrategyName, ChunkGranularity, ChunkingConfig, ParsedSection, ParsedDocument, BaseChunk, FinalChunk.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ChunkingStrategyName(str, Enum):
    """ChunkingStrategyName component.
    
    This class is defined in `src/document_analyzer_api/domain/models/chunking.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    meaningful = "meaningful"
    contextual_summary = "contextual_summary"


class ChunkGranularity(str, Enum):
    """ChunkGranularity component.
    
    This class is defined in `src/document_analyzer_api/domain/models/chunking.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    chapter = "chapter"
    paragraph = "paragraph"
    sub_paragraph_tokens = "sub_paragraph_tokens"


DEFAULT_CONTEXTUAL_SUMMARY_PROMPT = "Write a concise neutral summary of the target chunk."


@dataclass(slots=True)
class ChunkingConfig:
    """ChunkingConfig component.
    
    This class is defined in `src/document_analyzer_api/domain/models/chunking.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: strategy, granularity, target_tokens, overlap_tokens, contextual_summary_prompt.
    """
    strategy: ChunkingStrategyName = ChunkingStrategyName.meaningful
    granularity: ChunkGranularity = ChunkGranularity.paragraph
    target_tokens: int = 350
    overlap_tokens: int = 60
    contextual_summary_prompt: str = DEFAULT_CONTEXTUAL_SUMMARY_PROMPT


@dataclass(slots=True)
class ParsedSection:
    """ParsedSection component.
    
    This class is defined in `src/document_analyzer_api/domain/models/chunking.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: section_id, title, text.
    """
    section_id: str
    title: str
    text: str


@dataclass(slots=True)
class ParsedDocument:
    """ParsedDocument component.
    
    This class is defined in `src/document_analyzer_api/domain/models/chunking.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: document_name, sections.
    """
    document_name: str
    sections: list[ParsedSection] = field(default_factory=list)


@dataclass(slots=True)
class BaseChunk:
    """BaseChunk component.
    
    This class is defined in `src/document_analyzer_api/domain/models/chunking.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: chunk_id, section_id, text, context_text, metadata.
    """
    chunk_id: str
    section_id: str
    text: str
    context_text: str
    metadata: dict[str, Any]


@dataclass(slots=True)
class FinalChunk:
    """FinalChunk component.
    
    This class is defined in `src/document_analyzer_api/domain/models/chunking.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: chunk_id, content, metadata.
    """
    chunk_id: str
    content: str
    metadata: dict[str, Any]



