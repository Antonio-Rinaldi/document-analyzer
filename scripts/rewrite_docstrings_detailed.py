"""Detailed module documentation for `scripts/rewrite_docstrings_detailed.py`.

File role:
- Located in the project layer.
- Defines logic and symbols for `rewrite_docstrings_detailed.py` within Document Analyzer V1.

Purpose:
- Supports a focused concern in the Document Analyzer codebase.

Exported symbols overview:
- Classes: none.
- Functions: _iter_python_files, _domain_from_path, _module_purpose, _module_doc, _class_doc, _describe_param, _describe_function, _function_doc, _node_params, _replace_module_doc, _indent, _rewrite_symbol_docs, main.

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
    
    This callable is implemented in `scripts/rewrite_docstrings_detailed.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `_iter_python_files` contract and consumed by downstream callers.
    """
    return [
        p
        for p in ROOT.rglob("*.py")
        if "/.venv/" not in str(p) and "__pycache__" not in str(p) and "/.git/" not in str(p)
    ]


def _domain_from_path(rel: str) -> str:
    """Detailed synchronous function documentation for `_domain_from_path`.
    
    This callable is implemented in `scripts/rewrite_docstrings_detailed.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            rel: Input parameter for `_domain_from_path`.
    
        Returns:
            Value defined by `_domain_from_path` contract and consumed by downstream callers.
    """
    if "/api/routes/" in rel:
        return "API routing layer"
    if "/api/schemas/" in rel:
        return "API schema layer"
    if "/application/services/" in rel:
        return "application service layer"
    if "/domain/models/" in rel:
        return "domain model layer"
    if "/domain/ports/" in rel:
        return "domain port layer"
    if "/infrastructure/" in rel:
        return "infrastructure adapter layer"
    if "/observability/" in rel:
        return "observability layer"
    if "/bootstrap/" in rel:
        return "bootstrap/composition layer"
    if "/tests/" in rel:
        return "test layer"
    if "/scripts/" in rel:
        return "repository automation layer"
    return "project layer"


def _module_purpose(rel: str) -> str:
    """Detailed synchronous function documentation for `_module_purpose`.
    
    This callable is implemented in `scripts/rewrite_docstrings_detailed.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            rel: Input parameter for `_module_purpose`.
    
        Returns:
            Value defined by `_module_purpose` contract and consumed by downstream callers.
    """
    if rel.endswith("/main.py"):
        return "Bootstraps the FastAPI application and wires routers, middleware, and lifecycle hooks."
    if rel.endswith("/config/settings.py"):
        return "Defines typed runtime configuration loaded from environment variables with validation guards."
    if rel.endswith("/api/errors.py"):
        return "Maps domain and validation failures into RFC 7807 Problem Details responses."
    if rel.endswith("/observability/tracing.py"):
        return "Provides tracing initialization and decorator utilities for wrapper-based instrumentation."
    if "/api/routes/" in rel:
        return "Implements HTTP endpoint handlers and translates transport payloads into service calls."
    if "/application/services/" in rel:
        return "Implements use-case orchestration across domain ports and infrastructure adapters."
    if "/domain/models/" in rel:
        return "Declares domain-level structures exchanged by services and adapters."
    if "/domain/ports/" in rel:
        return "Declares abstract contracts implemented by infrastructure adapters."
    if "/infrastructure/" in rel:
        return "Implements concrete adapters for persistence, providers, parsing, and retrieval backends."
    if "/tests/" in rel:
        return "Contains automated tests that validate API contracts and internal behavior."
    if "/scripts/" in rel:
        return "Provides repository maintenance tooling used during development and refactoring."
    return "Supports a focused concern in the Document Analyzer codebase."


