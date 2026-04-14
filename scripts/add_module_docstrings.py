"""Detailed module documentation for `scripts/add_module_docstrings.py`.

File role:
- Located in the project layer.
- Defines logic and symbols for `add_module_docstrings.py` within Document Analyzer V1.

Purpose:
- Supports a focused concern in the Document Analyzer codebase.

Exported symbols overview:
- Classes: none.
- Functions: _module_doc, _iter_python_files, main.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _module_doc(relative_path: str, classes: list[str], functions: list[str]) -> str:
    """Detailed synchronous function documentation for `_module_doc`.
    
    This callable is implemented in `scripts/add_module_docstrings.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            relative_path: Input parameter for `_module_doc`.
            classes: Input parameter for `_module_doc`.
            functions: Input parameter for `_module_doc`.
    
        Returns:
            Value defined by `_module_doc` contract and consumed by downstream callers.
    """
    area = "shared project support utilities"
    if "/api/" in relative_path:
        area = "HTTP API routing, schema definitions, and error mapping"
    elif "/application/" in relative_path:
        area = "application-level orchestration and use-case coordination"
    elif "/domain/" in relative_path:
        area = "domain entities, value objects, and abstract ports"
    elif "/infrastructure/" in relative_path:
        area = "infrastructure adapters for persistence and external providers"
    elif "/observability/" in relative_path:
        area = "observability and telemetry instrumentation"
    elif "/bootstrap/" in relative_path:
        area = "dependency wiring and application bootstrap"
    elif "/tests/" in relative_path:
        area = "automated tests for contract and behavior validation"

    details: list[str] = []
    if classes:
        details.append("Classes: " + ", ".join(classes) + ".")
    if functions:
        details.append("Functions: " + ", ".join(functions) + ".")
    if not details:
        details.append("This module primarily exports constants, imports, or package markers.")

    detail_text = "\n".join(details)
    return (
        f'"""Module `{relative_path}`.\n\n'
        f"Purpose:\n"
        f"- Implements {area}.\n"
        f"- Contributes to the Document Analyzer V1 architecture described in `documentation/`.\n\n"
        f"{detail_text}\n\n"
        f"Notes:\n"
        f"- This documentation is module-focused and describes responsibility boundaries.\n"
        f"- Runtime and API behavior details are specified in refined specs and plan documents.\n"
        f'"""\n\n'
    )


def _iter_python_files() -> list[Path]:
    """Detailed synchronous function documentation for `_iter_python_files`.
    
    This callable is implemented in `scripts/add_module_docstrings.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `_iter_python_files` contract and consumed by downstream callers.
    """
    return [
        path
        for path in ROOT.rglob("*.py")
        if "/.venv/" not in str(path) and "__pycache__" not in str(path) and "/.git/" not in str(path)
    ]


def main() -> None:
    """Detailed synchronous function documentation for `main`.
    
    This callable is implemented in `scripts/add_module_docstrings.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Builds and configures the runtime application entrypoint.
    
        Args:
            None.
    
        Returns:
            Value defined by `main` contract and consumed by downstream callers.
    """
    updated = 0
    for path in sorted(_iter_python_files()):
        content = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(content)
        except Exception:
            continue

        if ast.get_docstring(tree) is not None:
            continue

        classes = [node.name for node in tree.body if isinstance(node, ast.ClassDef)]
        functions = [node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        relative_path = path.relative_to(ROOT).as_posix()
        doc = _module_doc(relative_path, classes, functions)

        lines = content.splitlines(keepends=True)
        insert_at = 0
        if lines and lines[0].startswith("#!"):
            insert_at = 1
        if len(lines) > insert_at and lines[insert_at].startswith("#") and "coding" in lines[insert_at]:
            insert_at += 1

        rewritten = "".join(lines[:insert_at]) + doc + "".join(lines[insert_at:])
        path.write_text(rewritten, encoding="utf-8")
        updated += 1

    print(f"updated={updated}")


if __name__ == "__main__":
    main()

