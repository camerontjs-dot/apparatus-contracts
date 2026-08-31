from __future__ import annotations

import json
import math
from contextlib import contextmanager
from typing import Any, Iterator


def iterative_json_value(value: Any, error_type, path: str = "$") -> None:
    """Validate genuine finite JSON without consuming Python call-stack depth.

    Cycle semantics intentionally match the frozen RC4 reference: only a container
    encountered again while it is active is a cycle. Shared-but-acyclic aliases are
    valid.
    """
    active: set[int] = set()
    stack: list[tuple[str, Any, str]] = [("visit", value, path)]

    while stack:
        op, current, current_path = stack.pop()
        if op == "leave":
            active.remove(id(current))
            continue

        if current is None or isinstance(current, (str, bool, int)):
            continue
        if isinstance(current, float):
            if not math.isfinite(current):
                raise error_type("non_finite_number", current_path)
            continue

        if isinstance(current, list):
            marker = id(current)
            if marker in active:
                raise error_type("non_json_value", current_path, "cyclic_container")
            active.add(marker)
            stack.append(("leave", current, current_path))
            for index in range(len(current) - 1, -1, -1):
                stack.append(("visit", current[index], f"{current_path}[{index}]"))
            continue

        if isinstance(current, dict):
            marker = id(current)
            if marker in active:
                raise error_type("non_json_value", current_path, "cyclic_container")
            active.add(marker)
            stack.append(("leave", current, current_path))
            items = list(current.items())
            for key, child in reversed(items):
                if not isinstance(key, str):
                    raise error_type("non_json_object_key", current_path)
                stack.append(("visit", child, f"{current_path}.{key}"))
            continue

        raise error_type("non_json_value", current_path, type(current).__name__)


def iterative_canonical_json_bytes(value: Any, error_type) -> bytes:
    """Canonicalize finite JSON with an explicit stack.

    Primitive lexical encoding delegates to stdlib json.dumps so integer, float,
    string, escaping, and Unicode behavior match the frozen RC4 algorithm. Only
    container traversal is made iterative.
    """
    iterative_json_value(value, error_type)
    chunks: list[str] = []
    stack: list[tuple[str, Any]] = [("value", value)]

    while stack:
        op, current = stack.pop()
        if op == "raw":
            chunks.append(current)
            continue

        if current is None or isinstance(current, (str, bool, int, float)):
            chunks.append(json.dumps(current, ensure_ascii=False, allow_nan=False, separators=(",", ":")))
            continue

        if isinstance(current, list):
            if not current:
                chunks.append("[]")
                continue
            chunks.append("[")
            stack.append(("raw", "]"))
            for index in range(len(current) - 1, -1, -1):
                if index < len(current) - 1:
                    stack.append(("raw", ","))
                stack.append(("value", current[index]))
            continue

        if isinstance(current, dict):
            if not current:
                chunks.append("{}")
                continue
            chunks.append("{")
            stack.append(("raw", "}"))
            items = sorted(current.items(), key=lambda item: item[0])
            for index in range(len(items) - 1, -1, -1):
                key, child = items[index]
                if index < len(items) - 1:
                    stack.append(("raw", ","))
                stack.append(("value", child))
                stack.append(("raw", ":"))
                stack.append(("raw", json.dumps(key, ensure_ascii=False)))
            continue

        raise AssertionError(f"unreachable non-JSON value: {type(current).__name__}")

    return ("".join(chunks) + "\n").encode("utf-8")


@contextmanager
def iterative_container_patch(core_module) -> Iterator[None]:
    """Patch only recursive container traversal for the focused experiment."""
    old_json_value = core_module._json_value
    old_canonical = core_module.canonical_json_bytes
    core_module._json_value = lambda value, path="$", active=None: iterative_json_value(
        value, core_module.ContractDError, path
    )
    core_module.canonical_json_bytes = lambda value: iterative_canonical_json_bytes(
        value, core_module.ContractDError
    )
    try:
        yield
    finally:
        core_module._json_value = old_json_value
        core_module.canonical_json_bytes = old_canonical


def catch_only(call, error_type):
    """Convert recursion escape into the existing Contract-D controlled-error class."""
    try:
        return ("ok", call())
    except RecursionError as exc:
        return ("controlled", error_type("resource_recursion_limit", "$", str(exc)))
    except error_type as exc:
        return ("controlled", exc)
