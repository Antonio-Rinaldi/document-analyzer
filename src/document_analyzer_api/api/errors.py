from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .schemas.problem import ProblemDetails


class DomainError(Exception):
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
        super().__init__(detail)
        self.status = status
        self.title = title
        self.detail = detail
        self.error_code = error_code
        self.problem_type = problem_type
        self.details = details


class ValidationProblem(DomainError):
    def __init__(self, detail: str, details: dict | list | None = None) -> None:
        super().__init__(
            status=400,
            title="Bad Request",
            detail=detail,
            error_code="VALIDATION_ERROR",
            problem_type="urn:problem:validation-error",
            details=details,
        )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
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