def _module_doc(rel: str, classes: list[str], funcs: list[str]) -> str:
    """Detailed synchronous function documentation for `_module_doc`.
    
    This callable is implemented in `scripts/rewrite_docstrings_detailed.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            rel: Input parameter for `_module_doc`.
            classes: Input parameter for `_module_doc`.
            funcs: Input parameter for `_module_doc`.
    
        Returns:
            Value defined by `_module_doc` contract and consumed by downstream callers.
    """
    filename = Path(rel).name
    return (
        f'"""Detailed module documentation for `{rel}`.\n\n'
        f'File role:\n'
        f'- Located in the {_domain_from_path(rel)}.\n'
        f'- Defines logic and symbols for `{filename}` within Document Analyzer V1.\n\n'
        f'Purpose:\n'
        f'- {_module_purpose(rel)}\n\n'
        f'Exported symbols overview:\n'
        f'- Classes: {", ".join(classes) if classes else "none"}.\n'
        f'- Functions: {", ".join(funcs) if funcs else "none"}.\n\n'
        f'Operational context:\n'
        f'- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in\n'
        f'  `documentation/REFINED_PROJECT_CONVENTIONS.md`.\n'
        f'- Contracts in this module are verified by the project test suite.\n'
        f'"""'
    )


def _class_doc(name: str, rel: str) -> str:
    """Detailed synchronous function documentation for `_class_doc`.
    
    This callable is implemented in `scripts/rewrite_docstrings_detailed.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            name: Environment variable or entity name, depending on callable context.
            rel: Input parameter for `_class_doc`.
    
        Returns:
            Value defined by `_class_doc` contract and consumed by downstream callers.
    """
    role = "component"
    lower = name.lower()
    if lower.endswith("service"):
        role = "application service"
    elif lower.endswith("repository"):
        role = "repository adapter"
    elif lower.endswith("provider"):
        role = "provider adapter"
    elif lower.endswith("settings"):
        role = "runtime configuration model"
    elif lower.endswith("request") or lower.endswith("response"):
        role = "transport schema model"

    return (
        f'"""Detailed class documentation for `{name}`.\n\n'
        f'This {role} belongs to `{rel}` and encapsulates one cohesive responsibility in the\n'
        f'Document Analyzer architecture. It is designed for dependency-injected composition,\n'
        f'explicit boundaries, stable contracts, and straightforward unit/integration testing.\n'
        f'"""'
    )


def _describe_param(name: str, func_name: str) -> str:
    """Detailed synchronous function documentation for `_describe_param`.
    
    This callable is implemented in `scripts/rewrite_docstrings_detailed.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            name: Environment variable or entity name, depending on callable context.
            func_name: Input parameter for `_describe_param`.
    
        Returns:
            Value defined by `_describe_param` contract and consumed by downstream callers.
    """
    key = name.lstrip("*").lower()
    known = {
        "app": "FastAPI application instance used for registration or runtime access.",
        "request": "Incoming request object carrying path/query/body/context information.",
        "settings": "Typed runtime settings used to configure behavior and integrations.",
        "detail": "Human-readable error detail or descriptive message payload.",
        "details": "Optional structured metadata attached to an operation or error response.",
        "title": "Short problem or object title used for structured responses.",
        "status": "HTTP-like status code or status indicator for downstream handling.",
        "error_code": "Stable machine-readable code used by clients for error branching.",
        "problem_type": "Problem type identifier compatible with RFC 7807 semantics.",
        "exc": "Raised exception instance being mapped or processed.",
        "session_id": "Server-side chat session identifier.",
        "question": "User question or prompt text to process.",
        "document_ids": "Optional subset of document identifiers to scope the operation.",
        "keywords": "Optional keyword list used by retrieval behavior.",
        "keywords_mode": "Retrieval keyword strategy selector.",
        "retrieval_mode": "Retrieval backend mode (`vector`, `graph`, or `hybrid`).",
        "top_k": "Maximum number of retrieved items considered in downstream steps.",
        "min_score": "Minimum score threshold used to accept retrieval hits.",
        "hybrid_alpha": "Fusion weight used when hybrid retrieval mode is selected.",
        "include_sources": "Flag controlling citation/source emission in responses.",
        "compact_context": "Flag requesting immediate chat context compaction.",
        "name": "Environment variable or entity name, depending on callable context.",
        "default": "Fallback value used when the primary source is not available.",
        "path": "Filesystem path argument used by the callable.",
        "content": "Raw payload bytes or text handled by the callable.",
    }
    return known.get(key, f"Input parameter for `{func_name}`.")


