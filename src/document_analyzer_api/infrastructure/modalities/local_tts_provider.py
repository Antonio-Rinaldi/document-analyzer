"""Module `src/document_analyzer_api/infrastructure/modalities/local_tts_provider.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: LocalTTSProvider.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import io
import math
import wave


class LocalTTSProvider:
    """LocalTTSProvider provider adapter.
    
    This class is defined in `src/document_analyzer_api/infrastructure/modalities/local_tts_provider.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def synthesize(self, text: str, audio_format: str) -> bytes:
        # Local deterministic wav generation used for development-phase modality plumbing.
        """Synchronous execution path for `synthesize`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/modalities/local_tts_provider.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (BytesIO, getvalue, int, len) to satisfy the callable contract.
        
            Args:
                text: Input parameter accepted by `synthesize`.
                audio_format: Input parameter accepted by `synthesize`.
        
            Returns:
                A value compatible with `bytes`.
        """
        sample_rate = 16000
        duration_seconds = max(1, min(6, len(text) // 80 + 1))
        frames = int(sample_rate * duration_seconds)
        frequency = 440.0
        amplitude = 12000

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            for i in range(frames):
                value = int(amplitude * math.sin(2 * math.pi * frequency * i / sample_rate))
                wav_file.writeframesraw(value.to_bytes(2, byteorder="little", signed=True))

        return buffer.getvalue()

