from .document_generation_service import DocumentGenerationService
from ...domain.ports.image_provider import ImageProviderPort


class ImageService:
    def __init__(self, generation_service: DocumentGenerationService, image_provider: ImageProviderPort) -> None:
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
        return self._image_provider.generate_from_text(text)

