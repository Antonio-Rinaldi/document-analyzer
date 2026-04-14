from enum import Enum

from pydantic import BaseModel, Field


class ChunkingStrategy(str, Enum):
    meaningful = "meaningful"
    contextual_summary = "contextual_summary"


class ChunkGranularity(str, Enum):
    chapter = "chapter"
    paragraph = "paragraph"
    sub_paragraph_tokens = "sub_paragraph_tokens"


class SubParagraphOptions(BaseModel):
    targetTokens: int = Field(default=350, ge=50)
    overlapTokens: int = Field(default=60, ge=0)


class ContextualSummaryOptions(BaseModel):
    prompt: str = Field(default="Write a concise neutral summary of the target chunk.", min_length=1)


class ChunkingStrategyOptions(BaseModel):
    contextualSummary: ContextualSummaryOptions | None = None


class ChunkingOptions(BaseModel):
    strategy: ChunkingStrategy = ChunkingStrategy.meaningful
    granularity: ChunkGranularity = ChunkGranularity.paragraph
    subParagraph: SubParagraphOptions | None = None
    strategyOptions: ChunkingStrategyOptions | None = None


class DocumentIngestFileStatus(str, Enum):
    processed = "processed"
    already_processed = "already_processed"
    conflict = "conflict"
    unsupported_media_type = "unsupported_media_type"
    failed = "failed"


class DocumentIngestResult(BaseModel):
    name: str
    status: DocumentIngestFileStatus
    documentId: str | None = None
    errorCode: str | None = None
    error: str | None = None


class DocumentIngestResponse(BaseModel):
    results: list[DocumentIngestResult]


class DocumentListItem(BaseModel):
    id: str
    name: str
    description: str


class DocumentListResponse(BaseModel):
    items: list[DocumentListItem]
    offset: int
    limit: int
    total: int


class DocumentCapabilitiesResponse(BaseModel):
    supportedInputExtensions: list[str]
    supportedSummaryOutputFormats: list[str]



