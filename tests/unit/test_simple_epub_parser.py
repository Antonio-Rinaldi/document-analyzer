import asyncio

from document_analyzer_api.infrastructure.parsing.markitdown_document_parser import MarkItDownDocumentParser


def test_markitdown_document_parser_parses_plain_text() -> None:
    parser = MarkItDownDocumentParser()

    parsed = asyncio.run(parser.parse("book.txt", b"Paragraph one.\n\nParagraph two."))

    assert parsed.document_name == "book.txt"
    assert len(parsed.sections) == 1
    assert "Paragraph one" in parsed.sections[0].text


def test_markitdown_document_parser_exposes_supported_extensions() -> None:
    parser = MarkItDownDocumentParser()
    supported = parser.supported_extensions()
    assert ".epub" in supported
    assert ".txt" in supported


