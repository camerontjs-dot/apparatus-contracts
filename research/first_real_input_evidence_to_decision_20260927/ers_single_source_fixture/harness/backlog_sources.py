"""Source-lineage recovery for ERS MainFrame backlog intake."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from harness.backlog_common import (
    canonical_identity,
    frontmatter_source_refs,
    is_within,
    parse_simple_frontmatter,
    refs_in_paragraph,
    sha256_bytes,
)


def _source_ref_id(raw_ref: str, observed_in: list[str]) -> str:
    return canonical_identity(
        {"raw_ref": raw_ref, "observed_in": sorted(observed_in)},
        "source-ref",
    )


def resolve_source_ref(
    raw_ref: str,
    *,
    reference_path: Path,
    mainframe_root: Path,
    observed_in: list[str],
    base_mode: str = "document",
) -> tuple[dict[str, Any], bytes | None]:
    ref = raw_ref.strip()
    entry: dict[str, Any] = {
        "source_ref_id": _source_ref_id(ref, observed_in),
        "raw_ref": ref,
        "observed_in": sorted(set(observed_in)),
        "semantic_status": "UNASSESSED",
    }
    if ref.lower().startswith("doi:"):
        entry.update(ref_type="doi", resolution_status="external_unfetched")
        return entry, None

    parts = urlsplit(ref)
    if parts.scheme in {"http", "https"}:
        entry.update(ref_type="external_url", resolution_status="external_unfetched")
        return entry, None
    if parts.scheme and parts.scheme != "file":
        entry.update(ref_type="unsupported_uri", resolution_status="unresolved")
        return entry, None

    local_text = unquote(
        parts.path if parts.scheme == "file" else ref.split("#", 1)[0].split("?", 1)[0]
    )
    if not local_text:
        entry.update(ref_type="anchor", resolution_status="not_a_source")
        return entry, None

    raw_path = Path(local_text).expanduser()
    if raw_path.is_absolute():
        candidate = raw_path
    elif base_mode == "mainframe_root":
        candidate = mainframe_root / raw_path
    else:
        candidate = reference_path.parent / raw_path

    root = mainframe_root.resolve(strict=True)
    resolved = candidate.resolve(strict=False)
    entry["ref_type"] = "local_path"
    if not is_within(resolved, root):
        entry["resolution_status"] = "blocked_path_escape"
        return entry, None
    entry["resolved_mainframe_path"] = resolved.relative_to(root).as_posix()
    if not resolved.exists():
        entry["resolution_status"] = "missing"
        return entry, None
    if not resolved.is_file():
        entry["resolution_status"] = "not_a_file"
        return entry, None

    final_path = resolved.resolve(strict=True)
    if not is_within(final_path, root):
        entry["resolution_status"] = "blocked_path_escape"
        entry.pop("resolved_mainframe_path", None)
        return entry, None
    data = final_path.read_bytes()
    entry.update(
        resolution_status="resolved_local",
        resolved_mainframe_path=final_path.relative_to(root).as_posix(),
        content_identity=sha256_bytes(data),
        size_bytes=len(data),
    )
    return entry, data


def collect_source_refs(
    text: str,
    parts: list[str],
    *,
    knowledge_path: Path,
    mainframe_root: Path,
) -> tuple[list[dict[str, Any]], dict[str, list[str]], list[str], dict[str, bytes]]:
    specs: list[tuple[str, list[str], str]] = []
    for raw, observed in frontmatter_source_refs(parse_simple_frontmatter(text)):
        specs.append((raw, [observed], "mainframe_root"))

    paragraph_to_pairs: dict[str, list[tuple[str, str]]] = {}
    for idx, paragraph in enumerate(parts, start=1):
        pref = f"paragraph[{idx}]"
        pairs = [(raw, "document") for raw in refs_in_paragraph(paragraph)]
        paragraph_to_pairs[pref] = pairs
        for raw, mode in pairs:
            specs.append((raw, [pref], mode))

    merged: dict[tuple[str, str], list[str]] = {}
    for raw, observed, mode in specs:
        merged.setdefault((raw, mode), []).extend(observed)

    entries: list[dict[str, Any]] = []
    source_bytes: dict[str, bytes] = {}
    key_to_id: dict[tuple[str, str], str] = {}
    frontmatter_ids: list[str] = []
    for (raw, mode), observed in sorted(merged.items()):
        obs = sorted(set(observed))
        entry, data = resolve_source_ref(
            raw,
            reference_path=knowledge_path,
            mainframe_root=mainframe_root,
            observed_in=obs,
            base_mode=mode,
        )
        entry["resolution_base"] = mode
        entries.append(entry)
        key_to_id[(raw, mode)] = entry["source_ref_id"]
        if any(value.startswith("frontmatter[") for value in obs):
            frontmatter_ids.append(entry["source_ref_id"])
        if data is not None:
            source_bytes[entry["content_identity"]] = data

    paragraph_to_ids = {
        pref: [key_to_id[pair] for pair in pairs if pair in key_to_id]
        for pref, pairs in paragraph_to_pairs.items()
    }
    return entries, paragraph_to_ids, frontmatter_ids, source_bytes


def trace_explicit_lineage(
    source_entries: list[dict[str, Any]],
    source_bytes: dict[str, bytes],
    *,
    mainframe_root: Path,
    max_depth: int = 8,
) -> list[dict[str, Any]]:
    """Follow explicit frontmatter provenance only, never arbitrary body links."""
    edges: list[dict[str, Any]] = []
    entries_by_id = {entry["source_ref_id"]: entry for entry in source_entries}

    def walk(entry: dict[str, Any], depth: int, stack: frozenset[str]) -> None:
        if depth > max_depth:
            entry["lineage_terminal_kind"] = "depth_limit"
            return
        if entry.get("resolution_status") != "resolved_local":
            entry.setdefault("lineage_terminal_kind", entry.get("resolution_status", "unresolved"))
            return
        rel = entry.get("resolved_mainframe_path")
        if not rel:
            entry["lineage_terminal_kind"] = "unresolved"
            return
        if rel in stack:
            entry["lineage_terminal_kind"] = "cycle"
            return
        next_stack = stack | {rel}
        path = mainframe_root / rel
        if path.suffix.lower() != ".md":
            entry["lineage_terminal_kind"] = "local_non_markdown_leaf"
            return

        data = source_bytes.get(entry.get("content_identity", "")) or path.read_bytes()
        source_bytes[sha256_bytes(data)] = data
        fm = parse_simple_frontmatter(data.decode("utf-8", errors="replace"))
        source_type = str(fm.get("type") or "").strip().lower()
        entry["mainframe_type"] = source_type or None
        rel_lower = rel.lower()
        raw_like_path = "__raw__" in Path(rel).name.lower() or "/raw/" in f"/{rel_lower}"
        if source_type == "raw" or raw_like_path:
            entry["lineage_terminal_kind"] = "raw_local"
            entry["raw_classification_basis"] = (
                "frontmatter[type]" if source_type == "raw" else "mainframe_raw_path_convention"
            )
            return

        children = frontmatter_source_refs(fm)
        if not children:
            entry["lineage_terminal_kind"] = "local_nonraw_leaf"
            return
        for raw, observed in children:
            child, child_data = resolve_source_ref(
                raw,
                reference_path=path,
                mainframe_root=mainframe_root,
                observed_in=[f"{rel}:{observed}"],
                base_mode="mainframe_root",
            )
            child["resolution_base"] = "mainframe_root"
            child_id = child["source_ref_id"]
            if child_id not in entries_by_id:
                entries_by_id[child_id] = child
                source_entries.append(child)
            else:
                child = entries_by_id[child_id]
            if child_data is not None:
                source_bytes[child["content_identity"]] = child_data
            edges.append(
                {
                    "parent_source_ref_id": entry["source_ref_id"],
                    "child_source_ref_id": child_id,
                    "basis": "explicit_frontmatter_provenance",
                }
            )
            walk(child, depth + 1, next_stack)

    for entry in list(source_entries):
        walk(entry, 0, frozenset())
    return edges


def terminal_descendants(
    direct_ids: list[str],
    source_entries: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> list[str]:
    children: dict[str, list[str]] = {}
    for edge in edges:
        children.setdefault(edge["parent_source_ref_id"], []).append(edge["child_source_ref_id"])
    terminals = {
        entry["source_ref_id"] for entry in source_entries if entry.get("lineage_terminal_kind")
    }
    result: list[str] = []
    stack = list(direct_ids)
    seen: set[str] = set()
    while stack:
        sid = stack.pop()
        if sid in seen:
            continue
        seen.add(sid)
        if sid in terminals or sid not in children:
            if sid not in result:
                result.append(sid)
        else:
            stack.extend(children[sid])
    return sorted(result)


def write_source_packet(
    source_dir: Path,
    source_entries: list[dict[str, Any]],
    source_bytes: dict[str, bytes],
) -> None:
    source_dir.mkdir(parents=True, exist_ok=True)
    identity_to_name: dict[str, str] = {}
    for entry in source_entries:
        identity = entry.get("content_identity")
        if not identity or identity not in source_bytes:
            continue
        digest = identity.split(":", 1)[1]
        suffix = Path(entry.get("resolved_mainframe_path", "")).suffix
        filename = f"{digest}{suffix}" if suffix else digest
        if identity not in identity_to_name:
            (source_dir / filename).write_bytes(source_bytes[identity])
            identity_to_name[identity] = filename
        entry["packet_path"] = f"sources/{identity_to_name[identity]}"
