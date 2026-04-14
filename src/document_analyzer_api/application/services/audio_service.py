"""Detailed module documentation for `src/document_analyzer_api/application/services/audio_service.py`.

File role:
- Located in the application service layer.
- Defines logic and symbols for `audio_service.py` within Document Analyzer V1.

Purpose:
- Implements use-case orchestration across domain ports and infrastructure adapters.

Exported symbols overview:
- Classes: AudioService.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from .document_generation_service import DocumentGenerationService
from ...domain.ports.tts_provider import TTSProviderPort


class AudioService:
    """Detailed class documentation for `AudioService`.
    
    This application service belongs to `src/document_analyzer_api/application/services/audio_service.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, generation_service: DocumentGenerationService, tts_provider: TTSProviderPort) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/audio_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                generation_service: Input parameter for `__init__`.
                tts_provider: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
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
        """Detailed asynchronous function documentation for `generate_audio_answer`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/audio_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Generates derived output from retrieved context and provided options.
        
            Args:
                question: User question or prompt text to process.
                document_ids: Optional subset of document identifiers to scope the operation.
                keywords: Optional keyword list used by retrieval behavior.
                keywords_mode: Retrieval keyword strategy selector.
                retrieval_mode: Retrieval backend mode (`vector`, `graph`, or `hybrid`).
                top_k: Maximum number of retrieved items considered in downstream steps.
                min_score: Minimum score threshold used to accept retrieval hits.
                hybrid_alpha: Fusion weight used when hybrid retrieval mode is selected.
                include_sources: Flag controlling citation/source emission in responses.
                audio_format: Input parameter for `generate_audio_answer`.
        
            Returns:
                Value defined by `generate_audio_answer` contract and consumed by downstream callers.
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
        """Detailed synchronous function documentation for `render_audio`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/audio_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                text: Input parameter for `render_audio`.
                audio_format: Input parameter for `render_audio`.
        
            Returns:
                Value defined by `render_audio` contract and consumed by downstream callers.
        """
        return self._tts_provider.synthesize(text=text, audio_format=audio_format)

