from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class DependencyStatus:
    name: str
    ok: bool
    detail: str


class DependencyHealthPort(Protocol):
    """Checks if an external dependency is reachable."""

    async def check(self) -> DependencyStatus:
        ...

