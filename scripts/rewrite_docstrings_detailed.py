"""Rewrite repository docstrings with narrative, technical wording.

This utility updates module, class, and function docstrings across the Document
Analyzer codebase. Generated text is context-aware (layer, symbol role, behavior
hints) and avoids repetitive template phrasing.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
SELF_PATH = Path(__file__).resolve()


def iter_python_files() -> list[Path]:
    """Return all repository Python files eligible for docstring rewriting."""
    return [
        path
        for path in ROOT.rglob("*.py")
        if "/.venv/" not in str(path)
        and "__pycache__" not in str(path)
        and "/.git/" not in str(path)
        and path.resolve() != SELF_PATH
    ]


def layer_description(rel: str) -> str:
    """Map a repository-relative path to its architectural layer label."""
    if "/api/routes/" in rel:
        return "API routing"
    if "/api/schemas/" in rel:
        return "API schema"
    if rel.endswith("/api/errors.py"):
        return "API error mapping"
    if "/application/services/" in rel:
        return "application service"
    if "/domain/models/" in rel:
        return "domain model"
    if "/domain/ports/" in rel:
        return "domain abstraction"
    if "/infrastructure/" in rel:
        return "infrastructure adapter"
    if "/observability/" in rel:
        return "observability"
    if "/bootstrap/" in rel:
        return "composition/bootstrap"
    if "/tests/" in rel:
        return "test"
    if "/scripts/" in rel:
        return "tooling"
    return "project support"


def module_purpose(rel: str) -> str:
    """Return a concise module-purpose sentence based on file path semantics."""
    if rel.endswith("/main.py"):
        return "Builds the FastAPI application and wires routers, middleware, and lifecycle hooks."
    if rel.endswith("/config/settings.py"):
        return "Defines typed runtime settings loaded from environment variables and validated at startup."
    if rel.endswith("/api/errors.py"):
        return "Maps internal failures to RFC 7807 problem responses returned by the HTTP API."
    if rel.endswith("/observability/tracing.py"):
        return "Initializes trace export and exposes decorator helpers used by tracing wrappers."
    if rel.endswith("/bootstrap/container.py"):
        return "Composes runtime dependencies for both local and real adapter modes."
    if "/api/routes/" in rel:
        return "Adapts HTTP input/output contracts to application-service calls."
    if "/application/services/" in rel:
        return "Coordinates use-case workflows over domain ports and adapters."
    if "/domain/models/" in rel:
        return "Declares domain objects exchanged across business workflows."
    if "/domain/ports/" in rel:
        return "Declares protocol contracts implemented by infrastructure adapters."
    if "/infrastructure/" in rel:
        return "Implements concrete integrations for storage, retrieval, parsing, and providers."
    if "/observability/" in rel:
        return "Implements metrics, tracing, and request-level telemetry support."
    if "/tests/" in rel:
        return "Validates behavior, contracts, and regressions through automated tests."
    if "/scripts/" in rel:
        return "Automates repository maintenance and repetitive development tasks."
    return "Implements a focused responsibility in the Document Analyzer codebase."


def symbol_names(nodes: Iterable[ast.AST], node_type: type) -> list[str]:
    """Extract symbol names for one AST node type from a sequence of nodes."""
    return [node.name for node in nodes if isinstance(node, node_type)]


def build_module_doc(rel: str, tree: ast.Module) -> str:
    """Build a narrative module-level docstring for one Python module."""
    classes = symbol_names(tree.body, ast.ClassDef)
    funcs = symbol_names(tree.body, ast.FunctionDef) + symbol_names(tree.body, ast.AsyncFunctionDef)

    return (
        f'"""Module `{rel}`.\n\n'
        f'This module belongs to the {layer_description(rel)} layer of Document Analyzer.\n\n'
        f'Purpose:\n'
        f'- {module_purpose(rel)}\n\n'
        f'Defined symbols:\n'
        f'- Classes: {", ".join(classes) if classes else "none"}.\n'
        f'- Functions: {", ".join(funcs) if funcs else "none"}.\n\n'
        f'Project alignment:\n'
        f'- Functional expectations are described in `documentation/REFINED_SPECS.md`.\n'
        f'- Architectural and style conventions are defined in\n'
        f'  `documentation/REFINED_PROJECT_CONVENTIONS.md`.\n'
        f'"""'
    )


