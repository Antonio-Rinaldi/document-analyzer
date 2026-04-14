"""Detailed module documentation for `src/document_analyzer_api/observability/metrics.py`.

File role:
- Located in the observability layer.
- Defines logic and symbols for `metrics.py` within Document Analyzer V1.

Purpose:
- Supports a focused concern in the Document Analyzer codebase.

Exported symbols overview:
- Classes: none.
- Functions: observe_request, render_prometheus_metrics.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from __future__ import annotations

from collections import defaultdict
from threading import Lock

_REQUEST_TOTAL: defaultdict[tuple[str, str, int], int] = defaultdict(int)
_REQUEST_DURATION_SUM: defaultdict[tuple[str, str], float] = defaultdict(float)
_REQUEST_DURATION_COUNT: defaultdict[tuple[str, str], int] = defaultdict(int)
_LOCK = Lock()


def observe_request(method: str, path: str, status_code: int, duration_ms: float) -> None:
    """Detailed synchronous function documentation for `observe_request`.
    
    This callable is implemented in `src/document_analyzer_api/observability/metrics.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            method: Input parameter for `observe_request`.
            path: Filesystem path argument used by the callable.
            status_code: Input parameter for `observe_request`.
            duration_ms: Input parameter for `observe_request`.
    
        Returns:
            Value defined by `observe_request` contract and consumed by downstream callers.
    """
    key_total = (method, path, status_code)
    key_duration = (method, path)
    with _LOCK:
        _REQUEST_TOTAL[key_total] += 1
        _REQUEST_DURATION_SUM[key_duration] += duration_ms
        _REQUEST_DURATION_COUNT[key_duration] += 1


def render_prometheus_metrics() -> str:
    """Detailed synchronous function documentation for `render_prometheus_metrics`.
    
    This callable is implemented in `src/document_analyzer_api/observability/metrics.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `render_prometheus_metrics` contract and consumed by downstream callers.
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

