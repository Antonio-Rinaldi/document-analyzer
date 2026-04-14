"""Detailed module documentation for `src/document_analyzer_api/api/schemas/problem.py`.

File role:
- Located in the API schema layer.
- Defines logic and symbols for `problem.py` within Document Analyzer V1.

Purpose:
- Supports a focused concern in the Document Analyzer codebase.

Exported symbols overview:
- Classes: ProblemDetails.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from pydantic import BaseModel, Field


class ProblemDetails(BaseModel):
    """Detailed class documentation for `ProblemDetails`.
    
    This component belongs to `src/document_analyzer_api/api/schemas/problem.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    type: str = Field(default="about:blank")
    title: str
    status: int
    detail: str
    instance: str | None = None
    errorCode: str
    details: dict | list | None = None

