from typing import Protocol


class TTSProviderPort(Protocol):
    def synthesize(self, text: str, audio_format: str) -> bytes:
        ...

