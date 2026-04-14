"""Detailed module documentation for `src/document_analyzer_api/api/errors.py`.

File role:
- Located in the project layer.
- Defines logic and symbols for `errors.py` within Document Analyzer V1.

Purpose:
- Maps domain and validation failures into RFC 7807 Problem Details responses.

Exported symbols overview:
- Classes: DomainError, ValidationProblem.
- Functions: register_exception_handlers.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .schemas.problem import ProblemDetails


class DomainError(Exception):
    """Detailed class documentation for `DomainError`.
    
    This component belongs to `src/document_analyzer_api/api/errors.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(
        self,
        *,
        status: int,
        title: str,
        detail: str,
        error_code: str,
        problem_type: str = "urn:problem:domain-error",
        details: dict | list | None = None,
    ) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/api/errors.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                status: HTTP-like status code or status indicator for downstream handling.
                title: Short problem or object title used for structured responses.
                detail: Human-readable error detail or descriptive message payload.
                error_code: Stable machine-readable code used by clients for error branching.
                problem_type: Problem type identifier compatible with RFC 7807 semantics.
                details: Optional structured metadata attached to an operation or error response.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        super().__init__(detail)
        self.status = status
        self.title = title
        self.detail = detail
        self.error_code = error_code
        self.problem_type = problem_type
        self.details = details


class ValidationProblem(DomainError):
    """Detailed class documentation for `ValidationProblem`.
    
    This component belongs to `src/document_analyzer_api/api/errors.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, detail: str, details: dict | list | None = None) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/api/errors.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                detail: Human-readable error detail or descriptive message payload.
                details: Optional structured metadata attached to an operation or error response.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        super().__init__(
            status=400,
            title="Bad Request",
            detail=detail,
            error_code="VALIDATION_ERROR",
            problem_type="urn:problem:validation-error",
            details=details,
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Detailed synchronous function documentation for `register_exception_handlers`.
    
    This callable is implemented in `src/document_analyzer_api/api/errors.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            app: FastAPI application instance used for registration or runtime access.
    
        Returns:
            Value defined by `register_exception_handlers` contract and consumed by downstream callers.
    """

    @app.exception_handler(DomainError)
    async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
        """Detailed asynchronous function documentation for `domain_error_handler`.
        
        This callable is implemented in `src/document_analyzer_api/api/errors.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                _: Input parameter for `domain_error_handler`.
                exc: Raised exception instance being mapped or processed.
        
            Returns:
                Value defined by `domain_error_handler` contract and consumed by downstream callers.
        """
        body = ProblemDetails(
            type=exc.problem_type,
            title=exc.title,
            status=exc.status,
            detail=exc.detail,
            errorCode=exc.error_code,
            details=exc.details,
        )
        return JSONResponse(
            status_code=exc.status,
            content=body.model_dump(exclude_none=True),
            media_type="application/problem+json",
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Detailed asynchronous function documentation for `request_validation_handler`.
        
        This callable is implemented in `src/document_analyzer_api/api/errors.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                request: Incoming request object carrying path/query/body/context information.
                exc: Raised exception instance being mapped or processed.
        
            Returns:
                Value defined by `request_validation_handler` contract and consumed by downstream callers.
        """
        body = ProblemDetails(
            type="urn:problem:request-validation",
            title="Bad Request",
            status=400,
            detail="Request validation failed",
            instance=str(request.url.path),
            errorCode="REQUEST_VALIDATION_ERROR",
            details=exc.errors(),
        )
        return JSONResponse(
            status_code=400,
            content=body.model_dump(exclude_none=True),
            media_type="application/problem+json",
        )