def class_role(name: str) -> str:
    """Infer a class role label from naming conventions."""
    lowered = name.lower()
    if lowered.endswith("service"):
        return "application service"
    if lowered.endswith("repository"):
        return "repository adapter"
    if lowered.endswith("provider"):
        return "provider adapter"
    if lowered.endswith("request") or lowered.endswith("response"):
        return "transport schema"
    if lowered.endswith("settings"):
        return "runtime settings model"
    if lowered.endswith("error") or lowered.endswith("exception"):
        return "error model"
    return "component"


def class_fields(node: ast.ClassDef) -> list[str]:
    """Collect annotated class field names from a class AST node."""
    fields: list[str] = []
    for item in node.body:
        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            fields.append(item.target.id)
    return fields


def build_class_doc(node: ast.ClassDef, rel: str) -> str:
    """Build a narrative class docstring for one class declaration."""
    fields = class_fields(node)
    sample_fields = ", ".join(fields[:8]) if fields else "no explicit annotated fields"
    return (
        f'"""{node.name} {class_role(node.name)}.\n\n'
        f'This class is defined in `{rel}` and encapsulates a single cohesive concern.\n'
        f'It is intended to be composed through dependency injection and exercised by\n'
        f'unit/integration tests with stable behavioral contracts.\n\n'
        f'Notable attributes: {sample_fields}.\n'
        f'"""'
    )


def describe_param(param: str, func_name: str) -> str:
    """Return a contextual parameter description for API and service idioms."""
    key = param.lstrip("*").lower()
    known = {
        "app": "FastAPI application instance used for registration or lifecycle wiring.",
        "request": "Incoming HTTP request carrying route/query/body/context data.",
        "settings": "Typed runtime configuration controlling integrations and defaults.",
        "session_id": "Server-side chat session identifier.",
        "question": "User prompt processed by retrieval and generation workflows.",
        "document_ids": "Optional subset of documents used to scope the operation.",
        "keywords": "Optional keyword list used for retrieval metadata/filtering/boosting.",
        "keywords_mode": "Keyword strategy selector (`metadata_only`, `filter`, `rank_boost`).",
        "retrieval_mode": "Retrieval backend mode (`vector`, `graph`, or `hybrid`).",
        "top_k": "Maximum number of retrieval hits retained for context assembly.",
        "min_score": "Minimum score threshold used to discard low-confidence hits.",
        "hybrid_alpha": "Fusion weight for hybrid retrieval blending.",
        "include_sources": "Flag controlling citation extraction in response payloads.",
        "compact_context": "Flag requesting immediate context compaction in chat flows.",
        "detail": "Human-readable detail text (often for problem/error payloads).",
        "details": "Optional structured metadata attached to operation or error outcomes.",
        "status": "Status value/code used for downstream branching and response mapping.",
        "error_code": "Stable machine-readable code for client-side error handling.",
        "problem_type": "Problem type identifier following RFC 7807 semantics.",
        "exc": "Exception instance being mapped, wrapped, or inspected.",
        "name": "Identifier/environment key consumed by this callable.",
        "default": "Fallback value used when primary input is absent.",
        "path": "Filesystem path handled by this callable.",
        "content": "Raw payload bytes/text processed or transformed by this callable.",
    }
    return known.get(key, f"Input parameter accepted by `{func_name}`.")


def call_names(node: ast.AST) -> list[str]:
    """Collect called function/attribute names appearing in one callable body."""
    names: list[str] = []
    for item in ast.walk(node):
        if isinstance(item, ast.Call):
            if isinstance(item.func, ast.Name):
                names.append(item.func.id)
            elif isinstance(item.func, ast.Attribute):
                names.append(item.func.attr)
    return sorted(set(names))


def function_behavior(name: str, calls: list[str]) -> str:
    """Infer a concise behavior summary for a callable from name and call hints."""
    lowered = name.lower()
    if lowered.startswith("get_"):
        return "Retrieves data from collaborators and returns a normalized representation."
    if lowered.startswith("list_"):
        return "Collects and returns a list or paginated subset of entities."
    if lowered.startswith("create_"):
        return "Creates a resource and returns identifiers or materialized result payloads."
    if lowered.startswith("delete_"):
        return "Deletes a target resource and reports outcome deterministically."
    if lowered.startswith("validate"):
        return "Validates inputs and raises explicit failures when invariants are violated."
    if lowered.startswith("parse"):
        return "Parses incoming payloads and converts them to structured internal objects."
    if lowered.startswith("generate"):
        return "Generates derived output from context, prompts, and generation options."
    if lowered.startswith("retrieve"):
        return "Executes retrieval strategy selection and returns ranked evidence chunks."
    if lowered.startswith("chat"):
        return "Runs stateful chat logic with persisted context and new user input."
    if lowered in {"main", "create_app"}:
        return "Builds and configures the runtime application entrypoint."
    if calls:
        preview = ", ".join(calls[:4])
        return f"Coordinates helper calls ({preview}) to satisfy the callable contract."
    return "Executes the callable contract for this module concern."


