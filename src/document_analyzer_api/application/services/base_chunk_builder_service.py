"""Detailed module documentation for `src/document_analyzer_api/application/services/base_chunk_builder_service.py`.

File role:
- Located in the application service layer.
- Defines logic and symbols for `base_chunk_builder_service.py` within Document Analyzer V1.

Purpose:
- Implements use-case orchestration across domain ports and infrastructure adapters.

Exported symbols overview:
- Classes: BaseChunkBuilderService.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

import re

from ...domain.models.chunking import BaseChunk, ChunkGranularity, ChunkingConfig, ParsedDocument


class BaseChunkBuilderService:
    """Detailed class documentation for `BaseChunkBuilderService`.
    
    This application service belongs to `src/document_analyzer_api/application/services/base_chunk_builder_service.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def build_chunks(self, document: ParsedDocument, config: ChunkingConfig) -> list[BaseChunk]:
        """Detailed synchronous function documentation for `build_chunks`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/base_chunk_builder_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                document: Input parameter for `build_chunks`.
                config: Input parameter for `build_chunks`.
        
            Returns:
                Value defined by `build_chunks` contract and consumed by downstream callers.
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
        """Detailed synchronous function documentation for `_build_sub_paragraph_chunks`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/base_chunk_builder_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                section_id: Input parameter for `_build_sub_paragraph_chunks`.
                section_title: Input parameter for `_build_sub_paragraph_chunks`.
                text: Input parameter for `_build_sub_paragraph_chunks`.
                config: Input parameter for `_build_sub_paragraph_chunks`.
        
            Returns:
                Value defined by `_build_sub_paragraph_chunks` contract and consumed by downstream callers.
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

