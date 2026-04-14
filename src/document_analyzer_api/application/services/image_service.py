"""Module `src/document_analyzer_api/application/services/image_service.py`.

This module belongs to the application service layer of Document Analyzer.

Purpose:
- Coordinates use-case workflows over domain ports and adapters.

Defined symbols:
- Classes: ImageService.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from .document_generation_service import DocumentGenerationService
from ...domain.ports.image_provider import ImageProviderPort


class ImageService:
    """ImageService application service.
    
    This class is defined in `src/document_analyzer_api/application/services/image_service.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, generation_service: DocumentGenerationService, image_provider: ImageProviderPort) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/image_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                generation_service: Input parameter accepted by `__init__`.
                image_provider: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._generation_service = generation_service
        self._image_provider = image_provider

    async def generate_image_answer(
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
    ) -> tuple[str, dict, list[dict]]:
        """Asynchronous execution path for `generate_image_answer`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/image_service.py` and contributes to module-level behavior
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
        
            Returns:
                A value compatible with `tuple[str, dict, list[dict]]`.
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
        image_payload = self._image_provider.generate_from_text(answer)
        return answer, image_payload, citations

    def render_image(self, text: str) -> dict:
        """Synchronous execution path for `render_image`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/image_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (generate_from_text) to satisfy the callable contract.
        
            Args:
                text: Input parameter accepted by `render_image`.
        
            Returns:
                A value compatible with `dict`.
        """
        return self._image_provider.generate_from_text(text)

