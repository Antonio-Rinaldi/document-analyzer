from __future__ import annotations

import httpx

from ...domain.ports.image_provider import ImageProviderPort


class OllamaImageProvider(ImageProviderPort):
    def __init__(self, *, base_url: str, model: str, fallback: ImageProviderPort | None = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._fallback = fallback

    def generate_from_text(self, text: str) -> dict:
        # Prefer Ollama OpenAI-compatible image route when available.
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self._base_url}/v1/images/generations",
                    json={"model": self._model, "prompt": text},
                )
                if response.status_code < 400:
                    payload = response.json()
                    data = payload.get("data", [])
                    if data:
                        item = data[0]
                        if "b64_json" in item:
                            return {
                                "mimeType": "image/png",
                                "dataBase64": item["b64_json"],
                                "promptUsed": text[:200],
                                "provider": "ollama",
                            }
                        if "url" in item:
                            return {
                                "mimeType": "image/url",
                                "url": item["url"],
                                "promptUsed": text[:200],
                                "provider": "ollama",
                            }
        except Exception:
            pass

        if self._fallback is not None:
            fallback_payload = self._fallback.generate_from_text(text)
            fallback_payload.setdefault("provider", "fallback")
            return fallback_payload

        return {
            "mimeType": "image/unsupported",
            "promptUsed": text[:200],
            "provider": "ollama",
            "warning": "Ollama image generation endpoint unavailable",
        }

