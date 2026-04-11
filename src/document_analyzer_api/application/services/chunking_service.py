from ...domain.models.chunking import BaseChunk, ChunkingConfig, ChunkingStrategyName, FinalChunk
from ...domain.ports.text_summarizer import TextSummarizerPort


class ChunkingService:
    def __init__(self, summarizer: TextSummarizerPort) -> None:
        self._summarizer = summarizer

    async def apply_strategy(self, base_chunks: list[BaseChunk], config: ChunkingConfig) -> list[FinalChunk]:
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


