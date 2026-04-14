"""Module `src/document_analyzer_api/domain/ports/tts_provider.py`.

This module belongs to the domain abstraction layer of Document Analyzer.

Purpose:
- Declares protocol contracts implemented by infrastructure adapters.

Defined symbols:
- Classes: TTSProviderPort.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from typing import Protocol


class TTSProviderPort(Protocol):
    """TTSProviderPort component.
    
    This class is defined in `src/document_analyzer_api/domain/ports/tts_provider.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def synthesize(self, text: str, audio_format: str) -> bytes:
        """Synchronous execution path for `synthesize`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/tts_provider.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                text: Input parameter accepted by `synthesize`.
                audio_format: Input parameter accepted by `synthesize`.
        
            Returns:
                A value compatible with `bytes`.
        """
        ...

