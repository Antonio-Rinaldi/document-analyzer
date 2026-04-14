"""Module `src/document_analyzer_api/application/services/audio_service.py`.

This module belongs to the application service layer of Document Analyzer.

Purpose:
- Coordinates use-case workflows over domain ports and adapters.

Defined symbols:
- Classes: AudioService.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from .document_generation_service import DocumentGenerationService
from ...domain.ports.tts_provider import TTSProviderPort


class AudioService:
    """AudioService application service.
    
    This class is defined in `src/document_analyzer_api/application/services/audio_service.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, generation_service: DocumentGenerationService, tts_provider: TTSProviderPort) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/audio_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                generation_service: Input parameter accepted by `__init__`.
                tts_provider: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._generation_service = generation_service
        self._tts_provider = tts_provider

    async def generate_audio_answer(
        self,
        *,
        question: str,
        document_ids: list[str] | None,
        keywords: list[str],
        keywords_mode: str,
        retrieval_mode: str,
        top_k: int,
        min_score: float,
        hybrid_alpha: float,
        include_sources: bool,
        audio_format: str,
    ) -> tuple[bytes, list[dict]]:
        """Asynchronous execution path for `generate_audio_answer`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/audio_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Generates derived output from context, prompts, and generation options.
        
            Args:
                question: User prompt processed by retrieval and generation workflows.
                document_ids: Optional subset of documents used to scope the operation.
                keywords: Optional keyword list used for retrieval metadata/filtering/boosting.
                keywords_mode: Keyword strategy selector (`metadata_only`, `filter`, `rank_boost`).
                retrieval_mode: Retrieval backend mode (`vector`, `graph`, or `hybrid`).
                top_k: Maximum number of retrieval hits retained for context assembly.
                min_score: Minimum score threshold used to discard low-confidence hits.
                hybrid_alpha: Fusion weight for hybrid retrieval blending.
                include_sources: Flag controlling citation extraction in response payloads.
                audio_format: Input parameter accepted by `generate_audio_answer`.
        
            Returns:
                A value compatible with `tuple[bytes, list[dict]]`.
        """
        answer, citations = await self._generation_service.generate(
            question=question,
            document_ids=document_ids,
            keywords=keywords,
            keywords_mode=keywords_mode,
            retrieval_mode=retrieval_mode,
            top_k=top_k,
            min_score=min_score,
            hybrid_alpha=hybrid_alpha,
            include_sources=include_sources,
        )
        audio_bytes = self._tts_provider.synthesize(text=answer, audio_format=audio_format)
        return audio_bytes, citations

    def render_audio(self, text: str, audio_format: str) -> bytes:
        """Synchronous execution path for `render_audio`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/audio_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (synthesize) to satisfy the callable contract.
        
            Args:
                text: Input parameter accepted by `render_audio`.
                audio_format: Input parameter accepted by `render_audio`.
        
            Returns:
                A value compatible with `bytes`.
        """
        return self._tts_provider.synthesize(text=text, audio_format=audio_format)

