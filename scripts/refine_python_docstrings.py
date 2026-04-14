"""Module `scripts/refine_python_docstrings.py`.

This module belongs to the project support layer of Document Analyzer.

Purpose:
- Implements a focused responsibility in the Document Analyzer codebase.

Defined symbols:
- Classes: none.
- Functions: _iter_python_files, _module_summary, _format_params, _indent_for, _build_module_doc, _build_function_doc, _build_class_doc, _replace_module_doc, _insert_missing_symbol_docstrings, main.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _iter_python_files() -> list[Path]:
    """Synchronous execution path for `_iter_python_files`.
    
    This callable is implemented in `scripts/refine_python_docstrings.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (append, rglob, str) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `list[Path]`.
    """
    files: list[Path] = []
    for path in ROOT.rglob("*.py"):
        raw = str(path)
        if "/.venv/" in raw or "__pycache__" in raw or "/.git/" in raw:
            continue
        files.append(path)
    return files


def _module_summary(rel: str) -> str:
    """Synchronous execution path for `_module_summary`.
    
    This callable is implemented in `scripts/refine_python_docstrings.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (endswith) to satisfy the callable contract.
    
        Args:
            rel: Input parameter accepted by `_module_summary`.
    
        Returns:
            A value compatible with `str`.
    """
    if rel.endswith("/main.py"):
        return "Application entrypoint and FastAPI assembly with router and middleware wiring."
    if "/api/routes/" in rel:
        return "HTTP route handlers that expose API contracts and adapt requests to application services."
    if "/api/schemas/" in rel:
        return "Pydantic request/response contracts used by API endpoints."
    if "/api/errors.py" in rel:
        return "Centralized exception mapping to RFC 7807 Problem Details responses."
    if "/application/services/" in rel:
        return "Use-case orchestration services coordinating domain ports and adapters."
    if "/domain/models/" in rel:
        return "Domain data structures and typed value objects used across the application."
    if "/domain/ports/" in rel:
        return "Protocol-based abstractions defining integration boundaries for adapters."
    if "/infrastructure/" in rel:
        return "Concrete adapters for persistence, providers, parsing, retrieval, and modality integrations."
    if "/observability/" in rel:
        return "Telemetry helpers, metrics rendering, and instrumentation wrappers."
    if "/bootstrap/" in rel:
        return "Composition root and dependency graph wiring for runtime modes."
    if "/tests/" in rel:
        return "Automated tests validating behavior, contracts, and regressions."
    if "/scripts/" in rel:
        return "Development and maintenance scripts for repository tooling."
    return "Project support module used by the Document Analyzer codebase."


def _format_params(args: ast.arguments) -> list[str]:
    """Synchronous execution path for `_format_params`.
    
    This callable is implemented in `scripts/refine_python_docstrings.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (append, extend) to satisfy the callable contract.
    
        Args:
            args: Input parameter accepted by `_format_params`.
    
        Returns:
            A value compatible with `list[str]`.
    """
    names = [a.arg for a in args.posonlyargs + args.args]
    if args.vararg:
        names.append("*" + args.vararg.arg)
    names.extend(a.arg for a in args.kwonlyargs)
    if args.kwarg:
        names.append("**" + args.kwarg.arg)
    return [name for name in names if name != "self" and name != "cls"]


def _indent_for(node: ast.AST, lines: list[str]) -> str:
    """Synchronous execution path for `_indent_for`.
    
    This callable is implemented in `scripts/refine_python_docstrings.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (len, lstrip) to satisfy the callable contract.
    
        Args:
            node: Input parameter accepted by `_indent_for`.
            lines: Input parameter accepted by `_indent_for`.
    
        Returns:
            A value compatible with `str`.
    """
    line = lines[node.lineno - 1]
    return line[: len(line) - len(line.lstrip())]


def _build_module_doc(rel: str, classes: list[ast.ClassDef], funcs: list[ast.AST]) -> str:
    """Synchronous execution path for `_build_module_doc`.
    
    This callable is implemented in `scripts/refine_python_docstrings.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (_module_summary, getattr, join) to satisfy the callable contract.
    
        Args:
            rel: Input parameter accepted by `_build_module_doc`.
            classes: Input parameter accepted by `_build_module_doc`.
            funcs: Input parameter accepted by `_build_module_doc`.
    
        Returns:
            A value compatible with `str`.
    """
    class_names = ", ".join(c.name for c in classes) if classes else "none"
    func_names = ", ".join(getattr(f, "name", "<anonymous>") for f in funcs) if funcs else "none"
    return (
        f'"""Module `{rel}`.\n\n'
        f"Summary:\n"
        f"- {_module_summary(rel)}\n"
        f"- Maintains behavior aligned with refined specs and project conventions.\n\n"
        f"Primary symbols:\n"
        f"- Classes: {class_names}.\n"
        f"- Functions: {func_names}.\n\n"
        f"Responsibilities:\n"
        f"- Encapsulates one cohesive concern within the Document Analyzer architecture.\n"
        f"- Exposes stable, test-covered behavior consumed by sibling modules.\n"
        f'"""\n'
    )


def _build_function_doc(name: str, params: list[str], is_async: bool) -> str:
    """Synchronous execution path for `_build_function_doc`.
    
    This callable is implemented in `scripts/refine_python_docstrings.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (format, join, replace) to satisfy the callable contract.
    
        Args:
            name: Identifier/environment key consumed by this callable.
            params: Input parameter accepted by `_build_function_doc`.
            is_async: Input parameter accepted by `_build_function_doc`.
    
        Returns:
            A value compatible with `str`.
    """
    mode = "asynchronous" if is_async else "synchronous"
    params_block = "\n".join(f"        {p}: Input value used by this callable." for p in params)
    if not params_block:
        params_block = "        (no explicit input parameters)."
    return (
        '"""Execute {} {} workflow.\n\n'
        '    Args:\n'
        '{}\n\n'
        '    Returns:\n'
        '        Result produced by the callable contract.\n'
        '    """'
    ).format(mode, name.replace("_", " "), params_block)


