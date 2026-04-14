"""Module `src/document_analyzer_api/domain/ports/chat_session_repository.py`.

This module belongs to the domain abstraction layer of Document Analyzer.

Purpose:
- Declares protocol contracts implemented by infrastructure adapters.

Defined symbols:
- Classes: ChatSessionRepositoryPort.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from typing import Protocol

from ..models.chat import ChatSession


class ChatSessionRepositoryPort(Protocol):
    """ChatSessionRepositoryPort component.
    
    This class is defined in `src/document_analyzer_api/domain/ports/chat_session_repository.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    async def create(self, session_id: str, ttl_seconds: int) -> ChatSession:
        """Asynchronous execution path for `create`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/chat_session_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                session_id: Server-side chat session identifier.
                ttl_seconds: Input parameter accepted by `create`.
        
            Returns:
                A value compatible with `ChatSession`.
        """
        ...

    async def get(self, session_id: str) -> ChatSession | None:
        """Asynchronous execution path for `get`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/chat_session_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                session_id: Server-side chat session identifier.
        
            Returns:
                A value compatible with `ChatSession | None`.
        """
        ...

    async def upsert(self, session: ChatSession, ttl_seconds: int) -> None:
        """Asynchronous execution path for `upsert`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/chat_session_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                session: Input parameter accepted by `upsert`.
                ttl_seconds: Input parameter accepted by `upsert`.
        
            Returns:
                A value compatible with `None`.
        """
        ...

    async def delete(self, session_id: str) -> bool:
        """Asynchronous execution path for `delete`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/chat_session_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                session_id: Server-side chat session identifier.
        
            Returns:
                A value compatible with `bool`.
        """
        ...

