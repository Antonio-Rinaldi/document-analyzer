"""Module `src/document_analyzer_api/domain/models/chat.py`.

This module belongs to the domain model layer of Document Analyzer.

Purpose:
- Declares domain objects exchanged across business workflows.

Defined symbols:
- Classes: ChatRole, ChatMessage, ChatSession.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class ChatRole(str, Enum):
    """ChatRole component.
    
    This class is defined in `src/document_analyzer_api/domain/models/chat.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    user = "user"
    assistant = "assistant"
    system = "system"


@dataclass(slots=True)
class ChatMessage:
    """ChatMessage component.
    
    This class is defined in `src/document_analyzer_api/domain/models/chat.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: role, content, created_at.
    """
    role: ChatRole
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class ChatSession:
    """ChatSession component.
    
    This class is defined in `src/document_analyzer_api/domain/models/chat.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: session_id, messages, expires_at.
    """
    session_id: str
    messages: list[ChatMessage] = field(default_factory=list)
    expires_at: datetime | None = None

