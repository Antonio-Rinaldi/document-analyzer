from ...domain.ports.text_summarizer import TextSummarizerPort
from ...domain.models.chunking import DEFAULT_CONTEXTUAL_SUMMARY_PROMPT


class DeterministicSummarizer(TextSummarizerPort):
    async def summarize(self, target_text: str, context_text: str, prompt: str) -> str:
        normalized = " ".join(target_text.split())
        if not normalized:
            return ""
        words = normalized.split(" ")
        summary_words = words[:40]
        summary = " ".join(summary_words)
        if len(words) > 40:
            summary += " ..."
        custom_prompt = prompt.strip()
        if custom_prompt and custom_prompt != DEFAULT_CONTEXTUAL_SUMMARY_PROMPT:
            summary = f"[{custom_prompt}] {summary}"
        return summary



