import uuid

from ...domain.models.chat import ChatMessage, ChatRole
from ...observability.tracing import set_span_attribute, start_span
from ...domain.ports.chat_session_repository import ChatSessionRepositoryPort
from .document_generation_service import DocumentGenerationService


class ChatService:
    def __init__(
        self,
        *,
        repository: ChatSessionRepositoryPort,
        generation_service: DocumentGenerationService,
        chat_ttl_seconds: int,
        max_messages_before_compaction: int,
    ) -> None:
        self._repository = repository
        self._generation_service = generation_service
        self._chat_ttl_seconds = chat_ttl_seconds
        self._max_messages_before_compaction = max_messages_before_compaction

    async def create_session(self) -> str:
        session_id = uuid.uuid4().hex
        await self._repository.create(session_id=session_id, ttl_seconds=self._chat_ttl_seconds)
        return session_id

    async def delete_session(self, session_id: str) -> bool:
        return await self._repository.delete(session_id)

    async def chat(
        self,
        *,
        session_id: str,
        question: str,
        document_ids: list[str] | None,
        keywords: list[str],
        keywords_mode: str,
        retrieval_mode: str,
        top_k: int,
        min_score: float,
        hybrid_alpha: float,
        include_sources: bool,
        compact_context: bool,
    ) -> tuple[str, list[dict]]:
        with start_span("document.chat"):
            set_span_attribute("session_id", session_id)
            session = await self._repository.get(session_id)
            if session is None:
                raise ValueError("Session not found")

            session.messages.append(ChatMessage(role=ChatRole.user, content=question))

            if compact_context or len(session.messages) > self._max_messages_before_compaction:
                session.messages = self._compact_messages(session.messages)

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

            session.messages.append(ChatMessage(role=ChatRole.assistant, content=answer))
            await self._repository.upsert(session, ttl_seconds=self._chat_ttl_seconds)
            return answer, citations

    def _compact_messages(self, messages: list[ChatMessage]) -> list[ChatMessage]:
        if len(messages) <= 2:
            return messages

        old_messages = messages[:-2]
        recent_messages = messages[-2:]
        summary = " ".join(message.content for message in old_messages)
        compacted = ChatMessage(role=ChatRole.system, content=f"Context summary: {summary[:500]}")
        return [compacted, *recent_messages]