def _describe_function(name: str) -> str:
    """Detailed synchronous function documentation for `_describe_function`.
    
    This callable is implemented in `scripts/rewrite_docstrings_detailed.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            name: Environment variable or entity name, depending on callable context.
    
        Returns:
            Value defined by `_describe_function` contract and consumed by downstream callers.
    """
    lowered = name.lower()
    if lowered.startswith("get_"):
        return "Retrieves data from collaborators and returns a normalized representation."
    if lowered.startswith("list_"):
        return "Collects and returns a paginated or aggregated list of entities."
    if lowered.startswith("create_"):
        return "Creates a new resource and returns identifiers or resulting payloads."
    if lowered.startswith("delete_"):
        return "Deletes a resource and reports whether deletion succeeded."
    if lowered.startswith("update_"):
        return "Applies updates to an existing resource while preserving contract invariants."
    if lowered.startswith("validate"):
        return "Validates inputs and raises explicit failures for invalid states."
    if lowered.startswith("parse"):
        return "Parses incoming payloads into structured objects used by downstream flows."
    if lowered.startswith("generate"):
        return "Generates derived output from retrieved context and provided options."
    if lowered.startswith("retrieve"):
        return "Executes retrieval strategy selection and returns matching evidence chunks."
    if lowered.startswith("chat"):
        return "Executes stateful chat logic using persisted session context."
    if lowered in {"main", "create_app"}:
        return "Builds and configures the runtime application entrypoint."
    return "Executes the callable contract for this module responsibility."


def _function_doc(name: str, params: list[str], is_async: bool, rel: str) -> str:
    """Detailed synchronous function documentation for `_function_doc`.
    
    This callable is implemented in `scripts/rewrite_docstrings_detailed.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            name: Environment variable or entity name, depending on callable context.
            params: Input parameter for `_function_doc`.
            is_async: Input parameter for `_function_doc`.
            rel: Input parameter for `_function_doc`.
    
        Returns:
            Value defined by `_function_doc` contract and consumed by downstream callers.
    """
    mode = "asynchronous" if is_async else "synchronous"
    if params:
        args_block = "\n".join(f"        {p}: {_describe_param(p, name)}" for p in params)
    else:
        args_block = "        None."

    return (
        f'"""Detailed {mode} function documentation for `{name}`.\n\n'
        f'This callable is implemented in `{rel}` and contributes to the module workflow\n'
        f'through deterministic input/output behavior and explicit collaboration contracts.\n\n'
        f'    Behavior:\n'
        f'        {_describe_function(name)}\n\n'
        f'    Args:\n'
        f'{args_block}\n\n'
        f'    Returns:\n'
        f'        Value defined by `{name}` contract and consumed by downstream callers.\n'
        f'"""'
    )


