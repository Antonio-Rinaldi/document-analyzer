"""Detailed module documentation for `src/document_analyzer_api/application/services/chunking_service.py`.

File role:
- Located in the application service layer.
- Defines logic and symbols for `chunking_service.py` within Document Analyzer V1.

Purpose:
- Implements use-case orchestration across domain ports and infrastructure adapters.

Exported symbols overview:
- Classes: ChunkingService.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from ...domain.models.chunking import BaseChunk, ChunkingConfig, ChunkingStrategyName, FinalChunk
from ...domain.ports.text_summarizer import TextSummarizerPort


class ChunkingService:
    """Detailed class documentation for `ChunkingService`.
    
    This application service belongs to `src/document_analyzer_api/application/services/chunking_service.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, summarizer: TextSummarizerPort) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/chunking_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                summarizer: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._summarizer = summarizer

    async def apply_strategy(self, base_chunks: list[BaseChunk], config: ChunkingConfig) -> list[FinalChunk]:
        """Detailed asynchronous function documentation for `apply_strategy`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/chunking_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                base_chunks: Input parameter for `apply_strategy`.
                config: Input parameter for `apply_strategy`.
        
            Returns:
                Value defined by `apply_strategy` contract and consumed by downstream callers.
        """
        if config.strategy == ChunkingStrategyName.meaningful:
            return [
                FinalChunk(chunk_id=chunk.chunk_id, content=chunk.text, metadata={**chunk.metadata})
                for chunk in base_chunks
            ]

        final_chunks: list[FinalChunk] = []
        for chunk in base_chunks:
            summary = await self._summarizer.summarize(
                target_text=chunk.text,
                context_text=chunk.context_text,
                prompt=config.contextual_summary_prompt,
            )
            final_chunks.append(
                FinalChunk(
                    chunk_id=chunk.chunk_id,
                    content=summary,
                    metadata={**chunk.metadata, "sourceExcerpt": chunk.text[:200]},
                )
            )
        return final_chunks


