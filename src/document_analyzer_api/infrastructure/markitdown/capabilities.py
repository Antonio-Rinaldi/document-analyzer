"""Module `src/document_analyzer_api/infrastructure/markitdown/capabilities.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: none.
- Functions: discover_supported_input_extensions.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
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
    """Synchronous execution path for `discover_supported_input_extensions`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/markitdown/capabilities.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (MarkItDown, add, getattr, lower) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `tuple[str, ...]`.
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