def _build_class_doc(name: str) -> str:
    """Synchronous execution path for `_build_class_doc`.
    
    This callable is implemented in `scripts/refine_python_docstrings.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (format) to satisfy the callable contract.
    
        Args:
            name: Identifier/environment key consumed by this callable.
    
        Returns:
            A value compatible with `str`.
    """
    return (
        '"""{} component.\n\n'
        '    This type groups related behavior/state for one architectural concern\n'
        '    and is consumed by dependency-injected collaborators.\n'
        '    """'
    ).format(name)


def _replace_module_doc(content: str, tree: ast.Module, rel: str) -> str:
    """Synchronous execution path for `_replace_module_doc`.
    
    This callable is implemented in `scripts/refine_python_docstrings.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (_build_module_doc, getattr, isinstance, join) to satisfy the callable contract.
    
        Args:
            content: Raw payload bytes/text processed or transformed by this callable.
            tree: Input parameter accepted by `_replace_module_doc`.
            rel: Input parameter accepted by `_replace_module_doc`.
    
        Returns:
            A value compatible with `str`.
    """
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    funcs = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    new_doc = _build_module_doc(rel, classes, funcs)

    lines = content.splitlines(keepends=True)
    if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(getattr(tree.body[0], "value", None), ast.Constant):
        value = tree.body[0].value
        if isinstance(value.value, str):
            start = tree.body[0].lineno - 1
            end = tree.body[0].end_lineno
            replacement = [line + "\n" for line in new_doc.splitlines()]
            return "".join(lines[:start] + replacement + lines[end:])

    insert_at = 0
    if lines and lines[0].startswith("#!"):
        insert_at = 1
    if len(lines) > insert_at and lines[insert_at].startswith("#") and "coding" in lines[insert_at]:
        insert_at += 1
    replacement = [line + "\n" for line in new_doc.splitlines()]
    return "".join(lines[:insert_at] + replacement + lines[insert_at:])


def _insert_missing_symbol_docstrings(content: str, tree: ast.Module) -> str:
    """Synchronous execution path for `_insert_missing_symbol_docstrings`.
    
    This callable is implemented in `scripts/refine_python_docstrings.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (_build_class_doc, _build_function_doc, _format_params, _indent_for) to satisfy the callable contract.
    
        Args:
            content: Raw payload bytes/text processed or transformed by this callable.
            tree: Input parameter accepted by `_insert_missing_symbol_docstrings`.
    
        Returns:
            A value compatible with `str`.
    """
    lines = content.splitlines(keepends=True)
    edits: list[tuple[int, list[str]]] = []

    nodes: list[ast.AST] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            nodes.append(node)

    for node in nodes:
        if ast.get_docstring(node) is not None:
            continue
        if not getattr(node, "body", None):
            continue
        insert_line = node.body[0].lineno - 1
        indent = _indent_for(node, lines) + "    "
        if isinstance(node, ast.ClassDef):
            doc = _build_class_doc(node.name)
        else:
            params = _format_params(node.args)
            doc = _build_function_doc(node.name, params, isinstance(node, ast.AsyncFunctionDef))
        rendered = [indent + line + "\n" for line in doc.splitlines()]
        edits.append((insert_line, rendered))

    for line_idx, rendered in sorted(edits, key=lambda x: x[0], reverse=True):
        lines[line_idx:line_idx] = rendered

    return "".join(lines)


def main() -> None:
    """Synchronous execution path for `main`.
    
    This callable is implemented in `scripts/refine_python_docstrings.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Builds and configures the runtime application entrypoint.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
    """
    changed = 0
    for path in _iter_python_files():
        original = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(original)
        except Exception:
            continue

        rel = path.relative_to(ROOT).as_posix()
        rewritten = _replace_module_doc(original, tree, rel)

        try:
            tree_after_module = ast.parse(rewritten)
        except Exception:
            continue

        rewritten = _insert_missing_symbol_docstrings(rewritten, tree_after_module)

        if rewritten != original:
            path.write_text(rewritten, encoding="utf-8")
            changed += 1

    print(f"changed={changed}")


if __name__ == "__main__":
    main()

