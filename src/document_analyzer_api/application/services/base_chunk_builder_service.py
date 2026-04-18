"""Module `src/document_analyzer_api/application/services/base_chunk_builder_service.py`.

This module belongs to the application service layer of Document Analyzer.

Purpose:
- Coordinates use-case workflows over domain ports and adapters.

Defined symbols:
- Classes: BaseChunkBuilderService.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import re

from ...domain.models.chunking import BaseChunk, ChunkGranularity, ChunkingConfig, ParsedDocument


class BaseChunkBuilderService:
    """BaseChunkBuilderService application service.
    
    This class is defined in `src/document_analyzer_api/application/services/base_chunk_builder_service.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def build_chunks(self, document: ParsedDocument, config: ChunkingConfig) -> list[BaseChunk]:
        """Synchronous execution path for `build_chunks`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/base_chunk_builder_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (BaseChunk, _build_sub_paragraph_chunks, append, enumerate) to satisfy the callable contract.
        
            Args:
                document: Input parameter accepted by `build_chunks`.
                config: Input parameter accepted by `build_chunks`.
        
            Returns:
                A value compatible with `list[BaseChunk]`.
        """
        chunks: list[BaseChunk] = []
        for chapter_index, section in enumerate(document.sections):
            if config.granularity == ChunkGranularity.chapter:
                chunks.append(
                    BaseChunk(
                        chunk_id=f"{section.section_id}:0",
                        section_id=section.section_id,
                        text=section.text.strip(),
                        context_text=section.text,
                        metadata=self._build_chunk_metadata(
                            chapter_id=section.section_id,
                            chapter_title=section.title,
                            chapter_index=chapter_index,
                            paragraph_index=0,
                            paragraph_chunk_index=0,
                            granularity=config.granularity,
                        ),
                    )
                )
                continue

            if config.granularity == ChunkGranularity.paragraph:
                paragraphs = self._split_paragraphs(section.text)
                for idx, paragraph in enumerate(paragraphs):
                    chunks.append(
                        BaseChunk(
                            chunk_id=f"{section.section_id}:{idx}",
                            section_id=section.section_id,
                            text=paragraph,
                            context_text=section.text,
                            metadata=self._build_chunk_metadata(
                                chapter_id=section.section_id,
                                chapter_title=section.title,
                                chapter_index=chapter_index,
                                paragraph_index=idx,
                                paragraph_chunk_index=0,
                                granularity=config.granularity,
                            ),
                        )
                    )
                continue

            chunks.extend(
                self._build_sub_paragraph_chunks(
                    section_id=section.section_id,
                    section_title=section.title,
                    chapter_index=chapter_index,
                    text=section.text,
                    config=config,
                )
            )

        return chunks

    def _build_sub_paragraph_chunks(
        self,
        section_id: str,
        section_title: str,
        chapter_index: int,
        text: str,
        config: ChunkingConfig,
    ) -> list[BaseChunk]:
        """Synchronous execution path for `_build_sub_paragraph_chunks`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/base_chunk_builder_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (BaseChunk, append, join, len) to satisfy the callable contract.
        
            Args:
                section_id: Input parameter accepted by `_build_sub_paragraph_chunks`.
                section_title: Input parameter accepted by `_build_sub_paragraph_chunks`.
                text: Input parameter accepted by `_build_sub_paragraph_chunks`.
                config: Input parameter accepted by `_build_sub_paragraph_chunks`.
        
            Returns:
                A value compatible with `list[BaseChunk]`.
        """
        target = max(config.target_tokens, 1)
        overlap = max(min(config.overlap_tokens, target - 1), 0)
        step = max(target - overlap, 1)

        chunks: list[BaseChunk] = []
        chunk_idx = 0
        for paragraph_index, paragraph_text in enumerate(self._split_paragraphs(text)):
            words = [word for word in paragraph_text.split() if word]
            index = 0
            paragraph_chunk_index = 0
            while index < len(words):
                piece = " ".join(words[index : index + target])
                chunks.append(
                    BaseChunk(
                        chunk_id=f"{section_id}:{chunk_idx}",
                        section_id=section_id,
                        text=piece,
                        context_text=text,
                        metadata=self._build_chunk_metadata(
                            chapter_id=section_id,
                            chapter_title=section_title,
                            chapter_index=chapter_index,
                            paragraph_index=paragraph_index,
                            paragraph_chunk_index=paragraph_chunk_index,
                            granularity=config.granularity,
                        ),
                    )
                )
                chunk_idx += 1
                paragraph_chunk_index += 1
                index += step

        return chunks

    @staticmethod
    def _split_paragraphs(text: str) -> list[str]:
        """Return trimmed non-empty paragraphs from section text with safe fallback."""
        paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", text) if paragraph.strip()]
        if paragraphs:
            return paragraphs
        fallback = text.strip()
        return [fallback] if fallback else []

    @staticmethod
    def _build_chunk_metadata(
        *,
        chapter_id: str,
        chapter_title: str,
        chapter_index: int,
        paragraph_index: int,
        paragraph_chunk_index: int,
        granularity: ChunkGranularity,
    ) -> dict[str, str | int]:
        """Build hierarchy-aware metadata consumed by persistence and graph retrieval adapters."""
        paragraph_id = f"{chapter_id}:p{paragraph_index}"
        return {
            "sectionTitle": chapter_title,
            "chapterId": chapter_id,
            "chapterTitle": chapter_title,
            "chapterIndex": chapter_index,
            "paragraphId": paragraph_id,
            "paragraphIndex": paragraph_index,
            "paragraphChunkIndex": paragraph_chunk_index,
            "granularity": granularity.value,
        }

