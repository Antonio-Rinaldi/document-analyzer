"""Detailed module documentation for `src/document_analyzer_api/domain/models/chat.py`.

File role:
- Located in the domain model layer.
- Defines logic and symbols for `chat.py` within Document Analyzer V1.

Purpose:
- Declares domain-level structures exchanged by services and adapters.

Exported symbols overview:
- Classes: ChatRole, ChatMessage, ChatSession.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class ChatRole(str, Enum):
    """Detailed class documentation for `ChatRole`.
    
    This component belongs to `src/document_analyzer_api/domain/models/chat.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    user = "user"
    assistant = "assistant"
    system = "system"


@dataclass(slots=True)
class ChatMessage:
    """Detailed class documentation for `ChatMessage`.
    
    This component belongs to `src/document_analyzer_api/domain/models/chat.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    role: ChatRole
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class ChatSession:
    """Detailed class documentation for `ChatSession`.
    
    This component belongs to `src/document_analyzer_api/domain/models/chat.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    session_id: str
    messages: list[ChatMessage] = field(default_factory=list)
    expires_at: datetime | None = None

