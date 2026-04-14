"""Module `scripts/add_module_docstrings.py`.

This module belongs to the project support layer of Document Analyzer.

Purpose:
- Implements a focused responsibility in the Document Analyzer codebase.

Defined symbols:
- Classes: none.
- Functions: _module_doc, _iter_python_files, main.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _module_doc(relative_path: str, classes: list[str], functions: list[str]) -> str:
    """Synchronous execution path for `_module_doc`.
    
    This callable is implemented in `scripts/add_module_docstrings.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (append, join) to satisfy the callable contract.
    
        Args:
            relative_path: Input parameter accepted by `_module_doc`.
            classes: Input parameter accepted by `_module_doc`.
            functions: Input parameter accepted by `_module_doc`.
    
        Returns:
            A value compatible with `str`.
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
    """Synchronous execution path for `_iter_python_files`.
    
    This callable is implemented in `scripts/add_module_docstrings.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (rglob, str) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `list[Path]`.
    """
    return [
        path
        for path in ROOT.rglob("*.py")
        if "/.venv/" not in str(path) and "__pycache__" not in str(path) and "/.git/" not in str(path)
    ]


def main() -> None:
    """Synchronous execution path for `main`.
    
    This callable is implemented in `scripts/add_module_docstrings.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Builds and configures the runtime application entrypoint.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
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

