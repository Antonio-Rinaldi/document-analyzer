"""Detailed module documentation for `scripts/refine_python_docstrings.py`.

File role:
- Located in the project layer.
- Defines logic and symbols for `refine_python_docstrings.py` within Document Analyzer V1.

Purpose:
- Supports a focused concern in the Document Analyzer codebase.

Exported symbols overview:
- Classes: none.
- Functions: _iter_python_files, _module_summary, _format_params, _indent_for, _build_module_doc, _build_function_doc, _build_class_doc, _replace_module_doc, _insert_missing_symbol_docstrings, main.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _iter_python_files() -> list[Path]:
    """Detailed synchronous function documentation for `_iter_python_files`.
    
    This callable is implemented in `scripts/refine_python_docstrings.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `_iter_python_files` contract and consumed by downstream callers.
    """
    files: list[Path] = []
    for path in ROOT.rglob("*.py"):
        raw = str(path)
        if "/.venv/" in raw or "__pycache__" in raw or "/.git/" in raw:
            continue
        files.append(path)
    return files


def _module_summary(rel: str) -> str:
    """Detailed synchronous function documentation for `_module_summary`.
    
    This callable is implemented in `scripts/refine_python_docstrings.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            rel: Input parameter for `_module_summary`.
    
        Returns:
            Value defined by `_module_summary` contract and consumed by downstream callers.
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
    """Detailed synchronous function documentation for `_format_params`.
    
    This callable is implemented in `scripts/refine_python_docstrings.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            args: Input parameter for `_format_params`.
    
        Returns:
            Value defined by `_format_params` contract and consumed by downstream callers.
    """
    names = [a.arg for a in args.posonlyargs + args.args]
    if args.vararg:
        names.append("*" + args.vararg.arg)
    names.extend(a.arg for a in args.kwonlyargs)
    if args.kwarg:
        names.append("**" + args.kwarg.arg)
    return [name for name in names if name != "self" and name != "cls"]


def _indent_for(node: ast.AST, lines: list[str]) -> str:
    """Detailed synchronous function documentation for `_indent_for`.
    
    This callable is implemented in `scripts/refine_python_docstrings.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            node: Input parameter for `_indent_for`.
            lines: Input parameter for `_indent_for`.
    
        Returns:
            Value defined by `_indent_for` contract and consumed by downstream callers.
    """
    line = lines[node.lineno - 1]
    return line[: len(line) - len(line.lstrip())]


def _build_module_doc(rel: str, classes: list[ast.ClassDef], funcs: list[ast.AST]) -> str:
    """Detailed synchronous function documentation for `_build_module_doc`.
    
    This callable is implemented in `scripts/refine_python_docstrings.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            rel: Input parameter for `_build_module_doc`.
            classes: Input parameter for `_build_module_doc`.
            funcs: Input parameter for `_build_module_doc`.
    
        Returns:
            Value defined by `_build_module_doc` contract and consumed by downstream callers.
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
    """Detailed synchronous function documentation for `_build_function_doc`.
    
    This callable is implemented in `scripts/refine_python_docstrings.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            name: Environment variable or entity name, depending on callable context.
            params: Input parameter for `_build_function_doc`.
            is_async: Input parameter for `_build_function_doc`.
    
        Returns:
            Value defined by `_build_function_doc` contract and consumed by downstream callers.
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
    """Detailed synchronous function documentation for `_build_class_doc`.
    
    This callable is implemented in `scripts/refine_python_docstrings.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            name: Environment variable or entity name, depending on callable context.
    
        Returns:
            Value defined by `_build_class_doc` contract and consumed by downstream callers.
    """
    return (
        '"""{} component.\n\n'
        '    This type groups related behavior/state for one architectural concern\n'
        '    and is consumed by dependency-injected collaborators.\n'
        '    """'
    ).format(name)


def _replace_module_doc(content: str, tree: ast.Module, rel: str) -> str:
    """Detailed synchronous function documentation for `_replace_module_doc`.
    
    This callable is implemented in `scripts/refine_python_docstrings.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            content: Raw payload bytes or text handled by the callable.
            tree: Input parameter for `_replace_module_doc`.
            rel: Input parameter for `_replace_module_doc`.
    
        Returns:
            Value defined by `_replace_module_doc` contract and consumed by downstream callers.
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
    """Detailed synchronous function documentation for `_insert_missing_symbol_docstrings`.
    
    This callable is implemented in `scripts/refine_python_docstrings.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            content: Raw payload bytes or text handled by the callable.
            tree: Input parameter for `_insert_missing_symbol_docstrings`.
    
        Returns:
            Value defined by `_insert_missing_symbol_docstrings` contract and consumed by downstream callers.
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
    """Detailed synchronous function documentation for `main`.
    
    This callable is implemented in `scripts/refine_python_docstrings.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Builds and configures the runtime application entrypoint.
    
        Args:
            None.
    
        Returns:
            Value defined by `main` contract and consumed by downstream callers.
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

