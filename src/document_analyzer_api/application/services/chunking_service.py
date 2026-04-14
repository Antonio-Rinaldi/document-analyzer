"""Module `src/document_analyzer_api/application/services/chunking_service.py`.

This module belongs to the application service layer of Document Analyzer.

Purpose:
- Coordinates use-case workflows over domain ports and adapters.

Defined symbols:
- Classes: ChunkingService.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from ...domain.models.chunking import BaseChunk, ChunkingConfig, ChunkingStrategyName, FinalChunk
from ...domain.ports.text_summarizer import TextSummarizerPort


class ChunkingService:
    """ChunkingService application service.
    
    This class is defined in `src/document_analyzer_api/application/services/chunking_service.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, summarizer: TextSummarizerPort) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/chunking_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                summarizer: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._summarizer = summarizer

    async def apply_strategy(self, base_chunks: list[BaseChunk], config: ChunkingConfig) -> list[FinalChunk]:
        """Asynchronous execution path for `apply_strategy`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/chunking_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (FinalChunk, append, summarize) to satisfy the callable contract.
        
            Args:
                base_chunks: Input parameter accepted by `apply_strategy`.
                config: Input parameter accepted by `apply_strategy`.
        
            Returns:
                A value compatible with `list[FinalChunk]`.
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


