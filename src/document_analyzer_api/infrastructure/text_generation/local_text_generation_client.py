from ...domain.ports.text_generation_client import TextGenerationClientPort


class LocalTextGenerationClient(TextGenerationClientPort):
    async def generate_answer(self, question: str, context_chunks: list[str]) -> str:
        context = " ".join(context_chunks[:3])
        return f"Based on selected documents: {context}" if context else ""

