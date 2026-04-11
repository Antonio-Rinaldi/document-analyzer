import re

from ...domain.models.chunking import BaseChunk, ChunkGranularity, ChunkingConfig, ParsedDocument


class BaseChunkBuilderService:
    def build_chunks(self, document: ParsedDocument, config: ChunkingConfig) -> list[BaseChunk]:
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

