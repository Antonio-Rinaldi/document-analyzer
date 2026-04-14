"""Module `tests/unit/test_simple_epub_parser.py`.

This module belongs to the project support layer of Document Analyzer.

Purpose:
- Implements a focused responsibility in the Document Analyzer codebase.

Defined symbols:
- Classes: none.
- Functions: test_markitdown_document_parser_parses_plain_text, test_markitdown_document_parser_exposes_supported_extensions.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import asyncio

from document_analyzer_api.infrastructure.parsing.markitdown_document_parser import MarkItDownDocumentParser


def test_markitdown_document_parser_parses_plain_text() -> None:
    """Synchronous execution path for `test_markitdown_document_parser_parses_plain_text`.
    
    This callable is implemented in `tests/unit/test_simple_epub_parser.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (MarkItDownDocumentParser, len, parse, run) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
    """
    parser = MarkItDownDocumentParser()

    parsed = asyncio.run(parser.parse("book.txt", b"Paragraph one.\n\nParagraph two."))

    assert parsed.document_name == "book.txt"
    assert len(parsed.sections) == 1
    assert "Paragraph one" in parsed.sections[0].text


def test_markitdown_document_parser_exposes_supported_extensions() -> None:
    """Synchronous execution path for `test_markitdown_document_parser_exposes_supported_extensions`.
    
    This callable is implemented in `tests/unit/test_simple_epub_parser.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (MarkItDownDocumentParser, supported_extensions) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
    """
    parser = MarkItDownDocumentParser()
    supported = parser.supported_extensions()
    assert ".epub" in supported
    assert ".txt" in supported


