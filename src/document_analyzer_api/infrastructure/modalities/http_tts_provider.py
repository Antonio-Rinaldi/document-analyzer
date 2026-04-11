from __future__ import annotations

import httpx

from ...domain.ports.tts_provider import TTSProviderPort


class HttpTTSProvider(TTSProviderPort):
    def __init__(self, *, base_url: str, model: str, voice: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._voice = voice

    def synthesize(self, text: str, audio_format: str) -> bytes:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{self._base_url}/v1/audio/speech",
                json={
                    "model": self._model,
                    "voice": self._voice,
                    "input": text,
                    "format": audio_format,
                },
            )
            response.raise_for_status()
            return response.content

