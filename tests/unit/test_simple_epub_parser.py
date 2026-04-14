"""Detailed module documentation for `tests/unit/test_simple_epub_parser.py`.

File role:
- Located in the project layer.
- Defines logic and symbols for `test_simple_epub_parser.py` within Document Analyzer V1.

Purpose:
- Supports a focused concern in the Document Analyzer codebase.

Exported symbols overview:
- Classes: none.
- Functions: test_markitdown_document_parser_parses_plain_text, test_markitdown_document_parser_exposes_supported_extensions.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

import asyncio

from document_analyzer_api.infrastructure.parsing.markitdown_document_parser import MarkItDownDocumentParser


def test_markitdown_document_parser_parses_plain_text() -> None:
    """Detailed synchronous function documentation for `test_markitdown_document_parser_parses_plain_text`.
    
    This callable is implemented in `tests/unit/test_simple_epub_parser.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `test_markitdown_document_parser_parses_plain_text` contract and consumed by downstream callers.
    """
    parser = MarkItDownDocumentParser()

    parsed = asyncio.run(parser.parse("book.txt", b"Paragraph one.\n\nParagraph two."))

    assert parsed.document_name == "book.txt"
    assert len(parsed.sections) == 1
    assert "Paragraph one" in parsed.sections[0].text


def test_markitdown_document_parser_exposes_supported_extensions() -> None:
    """Detailed synchronous function documentation for `test_markitdown_document_parser_exposes_supported_extensions`.
    
    This callable is implemented in `tests/unit/test_simple_epub_parser.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `test_markitdown_document_parser_exposes_supported_extensions` contract and consumed by downstream callers.
    """
    parser = MarkItDownDocumentParser()
    supported = parser.supported_extensions()
    assert ".epub" in supported
    assert ".txt" in supported