def return_hint(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Describe the return contract using annotations when available."""
    if node.returns is None:
        return "Return value defined by the callable contract."
    try:
        annotation = ast.unparse(node.returns)
    except Exception:
        annotation = "annotated type"
    return f"A value compatible with `{annotation}`."


def node_params(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """Extract callable parameter names excluding `self` and `cls`."""
    args = node.args
    names = [arg.arg for arg in args.posonlyargs + args.args if arg.arg not in {"self", "cls"}]
    if args.vararg:
        names.append("*" + args.vararg.arg)
    names.extend(arg.arg for arg in args.kwonlyargs)
    if args.kwarg:
        names.append("**" + args.kwarg.arg)
    return names


def build_function_doc(node: ast.FunctionDef | ast.AsyncFunctionDef, rel: str) -> str:
    """Build a narrative function docstring with behavior, args, and return contract."""
    is_async = isinstance(node, ast.AsyncFunctionDef)
    mode = "Asynchronous" if is_async else "Synchronous"
    params = node_params(node)
    calls = call_names(node)

    if params:
        args_block = "\n".join(f"        {param}: {describe_param(param, node.name)}" for param in params)
    else:
        args_block = "        None."

    return (
        f'"""{mode} execution path for `{node.name}`.\n\n'
        f'This callable is implemented in `{rel}` and contributes to module-level behavior\n'
        f'with explicit and testable execution semantics.\n\n'
        f'    Behavior:\n'
        f'        {function_behavior(node.name, calls)}\n\n'
        f'    Args:\n'
        f'{args_block}\n\n'
        f'    Returns:\n'
        f'        {return_hint(node)}\n'
        f'"""'
    )


def replace_module_doc(lines: list[str], tree: ast.Module, rel: str) -> list[str]:
    """Replace or inject a module docstring while preserving shebang/encoding headers."""
    doc = build_module_doc(rel, tree)
    rendered = [line + "\n" for line in doc.splitlines()]

    if tree.body and isinstance(tree.body[0], ast.Expr):
        value = getattr(tree.body[0], "value", None)
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            start = tree.body[0].lineno - 1
            end = tree.body[0].end_lineno
            return lines[:start] + rendered + lines[end:]

    insert_at = 0
    if lines and lines[0].startswith("#!"):
        insert_at = 1
    if len(lines) > insert_at and lines[insert_at].startswith("#") and "coding" in lines[insert_at]:
        insert_at += 1
    return lines[:insert_at] + rendered + lines[insert_at:]


def indent(line: str) -> str:
    """Return leading whitespace indentation for one source line."""
    return line[: len(line) - len(line.lstrip())]


def rewrite_symbol_docs(lines: list[str], tree: ast.Module, rel: str) -> list[str]:
    """Rewrite class/function docstrings in one module source buffer."""
    edits: list[tuple[int, int, list[str]]] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not getattr(node, "body", None):
            continue

        first_body = node.body[0]
        has_doc = (
            isinstance(first_body, ast.Expr)
            and isinstance(getattr(first_body, "value", None), ast.Constant)
            and isinstance(first_body.value.value, str)
        )

        doc = build_class_doc(node, rel) if isinstance(node, ast.ClassDef) else build_function_doc(node, rel)
        base_indent = indent(lines[node.lineno - 1]) + "    "
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

    for start, end, rendered in sorted(edits, key=lambda item: item[0], reverse=True):
        lines[start:end] = rendered

    return lines


def main() -> None:
    """Run repository-wide docstring rewrite and print how many files changed."""
    changed = 0
    for path in iter_python_files():
        original = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(original)
        except Exception:
            continue

        rel = path.relative_to(ROOT).as_posix()
        lines = original.splitlines(keepends=True)
        lines = replace_module_doc(lines, tree, rel)

        interim = "".join(lines)
        try:
            tree_after_module = ast.parse(interim)
        except Exception:
            continue

        lines = interim.splitlines(keepends=True)
        lines = rewrite_symbol_docs(lines, tree_after_module, rel)

        rewritten = "".join(lines)
        if rewritten != original:
            path.write_text(rewritten, encoding="utf-8")
            changed += 1

    print(f"changed={changed}")


if __name__ == "__main__":
    main()

