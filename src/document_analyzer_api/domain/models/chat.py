from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class ChatRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


@dataclass(slots=True)
class ChatMessage:
    role: ChatRole
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class ChatSession:
    session_id: str
    messages: list[ChatMessage] = field(default_factory=list)
    expires_at: datetime | None = None

