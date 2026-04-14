"""Module `src/document_analyzer_api/infrastructure/text_generation/local_text_generation_client.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: LocalTextGenerationClient.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from ...domain.ports.text_generation_client import TextGenerationClientPort


class LocalTextGenerationClient(TextGenerationClientPort):
    """LocalTextGenerationClient component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/text_generation/local_text_generation_client.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    async def generate_answer(self, question: str, context_chunks: list[str]) -> str:
        """Asynchronous execution path for `generate_answer`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/text_generation/local_text_generation_client.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Generates derived output from context, prompts, and generation options.
        
            Args:
                question: User prompt processed by retrieval and generation workflows.
                context_chunks: Input parameter accepted by `generate_answer`.
        
            Returns:
                A value compatible with `str`.
        """
        context = " ".join(context_chunks[:3])
        return f"Based on selected documents: {context}" if context else ""

