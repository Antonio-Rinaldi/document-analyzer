import asyncio

from document_analyzer_api.infrastructure.parsing.simple_epub_parser import SimpleEpubParser


def test_simple_epub_parser_fallback_text_when_not_zip() -> None:
    parser = SimpleEpubParser()

    parsed = asyncio.run(parser.parse("book.epub", b"Paragraph one.\n\nParagraph two."))

    assert parsed.document_name == "book.epub"
    assert len(parsed.sections) == 1
    assert "Paragraph one" in parsed.sections[0].text

