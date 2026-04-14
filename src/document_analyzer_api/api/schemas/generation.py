"""Detailed module documentation for `src/document_analyzer_api/api/schemas/generation.py`.

File role:
- Located in the API schema layer.
- Defines logic and symbols for `generation.py` within Document Analyzer V1.

Purpose:
- Supports a focused concern in the Document Analyzer codebase.

Exported symbols overview:
- Classes: KeywordsMode, RetrievalMode, OutputFormat, RetrievalOptionsCommon, RetrievalOptionsHybrid, RetrievalOptions, DocumentGenerateRequest, DocumentGenerateResponse, DocumentSummaryRequest, DocumentSummaryResponse, ChatSessionCreateResponse, DocumentChatRequest, DocumentChatResponse.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from enum import Enum

from pydantic import BaseModel, Field


class KeywordsMode(str, Enum):
    """Detailed class documentation for `KeywordsMode`.
    
    This component belongs to `src/document_analyzer_api/api/schemas/generation.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    metadata_only = "metadata_only"
    filter = "filter"
    rank_boost = "rank_boost"


class RetrievalMode(str, Enum):
    """Detailed class documentation for `RetrievalMode`.
    
    This component belongs to `src/document_analyzer_api/api/schemas/generation.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    vector = "vector"
    graph = "graph"
    hybrid = "hybrid"


class OutputFormat(str, Enum):
    """Detailed class documentation for `OutputFormat`.
    
    This component belongs to `src/document_analyzer_api/api/schemas/generation.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    text = "text"
    audio = "audio"
    image = "image"
    text_image = "text+image"


class RetrievalOptionsCommon(BaseModel):
    """Detailed class documentation for `RetrievalOptionsCommon`.
    
    This component belongs to `src/document_analyzer_api/api/schemas/generation.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    topK: int = Field(default=8, ge=1)
    minScore: float = Field(default=0.2, ge=0.0)


class RetrievalOptionsHybrid(BaseModel):
    """Detailed class documentation for `RetrievalOptionsHybrid`.
    
    This component belongs to `src/document_analyzer_api/api/schemas/generation.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    hybridAlpha: float = Field(default=0.5, ge=0.0, le=1.0)


class RetrievalOptions(BaseModel):
    """Detailed class documentation for `RetrievalOptions`.
    
    This component belongs to `src/document_analyzer_api/api/schemas/generation.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    common: RetrievalOptionsCommon = RetrievalOptionsCommon()
    hybrid: RetrievalOptionsHybrid = RetrievalOptionsHybrid()


class DocumentGenerateRequest(BaseModel):
    """Detailed class documentation for `DocumentGenerateRequest`.
    
    This transport schema model belongs to `src/document_analyzer_api/api/schemas/generation.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    question: str = Field(min_length=1)
    documentIds: list[str] | None = None
    keywords: list[str] = Field(default_factory=list)
    keywordsMode: KeywordsMode = KeywordsMode.metadata_only
    retrievalMode: RetrievalMode = RetrievalMode.vector
    retrievalOptions: RetrievalOptions = RetrievalOptions()
    outputFormat: OutputFormat = OutputFormat.text
    includeSources: bool = False
    stream: bool = True
    generationOptions: dict = Field(default_factory=dict)


class DocumentGenerateResponse(BaseModel):
    """Detailed class documentation for `DocumentGenerateResponse`.
    
    This transport schema model belongs to `src/document_analyzer_api/api/schemas/generation.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    answer: str
    citations: list[dict] = Field(default_factory=list)


class DocumentSummaryRequest(BaseModel):
    """Detailed class documentation for `DocumentSummaryRequest`.
    
    This transport schema model belongs to `src/document_analyzer_api/api/schemas/generation.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    documentIds: list[str] | None = None
    keywords: list[str] = Field(default_factory=list)
    outputFormat: str = Field(default="md")
    generationOptions: dict = Field(default_factory=dict)


class DocumentSummaryResponse(BaseModel):
    """Detailed class documentation for `DocumentSummaryResponse`.
    
    This transport schema model belongs to `src/document_analyzer_api/api/schemas/generation.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    url: str


class ChatSessionCreateResponse(BaseModel):
    """Detailed class documentation for `ChatSessionCreateResponse`.
    
    This transport schema model belongs to `src/document_analyzer_api/api/schemas/generation.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    sessionId: str


class DocumentChatRequest(DocumentGenerateRequest):
    """Detailed class documentation for `DocumentChatRequest`.
    
    This transport schema model belongs to `src/document_analyzer_api/api/schemas/generation.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    sessionId: str = Field(min_length=1)
    compactContext: bool = False


class DocumentChatResponse(DocumentGenerateResponse):
    """Detailed class documentation for `DocumentChatResponse`.
    
    This transport schema model belongs to `src/document_analyzer_api/api/schemas/generation.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    sessionId: str



