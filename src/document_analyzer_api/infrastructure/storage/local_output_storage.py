import asyncio
from pathlib import Path


class LocalOutputStorage:
    def __init__(self, root_path: str) -> None:
        self._root = Path(root_path) / "output"

    async def write_output(self, filename: str, content: bytes, content_type: str | None = None) -> str:
        path = self._root / filename

        def _write() -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)

        await asyncio.to_thread(_write)
        return f"local://output/{filename}"

