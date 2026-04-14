"""Detailed module documentation for `src/document_analyzer_api/domain/ports/chat_session_repository.py`.

File role:
- Located in the domain port layer.
- Defines logic and symbols for `chat_session_repository.py` within Document Analyzer V1.

Purpose:
- Declares abstract contracts implemented by infrastructure adapters.

Exported symbols overview:
- Classes: ChatSessionRepositoryPort.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from typing import Protocol

from ..models.chat import ChatSession


class ChatSessionRepositoryPort(Protocol):
    """Detailed class documentation for `ChatSessionRepositoryPort`.
    
    This component belongs to `src/document_analyzer_api/domain/ports/chat_session_repository.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    async def create(self, session_id: str, ttl_seconds: int) -> ChatSession:
        """Detailed asynchronous function documentation for `create`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/chat_session_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                session_id: Server-side chat session identifier.
                ttl_seconds: Input parameter for `create`.
        
            Returns:
                Value defined by `create` contract and consumed by downstream callers.
        """
        ...

    async def get(self, session_id: str) -> ChatSession | None:
        """Detailed asynchronous function documentation for `get`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/chat_session_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                session_id: Server-side chat session identifier.
        
            Returns:
                Value defined by `get` contract and consumed by downstream callers.
        """
        ...

    async def upsert(self, session: ChatSession, ttl_seconds: int) -> None:
        """Detailed asynchronous function documentation for `upsert`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/chat_session_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                session: Input parameter for `upsert`.
                ttl_seconds: Input parameter for `upsert`.
        
            Returns:
                Value defined by `upsert` contract and consumed by downstream callers.
        """
        ...

    async def delete(self, session_id: str) -> bool:
        """Detailed asynchronous function documentation for `delete`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/chat_session_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                session_id: Server-side chat session identifier.
        
            Returns:
                Value defined by `delete` contract and consumed by downstream callers.
        """
        ...

