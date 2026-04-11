import asyncio
from pathlib import Path

from document_analyzer_api.application.services.chat_service import ChatService
from document_analyzer_api.domain.models.chat import ChatRole
from document_analyzer_api.infrastructure.persistence.local_chat_session_repository import LocalChatSessionRepository


class StubGenerationService:
    async def generate(self, **kwargs):
        return "answer", []


def test_chat_service_compacts_history_when_threshold_exceeded(tmp_path: Path) -> None:
    repository = LocalChatSessionRepository(root_path=str(tmp_path))
    service = ChatService(
        repository=repository,
        generation_service=StubGenerationService(),
        chat_ttl_seconds=3600,
        max_messages_before_compaction=2,
    )

    session_id = asyncio.run(service.create_session())
    asyncio.run(
        service.chat(
            session_id=session_id,
            question="first",
            document_ids=None,
            keywords=[],
            keywords_mode="metadata_only",
            retrieval_mode="vector",
            top_k=8,
            min_score=0.0,
            hybrid_alpha=0.5,
            include_sources=False,
            compact_context=False,
        )
    )
    asyncio.run(
        service.chat(
            session_id=session_id,
            question="second",
            document_ids=None,
            keywords=[],
            keywords_mode="metadata_only",
            retrieval_mode="vector",
            top_k=8,
            min_score=0.0,
            hybrid_alpha=0.5,
            include_sources=False,
            compact_context=False,
        )
    )

    session = asyncio.run(repository.get(session_id))
    assert session is not None
    assert session.messages
    assert any(message.role == ChatRole.system for message in session.messages)


def test_chat_service_delete_session(tmp_path: Path) -> None:
    repository = LocalChatSessionRepository(root_path=str(tmp_path))
    service = ChatService(
        repository=repository,
        generation_service=StubGenerationService(),
        chat_ttl_seconds=3600,
        max_messages_before_compaction=20,
    )

    session_id = asyncio.run(service.create_session())
    deleted = asyncio.run(service.delete_session(session_id))

    assert deleted is True
    assert asyncio.run(repository.get(session_id)) is None

