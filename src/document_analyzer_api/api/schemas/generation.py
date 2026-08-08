"""Module `src/document_analyzer_api/api/schemas/generation.py`.

This module belongs to the API schema layer of Document Analyzer.

Purpose:
- Implements a focused responsibility in the Document Analyzer codebase.

Defined symbols:
- Classes: KeywordsMode, RetrievalMode, OutputFormat, RetrievalOptionsCommon, RetrievalOptionsGraph, RetrievalOptionsHybrid, RetrievalOptions, DocumentGenerateRequest, DocumentGenerateResponse, DocumentSummaryRequest, DocumentSummaryResponse, ChatSessionCreateResponse, DocumentChatRequest, DocumentChatResponse.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from enum import Enum

from pydantic import BaseModel, Field


class KeywordsMode(str, Enum):
    """KeywordsMode component.
    
    This class is defined in `src/document_analyzer_api/api/schemas/generation.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    metadata_only = "metadata_only"
    filter = "filter"
    rank_boost = "rank_boost"


class RetrievalMode(str, Enum):
    """RetrievalMode component.
    
    This class is defined in `src/document_analyzer_api/api/schemas/generation.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    vector = "vector"
    graph = "graph"
    hybrid = "hybrid"


class OutputFormat(str, Enum):
    """OutputFormat component.
    
    This class is defined in `src/document_analyzer_api/api/schemas/generation.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    text = "text"
    audio = "audio"
    image = "image"
    text_image = "text+image"


class RetrievalOptionsCommon(BaseModel):
    """RetrievalOptionsCommon component.
    
    This class is defined in `src/document_analyzer_api/api/schemas/generation.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: topK, minScore.
    """
    topK: int = Field(default=8, ge=1)
    minScore: float = Field(default=0.2, ge=0.0)


class RetrievalOptionsHybrid(BaseModel):
    """RetrievalOptionsHybrid component.
    
    This class is defined in `src/document_analyzer_api/api/schemas/generation.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: hybridAlpha.
    """
    hybridAlpha: float = Field(default=0.5, ge=0.0, le=1.0)


class RetrievalOptionsGraph(BaseModel):
    """RetrievalOptionsGraph component.

    Graph traversal controls used by Neo4j-backed retrieval mode.
    """

    maxHops: int = Field(default=2, ge=1, le=6)


class RetrievalOptions(BaseModel):
    """RetrievalOptions component.
    
    This class is defined in `src/document_analyzer_api/api/schemas/generation.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: common, graph, hybrid.
    """
    common: RetrievalOptionsCommon = RetrievalOptionsCommon()
    graph: RetrievalOptionsGraph = RetrievalOptionsGraph()
    hybrid: RetrievalOptionsHybrid = RetrievalOptionsHybrid()


def _default_summary_retrieval_options() -> RetrievalOptions:
    """Create summary-friendly retrieval defaults with permissive evidence thresholding."""
    return RetrievalOptions(
        common=RetrievalOptionsCommon(topK=8, minScore=0.0),
        graph=RetrievalOptionsGraph(),
        hybrid=RetrievalOptionsHybrid(),
    )


class DocumentGenerateRequest(BaseModel):
    """DocumentGenerateRequest transport schema.
    
    This class is defined in `src/document_analyzer_api/api/schemas/generation.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: question, documentIds, keywords, keywordsMode, retrievalMode, retrievalOptions, outputFormat, includeSources.
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
    """DocumentGenerateResponse transport schema.
    
    This class is defined in `src/document_analyzer_api/api/schemas/generation.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: answer, citations.
    """
    answer: str
    citations: list[dict] = Field(default_factory=list)


class DocumentSummaryRequest(BaseModel):
    """DocumentSummaryRequest transport schema.
    
    This class is defined in `src/document_analyzer_api/api/schemas/generation.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: documentIds, keywords, keywordsMode, retrievalMode, retrievalOptions, summaryWordCount, summaryPrompt, includeSummary, outputFormat, generationOptions.
    """
    documentIds: list[str] | None = None
    keywords: list[str] = Field(default_factory=list)
    keywordsMode: KeywordsMode = KeywordsMode.metadata_only
    retrievalMode: RetrievalMode = RetrievalMode.vector
    retrievalOptions: RetrievalOptions = Field(default_factory=_default_summary_retrieval_options)
    summaryWordCount: int | None = Field(default=None, ge=1)
    summaryPrompt: str | None = Field(default=None, min_length=1)
    includeSummary: bool = False
    outputFormat: str = Field(default="md")
    generationOptions: dict = Field(default_factory=dict)


class DocumentSummaryResponse(BaseModel):
    """DocumentSummaryResponse transport schema.
    
    This class is defined in `src/document_analyzer_api/api/schemas/generation.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: url, summaryText.
    """
    url: str
    summaryText: str | None = None


class ChatSessionCreateResponse(BaseModel):
    """ChatSessionCreateResponse transport schema.
    
    This class is defined in `src/document_analyzer_api/api/schemas/generation.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: sessionId.
    """
    sessionId: str


class DocumentChatRequest(DocumentGenerateRequest):
    """DocumentChatRequest transport schema.
    
    This class is defined in `src/document_analyzer_api/api/schemas/generation.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: sessionId, compactContext.
    """
    sessionId: str = Field(min_length=1)
    compactContext: bool = False


class DocumentChatResponse(DocumentGenerateResponse):
    """DocumentChatResponse transport schema.
    
    This class is defined in `src/document_analyzer_api/api/schemas/generation.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: sessionId.
    """
    sessionId: str



