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
        for section in document.sections:
            if config.granularity == ChunkGranularity.chapter:
                chunks.append(
                    BaseChunk(
                        chunk_id=f"{section.section_id}:0",
                        section_id=section.section_id,
                        text=section.text.strip(),
                        context_text=section.text,
                        metadata={"sectionTitle": section.title, "granularity": config.granularity.value},
                    )
                )
                continue

            if config.granularity == ChunkGranularity.paragraph:
                paragraphs = [p.strip() for p in re.split(r"\n\s*\n", section.text) if p.strip()]
                if not paragraphs and section.text.strip():
                    paragraphs = [section.text.strip()]
                for idx, paragraph in enumerate(paragraphs):
                    chunks.append(
                        BaseChunk(
                            chunk_id=f"{section.section_id}:{idx}",
                            section_id=section.section_id,
                            text=paragraph,
                            context_text=section.text,
                            metadata={"sectionTitle": section.title, "granularity": config.granularity.value},
                        )
                    )
                continue

            chunks.extend(self._build_sub_paragraph_chunks(section.section_id, section.title, section.text, config))

        return chunks

    def _build_sub_paragraph_chunks(
        self,
        section_id: str,
        section_title: str,
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
        words = [word for word in text.split() if word]
        if not words:
            return []

        target = max(config.target_tokens, 1)
        overlap = max(min(config.overlap_tokens, target - 1), 0)
        step = max(target - overlap, 1)

        chunks: list[BaseChunk] = []
        index = 0
        chunk_idx = 0
        while index < len(words):
            piece = " ".join(words[index : index + target])
            chunks.append(
                BaseChunk(
                    chunk_id=f"{section_id}:{chunk_idx}",
                    section_id=section_id,
                    text=piece,
                    context_text=text,
                    metadata={"sectionTitle": section_title, "granularity": config.granularity.value},
                )
            )
            chunk_idx += 1
            index += step

        return chunks

