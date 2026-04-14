"""Module `src/document_analyzer_api/domain/ports/document_storage.py`.

This module belongs to the domain abstraction layer of Document Analyzer.

Purpose:
- Declares protocol contracts implemented by infrastructure adapters.

Defined symbols:
- Classes: UploadedFileData, DocumentStoragePort.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class UploadedFileData:
    """UploadedFileData component.
    
    This class is defined in `src/document_analyzer_api/domain/ports/document_storage.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: name, content.
    """
    name: str
    content: bytes


class DocumentStoragePort(Protocol):
    """DocumentStoragePort component.
    
    This class is defined in `src/document_analyzer_api/domain/ports/document_storage.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    async def object_exists(self, name: str) -> bool:
        """Asynchronous execution path for `object_exists`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                name: Identifier/environment key consumed by this callable.
        
            Returns:
                A value compatible with `bool`.
        """
        ...

    async def object_hash(self, name: str) -> str:
        """Asynchronous execution path for `object_hash`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                name: Identifier/environment key consumed by this callable.
        
            Returns:
                A value compatible with `str`.
        """
        ...

    async def put_object(self, name: str, content: bytes) -> None:
        """Asynchronous execution path for `put_object`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                name: Identifier/environment key consumed by this callable.
                content: Raw payload bytes/text processed or transformed by this callable.
        
            Returns:
                A value compatible with `None`.
        """
        ...

    async def has_done_marker(self, name: str) -> bool:
        """Asynchronous execution path for `has_done_marker`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                name: Identifier/environment key consumed by this callable.
        
            Returns:
                A value compatible with `bool`.
        """
        ...

    async def write_done_marker(self, name: str) -> None:
        """Asynchronous execution path for `write_done_marker`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                name: Identifier/environment key consumed by this callable.
        
            Returns:
                A value compatible with `None`.
        """
        ...

