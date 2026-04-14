from enum import Enum

from pydantic import BaseModel, Field


class KeywordsMode(str, Enum):
    metadata_only = "metadata_only"
    filter = "filter"
    rank_boost = "rank_boost"


class RetrievalMode(str, Enum):
    vector = "vector"
    graph = "graph"
    hybrid = "hybrid"


class OutputFormat(str, Enum):
    text = "text"
    audio = "audio"
    image = "image"
    text_image = "text+image"


class RetrievalOptionsCommon(BaseModel):
    topK: int = Field(default=8, ge=1)
    minScore: float = Field(default=0.2, ge=0.0)


class RetrievalOptionsHybrid(BaseModel):
    hybridAlpha: float = Field(default=0.5, ge=0.0, le=1.0)


class RetrievalOptions(BaseModel):
    common: RetrievalOptionsCommon = RetrievalOptionsCommon()
    hybrid: RetrievalOptionsHybrid = RetrievalOptionsHybrid()


class DocumentGenerateRequest(BaseModel):
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
    answer: str
    citations: list[dict] = Field(default_factory=list)


class DocumentSummaryRequest(BaseModel):
    documentIds: list[str] | None = None
    keywords: list[str] = Field(default_factory=list)
    outputFormat: str = Field(default="md")
    generationOptions: dict = Field(default_factory=dict)


class DocumentSummaryResponse(BaseModel):
    url: str


class ChatSessionCreateResponse(BaseModel):
    sessionId: str


class DocumentChatRequest(DocumentGenerateRequest):
    sessionId: str = Field(min_length=1)
    compactContext: bool = False


class DocumentChatResponse(DocumentGenerateResponse):
    sessionId: str



