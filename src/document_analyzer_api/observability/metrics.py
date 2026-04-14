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
from threading import Lock

_REQUEST_TOTAL: defaultdict[tuple[str, str, int], int] = defaultdict(int)
_REQUEST_DURATION_SUM: defaultdict[tuple[str, str], float] = defaultdict(float)
_REQUEST_DURATION_COUNT: defaultdict[tuple[str, str], int] = defaultdict(int)
_LOCK = Lock()


def observe_request(method: str, path: str, status_code: int, duration_ms: float) -> None:
    """Synchronous execution path for `observe_request`.
    
    This callable is implemented in `src/document_analyzer_api/observability/metrics.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Executes the callable contract for this module concern.
    
        Args:
            method: Input parameter accepted by `observe_request`.
            path: Filesystem path handled by this callable.
            status_code: Input parameter accepted by `observe_request`.
            duration_ms: Input parameter accepted by `observe_request`.
    
        Returns:
            A value compatible with `None`.
    """
    key_total = (method, path, status_code)
    key_duration = (method, path)
    with _LOCK:
        _REQUEST_TOTAL[key_total] += 1
        _REQUEST_DURATION_SUM[key_duration] += duration_ms
        _REQUEST_DURATION_COUNT[key_duration] += 1


def render_prometheus_metrics() -> str:
    """Synchronous execution path for `render_prometheus_metrics`.
    
    This callable is implemented in `src/document_analyzer_api/observability/metrics.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (append, extend, items, join) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `str`.
    """
    lines: list[str] = [
        "# HELP http_requests_total Total HTTP requests by method, path and status code.",
        "# TYPE http_requests_total counter",
    ]

    with _LOCK:
        for (method, path, status_code), value in sorted(_REQUEST_TOTAL.items()):
            lines.append(
                f'http_requests_total{{method="{method}",path="{path}",status="{status_code}"}} {value}'
            )

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

    return "\n".join(lines) + "\n"

