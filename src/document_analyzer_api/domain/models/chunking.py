from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ChunkingStrategyName(str, Enum):
    meaningful = "meaningful"
    contextual_summary = "contextual_summary"


class ChunkGranularity(str, Enum):
    chapter = "chapter"
    paragraph = "paragraph"
    sub_paragraph_tokens = "sub_paragraph_tokens"


DEFAULT_CONTEXTUAL_SUMMARY_PROMPT = "Write a concise neutral summary of the target chunk."


@dataclass(slots=True)
class ChunkingConfig:
    strategy: ChunkingStrategyName = ChunkingStrategyName.meaningful
    granularity: ChunkGranularity = ChunkGranularity.paragraph
    target_tokens: int = 350
    overlap_tokens: int = 60
    contextual_summary_prompt: str = DEFAULT_CONTEXTUAL_SUMMARY_PROMPT


@dataclass(slots=True)
class ParsedSection:
    section_id: str
    title: str
    text: str


@dataclass(slots=True)
class ParsedDocument:
    document_name: str
    sections: list[ParsedSection] = field(default_factory=list)


@dataclass(slots=True)
class BaseChunk:
    chunk_id: str
    section_id: str
    text: str
    context_text: str
    metadata: dict[str, Any]


@dataclass(slots=True)
class FinalChunk:
    chunk_id: str
    content: str
    metadata: dict[str, Any]



