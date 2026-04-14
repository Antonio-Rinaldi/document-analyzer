"""Detailed module documentation for `src/document_analyzer_api/domain/ports/document_storage.py`.

File role:
- Located in the domain port layer.
- Defines logic and symbols for `document_storage.py` within Document Analyzer V1.

Purpose:
- Declares abstract contracts implemented by infrastructure adapters.

Exported symbols overview:
- Classes: UploadedFileData, DocumentStoragePort.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class UploadedFileData:
    """Detailed class documentation for `UploadedFileData`.
    
    This component belongs to `src/document_analyzer_api/domain/ports/document_storage.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    name: str
    content: bytes


class DocumentStoragePort(Protocol):
    """Detailed class documentation for `DocumentStoragePort`.
    
    This component belongs to `src/document_analyzer_api/domain/ports/document_storage.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    async def object_exists(self, name: str) -> bool:
        """Detailed asynchronous function documentation for `object_exists`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                name: Environment variable or entity name, depending on callable context.
        
            Returns:
                Value defined by `object_exists` contract and consumed by downstream callers.
        """
        ...

    async def object_hash(self, name: str) -> str:
        """Detailed asynchronous function documentation for `object_hash`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                name: Environment variable or entity name, depending on callable context.
        
            Returns:
                Value defined by `object_hash` contract and consumed by downstream callers.
        """
        ...

    async def put_object(self, name: str, content: bytes) -> None:
        """Detailed asynchronous function documentation for `put_object`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                name: Environment variable or entity name, depending on callable context.
                content: Raw payload bytes or text handled by the callable.
        
            Returns:
                Value defined by `put_object` contract and consumed by downstream callers.
        """
        ...

    async def has_done_marker(self, name: str) -> bool:
        """Detailed asynchronous function documentation for `has_done_marker`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                name: Environment variable or entity name, depending on callable context.
        
            Returns:
                Value defined by `has_done_marker` contract and consumed by downstream callers.
        """
        ...

    async def write_done_marker(self, name: str) -> None:
        """Detailed asynchronous function documentation for `write_done_marker`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                name: Environment variable or entity name, depending on callable context.
        
            Returns:
                Value defined by `write_done_marker` contract and consumed by downstream callers.
        """
        ...

