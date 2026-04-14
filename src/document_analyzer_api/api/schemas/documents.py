"""Detailed module documentation for `src/document_analyzer_api/api/schemas/documents.py`.

File role:
- Located in the API schema layer.
- Defines logic and symbols for `documents.py` within Document Analyzer V1.

Purpose:
- Supports a focused concern in the Document Analyzer codebase.

Exported symbols overview:
- Classes: ChunkingStrategy, ChunkGranularity, SubParagraphOptions, ContextualSummaryOptions, ChunkingStrategyOptions, ChunkingOptions, DocumentIngestFileStatus, DocumentIngestResult, DocumentIngestResponse, DocumentListItem, DocumentListResponse, DocumentCapabilitiesResponse.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from enum import Enum

from pydantic import BaseModel, Field


class ChunkingStrategy(str, Enum):
    """Detailed class documentation for `ChunkingStrategy`.
    
    This component belongs to `src/document_analyzer_api/api/schemas/documents.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    meaningful = "meaningful"
    contextual_summary = "contextual_summary"


class ChunkGranularity(str, Enum):
    """Detailed class documentation for `ChunkGranularity`.
    
    This component belongs to `src/document_analyzer_api/api/schemas/documents.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    chapter = "chapter"
    paragraph = "paragraph"
    sub_paragraph_tokens = "sub_paragraph_tokens"


class SubParagraphOptions(BaseModel):
    """Detailed class documentation for `SubParagraphOptions`.
    
    This component belongs to `src/document_analyzer_api/api/schemas/documents.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    targetTokens: int = Field(default=350, ge=50)
    overlapTokens: int = Field(default=60, ge=0)


class ContextualSummaryOptions(BaseModel):
    """Detailed class documentation for `ContextualSummaryOptions`.
    
    This component belongs to `src/document_analyzer_api/api/schemas/documents.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    prompt: str = Field(default="Write a concise neutral summary of the target chunk.", min_length=1)


class ChunkingStrategyOptions(BaseModel):
    """Detailed class documentation for `ChunkingStrategyOptions`.
    
    This component belongs to `src/document_analyzer_api/api/schemas/documents.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    contextualSummary: ContextualSummaryOptions | None = None


class ChunkingOptions(BaseModel):
    """Detailed class documentation for `ChunkingOptions`.
    
    This component belongs to `src/document_analyzer_api/api/schemas/documents.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    strategy: ChunkingStrategy = ChunkingStrategy.meaningful
    granularity: ChunkGranularity = ChunkGranularity.paragraph
    subParagraph: SubParagraphOptions | None = None
    strategyOptions: ChunkingStrategyOptions | None = None


class DocumentIngestFileStatus(str, Enum):
    """Detailed class documentation for `DocumentIngestFileStatus`.
    
    This component belongs to `src/document_analyzer_api/api/schemas/documents.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    processed = "processed"
    already_processed = "already_processed"
    conflict = "conflict"
    unsupported_media_type = "unsupported_media_type"
    failed = "failed"


class DocumentIngestResult(BaseModel):
    """Detailed class documentation for `DocumentIngestResult`.
    
    This component belongs to `src/document_analyzer_api/api/schemas/documents.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    name: str
    status: DocumentIngestFileStatus
    documentId: str | None = None
    errorCode: str | None = None
    error: str | None = None


class DocumentIngestResponse(BaseModel):
    """Detailed class documentation for `DocumentIngestResponse`.
    
    This transport schema model belongs to `src/document_analyzer_api/api/schemas/documents.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    results: list[DocumentIngestResult]


class DocumentListItem(BaseModel):
    """Detailed class documentation for `DocumentListItem`.
    
    This component belongs to `src/document_analyzer_api/api/schemas/documents.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    id: str
    name: str
    description: str


class DocumentListResponse(BaseModel):
    """Detailed class documentation for `DocumentListResponse`.
    
    This transport schema model belongs to `src/document_analyzer_api/api/schemas/documents.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    items: list[DocumentListItem]
    offset: int
    limit: int
    total: int


class DocumentCapabilitiesResponse(BaseModel):
    """Detailed class documentation for `DocumentCapabilitiesResponse`.
    
    This transport schema model belongs to `src/document_analyzer_api/api/schemas/documents.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    supportedInputExtensions: list[str]
    supportedSummaryOutputFormats: list[str]



