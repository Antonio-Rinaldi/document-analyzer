"""Module `src/document_analyzer_api/infrastructure/modalities/local_image_provider.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: LocalImageProvider.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import base64


class LocalImageProvider:
    """LocalImageProvider provider adapter.
    
    This class is defined in `src/document_analyzer_api/infrastructure/modalities/local_image_provider.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def generate_from_text(self, text: str) -> dict:
        # 1x1 PNG (transparent) placeholder for local modality integration.
        """Synchronous execution path for `generate_from_text`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/modalities/local_image_provider.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Generates derived output from context, prompts, and generation options.
        
            Args:
                text: Input parameter accepted by `generate_from_text`.
        
            Returns:
                A value compatible with `dict`.
        """
        one_pixel_png = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\x9cc``\x00\x00"
            b"\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        return {
            "mimeType": "image/png",
            "dataBase64": base64.b64encode(one_pixel_png).decode("ascii"),
            "promptUsed": text[:200],
        }

