from typing import Protocol


class TextGenerationClientPort(Protocol):
    async def generate_answer(self, question: str, context_chunks: list[str]) -> str:
        ...

