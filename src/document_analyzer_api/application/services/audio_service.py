from .document_generation_service import DocumentGenerationService
from ...domain.ports.tts_provider import TTSProviderPort


class AudioService:
    def __init__(self, generation_service: DocumentGenerationService, tts_provider: TTSProviderPort) -> None:
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
        return self._tts_provider.synthesize(text=text, audio_format=audio_format)

