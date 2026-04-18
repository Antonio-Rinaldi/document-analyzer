"""Module `src/document_analyzer_api/observability/metrics.py`.

This module belongs to the observability layer of Document Analyzer.

Purpose:
- Implements metrics, tracing, and request-level telemetry support.

Defined symbols:
- Classes: none.
- Functions: observe_request, render_prometheus_metrics.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from __future__ import annotations

from collections import defaultdict
from functools import wraps
from threading import Lock
from time import perf_counter
from typing import Any, Awaitable, Callable, TypeVar

T = TypeVar("T")

_REQUEST_TOTAL: defaultdict[tuple[str, str, int], int] = defaultdict(int)
_REQUEST_DURATION_SUM: defaultdict[tuple[str, str], float] = defaultdict(float)
_REQUEST_DURATION_COUNT: defaultdict[tuple[str, str], int] = defaultdict(int)

_OPERATION_TOTAL: defaultdict[tuple[str, str, str], int] = defaultdict(int)
_OPERATION_DURATION_SUM: defaultdict[tuple[str, str], float] = defaultdict(float)
_OPERATION_DURATION_COUNT: defaultdict[tuple[str, str], int] = defaultdict(int)
_OPERATION_ERRORS: defaultdict[tuple[str, str, str], int] = defaultdict(int)

_LOCK = Lock()


def observe_request(method: str, path: str, status_code: int, duration_ms: float) -> None:
    """Record one HTTP request metric observation."""
    key_total = (method, path, status_code)
    key_duration = (method, path)
    with _LOCK:
        _REQUEST_TOTAL[key_total] += 1
        _REQUEST_DURATION_SUM[key_duration] += duration_ms
        _REQUEST_DURATION_COUNT[key_duration] += 1


def observe_operation(
    *,
    component: str,
    operation: str,
    duration_ms: float,
    ok: bool,
    error_type: str | None = None,
) -> None:
    """Record one component operation observation (calls, latency, errors)."""
    status = "success" if ok else "error"
    key_total = (component, operation, status)
    key_duration = (component, operation)
    with _LOCK:
        _OPERATION_TOTAL[key_total] += 1
        _OPERATION_DURATION_SUM[key_duration] += duration_ms
        _OPERATION_DURATION_COUNT[key_duration] += 1
        if not ok and error_type is not None:
            _OPERATION_ERRORS[(component, operation, error_type)] += 1


def metered_async(component: str, operation: str) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Decorator that records latency/call/error metrics for async callables."""

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            start = perf_counter()
            try:
                result = await func(*args, **kwargs)
            except Exception as exc:
                duration_ms = (perf_counter() - start) * 1000.0
                observe_operation(
                    component=component,
                    operation=operation,
                    duration_ms=duration_ms,
                    ok=False,
                    error_type=type(exc).__name__,
                )
                raise
            duration_ms = (perf_counter() - start) * 1000.0
            observe_operation(component=component, operation=operation, duration_ms=duration_ms, ok=True)
            return result

        return wrapper

    return decorator


def metered_sync(component: str, operation: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that records latency/call/error metrics for sync callables."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            start = perf_counter()
            try:
                result = func(*args, **kwargs)
            except Exception as exc:
                duration_ms = (perf_counter() - start) * 1000.0
                observe_operation(
                    component=component,
                    operation=operation,
                    duration_ms=duration_ms,
                    ok=False,
                    error_type=type(exc).__name__,
                )
                raise
            duration_ms = (perf_counter() - start) * 1000.0
            observe_operation(component=component, operation=operation, duration_ms=duration_ms, ok=True)
            return result

        return wrapper

    return decorator


def render_prometheus_metrics() -> str:
    """Render all in-memory metrics in Prometheus text exposition format."""
    lines: list[str] = [
        "# HELP http_requests_total Total HTTP requests by method, path and status code.",
        "# TYPE http_requests_total counter",
    ]

    with _LOCK:
        for (method, path, status_code), value in sorted(_REQUEST_TOTAL.items()):
            lines.append(f'http_requests_total{{method="{method}",path="{path}",status="{status_code}"}} {value}')

        lines.extend(
            [
                "# HELP http_request_duration_ms_sum Sum of request duration in milliseconds.",
                "# TYPE http_request_duration_ms_sum gauge",
            ]
        )
        for (method, path), value in sorted(_REQUEST_DURATION_SUM.items()):
            lines.append(f'http_request_duration_ms_sum{{method="{method}",path="{path}"}} {value:.3f}')

        lines.extend(
            [
                "# HELP http_request_duration_ms_count Number of observed request durations.",
                "# TYPE http_request_duration_ms_count counter",
            ]
        )
        for (method, path), value in sorted(_REQUEST_DURATION_COUNT.items()):
            lines.append(f'http_request_duration_ms_count{{method="{method}",path="{path}"}} {value}')

        lines.extend(
            [
                "# HELP operation_calls_total Total operation calls by component, operation, and status.",
                "# TYPE operation_calls_total counter",
            ]
        )
        for (component, operation, status), value in sorted(_OPERATION_TOTAL.items()):
            lines.append(
                f'operation_calls_total{{component="{component}",operation="{operation}",status="{status}"}} {value}'
            )

        lines.extend(
            [
                "# HELP operation_duration_ms_sum Sum of operation duration in milliseconds.",
                "# TYPE operation_duration_ms_sum gauge",
            ]
        )
        for (component, operation), value in sorted(_OPERATION_DURATION_SUM.items()):
            lines.append(f'operation_duration_ms_sum{{component="{component}",operation="{operation}"}} {value:.3f}')

        lines.extend(
            [
                "# HELP operation_duration_ms_count Number of operation duration observations.",
                "# TYPE operation_duration_ms_count counter",
            ]
        )
        for (component, operation), value in sorted(_OPERATION_DURATION_COUNT.items()):
            lines.append(f'operation_duration_ms_count{{component="{component}",operation="{operation}"}} {value}')

        lines.extend(
            [
                "# HELP operation_errors_total Total operation errors by component, operation and exception type.",
                "# TYPE operation_errors_total counter",
            ]
        )
        for (component, operation, error), value in sorted(_OPERATION_ERRORS.items()):
            lines.append(
                f'operation_errors_total{{component="{component}",operation="{operation}",error="{error}"}} {value}'
            )

    return "\n".join(lines) + "\n"

