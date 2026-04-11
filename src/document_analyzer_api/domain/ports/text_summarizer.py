from typing import Protocol


class TextSummarizerPort(Protocol):
    async def summarize(self, target_text: str, context_text: str, prompt: str) -> str:
        ...


