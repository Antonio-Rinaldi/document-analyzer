"""Module `src/document_analyzer_api/api/schemas/documents.py`.

This module belongs to the API schema layer of Document Analyzer.

Purpose:
- Implements a focused responsibility in the Document Analyzer codebase.

Defined symbols:
- Classes: ChunkingStrategy, ChunkGranularity, SubParagraphOptions, ContextualSummaryOptions, ChunkingStrategyOptions, ChunkingOptions, DocumentIngestFileStatus, DocumentIngestResult, DocumentIngestResponse, DocumentListItem, DocumentListResponse, DocumentCapabilitiesResponse.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from enum import Enum

from pydantic import BaseModel, Field


class ChunkingStrategy(str, Enum):
    """ChunkingStrategy component.
    
    This class is defined in `src/document_analyzer_api/api/schemas/documents.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    meaningful = "meaningful"
    contextual_summary = "contextual_summary"


class ChunkGranularity(str, Enum):
    """ChunkGranularity component.
    
    This class is defined in `src/document_analyzer_api/api/schemas/documents.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    chapter = "chapter"
    paragraph = "paragraph"
    sub_paragraph_tokens = "sub_paragraph_tokens"


class SubParagraphOptions(BaseModel):
    """SubParagraphOptions component.
    
    This class is defined in `src/document_analyzer_api/api/schemas/documents.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: targetTokens, overlapTokens.
    """
    targetTokens: int = Field(default=350, ge=50)
    overlapTokens: int = Field(default=60, ge=0)


class ContextualSummaryOptions(BaseModel):
    """ContextualSummaryOptions component.
    
    This class is defined in `src/document_analyzer_api/api/schemas/documents.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: prompt.
    """
    prompt: str = Field(default="Write a concise neutral summary of the target chunk.", min_length=1)


class ChunkingStrategyOptions(BaseModel):
    """ChunkingStrategyOptions component.
    
    This class is defined in `src/document_analyzer_api/api/schemas/documents.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: contextualSummary.
    """
    contextualSummary: ContextualSummaryOptions | None = None


class ChunkingOptions(BaseModel):
    """ChunkingOptions component.
    
    This class is defined in `src/document_analyzer_api/api/schemas/documents.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: strategy, granularity, subParagraph, strategyOptions.
    """
    strategy: ChunkingStrategy = ChunkingStrategy.meaningful
    granularity: ChunkGranularity = ChunkGranularity.paragraph
    subParagraph: SubParagraphOptions | None = None
    strategyOptions: ChunkingStrategyOptions | None = None


class DocumentIngestFileStatus(str, Enum):
    """DocumentIngestFileStatus component.
    
    This class is defined in `src/document_analyzer_api/api/schemas/documents.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    processed = "processed"
    already_processed = "already_processed"
    conflict = "conflict"
    unsupported_media_type = "unsupported_media_type"
    failed = "failed"


class DocumentIngestResult(BaseModel):
    """DocumentIngestResult component.
    
    This class is defined in `src/document_analyzer_api/api/schemas/documents.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: name, status, documentId, errorCode, error.
    """
    name: str
    status: DocumentIngestFileStatus
    documentId: str | None = None
    errorCode: str | None = None
    error: str | None = None


class DocumentIngestResponse(BaseModel):
    """DocumentIngestResponse transport schema.
    
    This class is defined in `src/document_analyzer_api/api/schemas/documents.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: results.
    """
    results: list[DocumentIngestResult]


class DocumentListItem(BaseModel):
    """DocumentListItem component.
    
    This class is defined in `src/document_analyzer_api/api/schemas/documents.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: id, name, description.
    """
    id: str
    name: str
    description: str


class DocumentListResponse(BaseModel):
    """DocumentListResponse transport schema.
    
    This class is defined in `src/document_analyzer_api/api/schemas/documents.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: items, offset, limit, total.
    """
    items: list[DocumentListItem]
    offset: int
    limit: int
    total: int


class DocumentCapabilitiesResponse(BaseModel):
    """DocumentCapabilitiesResponse transport schema.
    
    This class is defined in `src/document_analyzer_api/api/schemas/documents.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: supportedInputExtensions, supportedSummaryOutputFormats.
    """
    supportedInputExtensions: list[str]
    supportedSummaryOutputFormats: list[str]



