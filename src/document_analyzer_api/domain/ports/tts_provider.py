"""Detailed module documentation for `src/document_analyzer_api/domain/ports/tts_provider.py`.

File role:
- Located in the domain port layer.
- Defines logic and symbols for `tts_provider.py` within Document Analyzer V1.

Purpose:
- Declares abstract contracts implemented by infrastructure adapters.

Exported symbols overview:
- Classes: TTSProviderPort.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from typing import Protocol


class TTSProviderPort(Protocol):
    """Detailed class documentation for `TTSProviderPort`.
    
    This component belongs to `src/document_analyzer_api/domain/ports/tts_provider.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def synthesize(self, text: str, audio_format: str) -> bytes:
        """Detailed synchronous function documentation for `synthesize`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/tts_provider.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                text: Input parameter for `synthesize`.
                audio_format: Input parameter for `synthesize`.
        
            Returns:
                Value defined by `synthesize` contract and consumed by downstream callers.
        """
        ...

