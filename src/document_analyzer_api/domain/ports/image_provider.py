from typing import Protocol


class ImageProviderPort(Protocol):
    def generate_from_text(self, text: str) -> dict:
        ...

