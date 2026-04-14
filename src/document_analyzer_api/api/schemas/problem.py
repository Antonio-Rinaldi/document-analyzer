"""Module `src/document_analyzer_api/api/schemas/problem.py`.

This module belongs to the API schema layer of Document Analyzer.

Purpose:
- Implements a focused responsibility in the Document Analyzer codebase.

Defined symbols:
- Classes: ProblemDetails.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from pydantic import BaseModel, Field


class ProblemDetails(BaseModel):
    """ProblemDetails component.
    
    This class is defined in `src/document_analyzer_api/api/schemas/problem.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: type, title, status, detail, instance, errorCode, details.
    """
    type: str = Field(default="about:blank")
    title: str
    status: int
    detail: str
    instance: str | None = None
    errorCode: str
    details: dict | list | None = None

