from __future__ import annotations

import httpx

from ...domain.ports.image_provider import ImageProviderPort


class HttpImageProvider(ImageProviderPort):
    def __init__(self, *, base_url: str, model: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    def generate_from_text(self, text: str) -> dict:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{self._base_url}/v1/images/generations",
                json={"model": self._model, "prompt": text},
            )
            response.raise_for_status()
            payload = response.json()
            data = payload.get("data", [])
            if data:
                item = data[0]
                if "b64_json" in item:
                    return {"mimeType": "image/png", "dataBase64": item["b64_json"], "promptUsed": text[:200]}
                if "url" in item:
                    return {"mimeType": "image/url", "url": item["url"], "promptUsed": text[:200]}
            return {"mimeType": "image/unknown", "promptUsed": text[:200]}

