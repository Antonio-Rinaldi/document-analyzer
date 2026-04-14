"""Detailed module documentation for `tests/unit/test_chat_service.py`.

File role:
- Located in the project layer.
- Defines logic and symbols for `test_chat_service.py` within Document Analyzer V1.

Purpose:
- Supports a focused concern in the Document Analyzer codebase.

Exported symbols overview:
- Classes: StubGenerationService.
- Functions: test_chat_service_compacts_history_when_threshold_exceeded, test_chat_service_delete_session.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

import asyncio
from pathlib import Path

from document_analyzer_api.application.services.chat_service import ChatService
from document_analyzer_api.domain.models.chat import ChatRole
from document_analyzer_api.infrastructure.persistence.local_chat_session_repository import LocalChatSessionRepository


class StubGenerationService:
    """Detailed class documentation for `StubGenerationService`.
    
    This application service belongs to `tests/unit/test_chat_service.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    async def generate(self, **kwargs):
        """Detailed asynchronous function documentation for `generate`.
        
        This callable is implemented in `tests/unit/test_chat_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Generates derived output from retrieved context and provided options.
        
            Args:
                **kwargs: Input parameter for `generate`.
        
            Returns:
                Value defined by `generate` contract and consumed by downstream callers.
        """
        return "answer", []


def test_chat_service_compacts_history_when_threshold_exceeded(tmp_path: Path) -> None:
    """Detailed synchronous function documentation for `test_chat_service_compacts_history_when_threshold_exceeded`.
    
    This callable is implemented in `tests/unit/test_chat_service.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            tmp_path: Input parameter for `test_chat_service_compacts_history_when_threshold_exceeded`.
    
        Returns:
            Value defined by `test_chat_service_compacts_history_when_threshold_exceeded` contract and consumed by downstream callers.
    """
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
    """Detailed synchronous function documentation for `test_chat_service_delete_session`.
    
    This callable is implemented in `tests/unit/test_chat_service.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            tmp_path: Input parameter for `test_chat_service_delete_session`.
    
        Returns:
            Value defined by `test_chat_service_delete_session` contract and consumed by downstream callers.
    """
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

