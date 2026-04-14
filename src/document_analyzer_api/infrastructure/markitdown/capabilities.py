"""Detailed module documentation for `src/document_analyzer_api/infrastructure/markitdown/capabilities.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `capabilities.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: none.
- Functions: discover_supported_input_extensions.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from __future__ import annotations

from markitdown import MarkItDown


# MarkItDown built-ins convert source documents into markdown/text.
SUPPORTED_OUTPUT_FORMATS: tuple[str, ...] = ("md", "markdown", "txt")

# Safe fallback if runtime discovery cannot find converter extension metadata.
DEFAULT_SUPPORTED_INPUT_EXTENSIONS: tuple[str, ...] = (
    ".txt",
    ".md",
    ".markdown",
    ".csv",
    ".html",
    ".htm",
    ".xml",
    ".rss",
    ".atom",
    ".json",
    ".pdf",
    ".docx",
    ".pptx",
    ".xlsx",
    ".xls",
    ".epub",
    ".ipynb",
    ".msg",
    ".zip",
    ".jpg",
    ".jpeg",
    ".png",
    ".wav",
    ".mp3",
    ".mp4",
    ".m4a",
)


def discover_supported_input_extensions() -> tuple[str, ...]:
    """Detailed synchronous function documentation for `discover_supported_input_extensions`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/markitdown/capabilities.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `discover_supported_input_extensions` contract and consumed by downstream callers.
    """
    discovered: set[str] = set()
    md = MarkItDown(enable_plugins=False)
    for registration in getattr(md, "_converters", []):
        converter = registration.converter
        for attr in (
            "ACCEPTED_FILE_EXTENSIONS",
            "ACCEPTED_XLSX_FILE_EXTENSIONS",
            "ACCEPTED_XLS_FILE_EXTENSIONS",
            "PRECISE_FILE_EXTENSIONS",
        ):
            values = getattr(converter, attr, None)
            if not values:
                continue
            for value in values:
                ext = str(value).strip().lower()
                if ext.startswith("."):
                    discovered.add(ext)

    # Keep discovery + conservative defaults merged for stable API validation.
    discovered.update(DEFAULT_SUPPORTED_INPUT_EXTENSIONS)

    if not discovered:
        return DEFAULT_SUPPORTED_INPUT_EXTENSIONS
    return tuple(sorted(discovered))


