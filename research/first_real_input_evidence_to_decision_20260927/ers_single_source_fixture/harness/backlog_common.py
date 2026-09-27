"""Shared helpers for ERS MainFrame backlog intake."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

FRONTMATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*(?:\n|$)", re.DOTALL)
ORIGIN_REF_RE = re.compile(r"^paragraph\[(\d+)\]$")
MD_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")
BARE_URL_RE = re.compile(r"https?://[^\s<>()\]\}]+")
WIKI_LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
ALLOWED_RELATIONS = {"explicit", "inference", "hypothesis", "quotation"}
SOURCE_FRONTMATTER_KEYS = {
    "source",
    "sources",
    "source_path",
    "source_paths",
    "source_url",
    "raw_source",
    "raw_sources",
    "url",
    "doi",
}


def sha256_bytes(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def canonical_identity(payload: Any, prefix: str) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return f"{prefix}:sha256:{hashlib.sha256(raw.encode('utf-8')).hexdigest()}"


def extract_json(value: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    text = value.strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    for pattern in (r"```json\s*(.*?)\s*```", r"```\s*(.*?)\s*```"):
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            parsed = json.loads(matches[-1])
            if isinstance(parsed, dict):
                return parsed
    raise ValueError("No JSON object found in model output")


def frontmatter_block(text: str) -> str:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return ""
    lines = match.group(0).splitlines()
    return "\n".join(lines[1:-1])


def parse_simple_frontmatter(text: str) -> dict[str, Any]:
    """Parse the scalar/list subset used by MainFrame routing metadata."""
    block = frontmatter_block(text)
    if not block:
        return {}
    result: dict[str, Any] = {}
    current_list_key: str | None = None
    for raw_line in block.splitlines():
        top = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", raw_line)
        if top:
            key = top.group(1).lower()
            value = top.group(2).strip()
            current_list_key = None
            if not value:
                result[key] = []
                current_list_key = key
            elif value.startswith("[") and value.endswith("]"):
                inner = value[1:-1].strip()
                result[key] = [
                    item.strip().strip('"').strip("'")
                    for item in inner.split(",")
                    if item.strip()
                ]
            else:
                result[key] = value.strip('"').strip("'")
            continue
        if current_list_key is not None:
            item = re.match(r"^\s*-\s*(.+?)\s*$", raw_line)
            if item:
                result[current_list_key].append(item.group(1).strip().strip('"').strip("'"))
            elif raw_line.strip():
                current_list_key = None
    return result


def paragraphs(text: str) -> list[str]:
    match = FRONTMATTER_RE.match(text)
    body = text[match.end():] if match else text
    result: list[str] = []
    for raw in re.split(r"\n\s*\n", body):
        lines = [line.rstrip() for line in raw.splitlines() if line.strip()]
        if lines:
            result.append("\n".join(lines))
    return result


def render_numbered_paragraphs(parts: list[str]) -> str:
    return "\n\n".join(
        f"[paragraph:{idx}]\n{text}" for idx, text in enumerate(parts, start=1)
    )


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def frontmatter_source_refs(frontmatter: dict[str, Any]) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    for key in sorted(SOURCE_FRONTMATTER_KEYS):
        value = frontmatter.get(key)
        values = value if isinstance(value, list) else [value]
        for item in values:
            if item is None:
                continue
            text = str(item).strip()
            if not text or text.lower() in {"none", "n/a", "unknown", "null", "[]"}:
                continue
            if key == "doi" and not text.lower().startswith("doi:"):
                text = f"doi:{text}"
            refs.append((text, f"frontmatter[{key}]"))
    return refs


def refs_in_paragraph(text: str) -> list[str]:
    refs: list[str] = []
    seen: set[str] = set()

    def add(value: str) -> None:
        value = value.strip().rstrip(".,;:")
        if value and value not in seen:
            seen.add(value)
            refs.append(value)

    for match in MD_LINK_RE.finditer(text):
        add(match.group(1))
    for match in BARE_URL_RE.finditer(text):
        add(match.group(0))
    for match in WIKI_LINK_RE.finditer(text):
        add(match.group(1))
    return refs


def validated_refs(values: Any, paragraph_count: int) -> tuple[list[str], list[str]]:
    valid: list[str] = []
    errors: list[str] = []
    if not isinstance(values, list):
        return [], ["reference field is not a list"]
    for raw in values:
        if not isinstance(raw, str):
            errors.append("non-string paragraph reference")
            continue
        match = ORIGIN_REF_RE.match(raw.strip())
        if not match:
            errors.append(f"invalid paragraph reference: {raw}")
            continue
        idx = int(match.group(1))
        if idx < 1 or idx > paragraph_count:
            errors.append(f"paragraph reference out of range: {raw}")
            continue
        normalized = f"paragraph[{idx}]"
        if normalized not in valid:
            valid.append(normalized)
    return valid, errors


def normalize_relation(value: Any) -> str:
    text = str(value or "").strip().lower()
    return text if text in ALLOWED_RELATIONS else "unknown"


def claim_id(document_identity: str, text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.strip())
    return canonical_identity(
        {"document_identity": document_identity, "claim_text": normalized},
        "claim",
    )


def relative_mainframe_path(path: Path, mainframe_root: Path) -> str:
    root = mainframe_root.resolve(strict=False)
    resolved = path.resolve(strict=True)
    if not is_within(resolved, root):
        raise ValueError(f"Path escapes MainFrame root: {path}")
    return resolved.relative_to(root).as_posix()