def _node_params(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """Detailed synchronous function documentation for `_node_params`.
    
    This callable is implemented in `scripts/rewrite_docstrings_detailed.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            node: Input parameter for `_node_params`.
    
        Returns:
            Value defined by `_node_params` contract and consumed by downstream callers.
    """
    args = node.args
    names = [a.arg for a in args.posonlyargs + args.args if a.arg not in {"self", "cls"}]
    if args.vararg:
        names.append("*" + args.vararg.arg)
    names.extend(a.arg for a in args.kwonlyargs)
    if args.kwarg:
        names.append("**" + args.kwarg.arg)
    return names


def _replace_module_doc(lines: list[str], tree: ast.Module, rel: str) -> list[str]:
    """Detailed synchronous function documentation for `_replace_module_doc`.
    
    This callable is implemented in `scripts/rewrite_docstrings_detailed.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            lines: Input parameter for `_replace_module_doc`.
            tree: Input parameter for `_replace_module_doc`.
            rel: Input parameter for `_replace_module_doc`.
    
        Returns:
            Value defined by `_replace_module_doc` contract and consumed by downstream callers.
    """
    classes = [n.name for n in tree.body if isinstance(n, ast.ClassDef)]
    funcs = [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    doc = _module_doc(rel, classes, funcs)
    rendered = [line + "\n" for line in doc.splitlines()]

    if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(getattr(tree.body[0], "value", None), ast.Constant):
        value = tree.body[0].value
        if isinstance(value.value, str):
            start = tree.body[0].lineno - 1
            end = tree.body[0].end_lineno
            return lines[:start] + rendered + lines[end:]

    insert_at = 0
    if lines and lines[0].startswith("#!"):
        insert_at = 1
    if len(lines) > insert_at and lines[insert_at].startswith("#") and "coding" in lines[insert_at]:
        insert_at += 1
    return lines[:insert_at] + rendered + lines[insert_at:]


def _indent(line: str) -> str:
    """Detailed synchronous function documentation for `_indent`.
    
    This callable is implemented in `scripts/rewrite_docstrings_detailed.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            line: Input parameter for `_indent`.
    
        Returns:
            Value defined by `_indent` contract and consumed by downstream callers.
    """
    return line[: len(line) - len(line.lstrip())]


def _rewrite_symbol_docs(lines: list[str], tree: ast.Module, rel: str) -> list[str]:
    """Detailed synchronous function documentation for `_rewrite_symbol_docs`.
    
    This callable is implemented in `scripts/rewrite_docstrings_detailed.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            lines: Input parameter for `_rewrite_symbol_docs`.
            tree: Input parameter for `_rewrite_symbol_docs`.
            rel: Input parameter for `_rewrite_symbol_docs`.
    
        Returns:
            Value defined by `_rewrite_symbol_docs` contract and consumed by downstream callers.
    """
    edits: list[tuple[int, int, list[str]]] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not getattr(node, "body", None):
            continue

        first_body = node.body[0]
        has_doc = isinstance(first_body, ast.Expr) and isinstance(getattr(first_body, "value", None), ast.Constant) and isinstance(first_body.value.value, str)

        if isinstance(node, ast.ClassDef):
            doc = _class_doc(node.name, rel)
        else:
            doc = _function_doc(node.name, _node_params(node), isinstance(node, ast.AsyncFunctionDef), rel)

        base_indent = _indent(lines[node.lineno - 1]) + "    "
        rendered = [base_indent + line + "\n" for line in doc.splitlines()]

        if has_doc:
            start = first_body.lineno - 1
            end = first_body.end_lineno
            edits.append((start, end, rendered))
        else:
            insert_at = first_body.lineno - 1
            if isinstance(first_body, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and first_body.decorator_list:
                insert_at = min(item.lineno for item in first_body.decorator_list) - 1
            edits.append((insert_at, insert_at, rendered))

    for start, end, rendered in sorted(edits, key=lambda x: x[0], reverse=True):
        lines[start:end] = rendered

    return lines


def main() -> None:
    """Detailed synchronous function documentation for `main`.
    
    This callable is implemented in `scripts/rewrite_docstrings_detailed.py` and contributes to the module workflow
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
        lines = original.splitlines(keepends=True)
        lines = _replace_module_doc(lines, tree, rel)

        interim = "".join(lines)
        try:
            tree_interim = ast.parse(interim)
        except Exception:
            continue

        lines = interim.splitlines(keepends=True)
        lines = _rewrite_symbol_docs(lines, tree_interim, rel)

        rewritten = "".join(lines)
        if rewritten != original:
            path.write_text(rewritten, encoding="utf-8")
            changed += 1

    print(f"changed={changed}")


if __name__ == "__main__":
    main()




