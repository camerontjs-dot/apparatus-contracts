"""Exact single-item read-only MainFrame intake for the first CAL Pipeline real-input run.

This is a separately identified successor to backlog_intake RC0. It never scans the
knowledge tree. The operator must admit exactly one relative knowledge path and exact
document SHA-256 before the private document is read or a model is called.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any

from adapters.base import LLMAdapter
from harness.backlog_common import (
    canonical_identity,
    paragraphs,
    parse_simple_frontmatter,
    relative_mainframe_path,
    render_numbered_paragraphs,
    sha256_bytes,
)
from harness.backlog_intake import (
    PROMPT_PATH,
    _claim_record,
    _normalize_model_claims,
    _render_prompt,
)
from harness.backlog_sources import (
    collect_source_refs,
    terminal_descendants,
    trace_explicit_lineage,
    write_source_packet,
)
from harness.claim_filters import filter_claims

ALLOWLIST_SCHEMA = "ers.mainframe_single_item_allowlist.rc1"
INVENTORY_SCHEMA = "ers.mainframe_single_item_intake.rc1"


class SingleItemIntakeError(ValueError):
    """Raised before model generation when single-item admission/provenance is invalid."""


class SingleItemStopped(RuntimeError):
    """Legitimate stopped outcome that preserves the observed boundary without widening scope."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def _allowlist(path: Path) -> tuple[dict[str, str], str]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SingleItemIntakeError(f"invalid single-item allowlist: {exc}") from exc
    if not isinstance(value, dict) or set(value) != {"schema", "items"}:
        raise SingleItemIntakeError("allowlist must contain exactly schema and items")
    if value["schema"] != ALLOWLIST_SCHEMA:
        raise SingleItemIntakeError(f"allowlist schema must equal {ALLOWLIST_SCHEMA}")
    items = value["items"]
    if not isinstance(items, list):
        raise SingleItemIntakeError("allowlist.items must be an array")
    if len(items) != 1:
        rendered = []
        for item in items:
            if isinstance(item, dict):
                rendered.append(str(item.get("knowledge_path")))
        if len(rendered) != len(set(rendered)):
            raise SingleItemIntakeError("allowlist contains duplicate knowledge-path selections")
        raise SingleItemIntakeError(
            f"allowlist must contain exactly one item; observed {len(items)}"
        )
    item = items[0]
    if not isinstance(item, dict) or set(item) != {"knowledge_path", "document_identity"}:
        raise SingleItemIntakeError(
            "allowlist item must contain exactly knowledge_path and document_identity"
        )
    knowledge_path = item["knowledge_path"]
    document_identity = item["document_identity"]
    if not isinstance(knowledge_path, str) or not knowledge_path.strip():
        raise SingleItemIntakeError("knowledge_path must be a non-empty string")
    if not isinstance(document_identity, str) or not document_identity.startswith("sha256:"):
        raise SingleItemIntakeError("document_identity must be a tagged SHA-256 identity")
    return {
        "knowledge_path": knowledge_path,
        "document_identity": document_identity,
    }, sha256_bytes(raw)


def _lexical_parts(raw: str) -> tuple[str, ...]:
    if "\\" in raw:
        raise SingleItemIntakeError("knowledge_path must use forward slashes only")
    if raw.startswith("/"):
        raise SingleItemIntakeError("absolute knowledge_path is forbidden")
    segments = raw.split("/")
    if any(part in {"", ".", ".."} for part in segments):
        raise SingleItemIntakeError("knowledge_path contains empty/dot/traversal segment")
    pure = PurePosixPath(raw)
    if pure.is_absolute() or not pure.parts or pure.parts[0] != "10_knowledge":
        raise SingleItemIntakeError("knowledge_path must be lexically confined under 10_knowledge/")
    if pure.suffix.lower() != ".md":
        raise SingleItemIntakeError("knowledge_path must identify one Markdown document")
    return tuple(pure.parts)


def resolve_admitted_document(mainframe_root: Path, raw_path: str) -> tuple[Path, str]:
    """Resolve exactly one admitted path without scanning or reading knowledge documents."""
    root = Path(mainframe_root).resolve(strict=True)
    parts = _lexical_parts(raw_path)
    candidate = root.joinpath(*parts)
    try:
        resolved = candidate.resolve(strict=True)
    except FileNotFoundError as exc:
        raise SingleItemIntakeError("admitted knowledge_path does not exist") from exc
    if not resolved.is_file():
        raise SingleItemIntakeError("admitted knowledge_path is not a file")
    try:
        relative = resolved.relative_to(root)
    except ValueError as exc:
        raise SingleItemIntakeError("admitted knowledge_path resolves outside MainFrame root") from exc
    resolved_rel = relative.as_posix()
    if resolved_rel != raw_path:
        raise SingleItemIntakeError(
            "admitted lexical path does not equal resolved MainFrame path "
            "(symlink/alias/normalization is forbidden)"
        )
    if not resolved_rel.startswith("10_knowledge/"):
        raise SingleItemIntakeError("resolved knowledge_path is outside 10_knowledge/")
    return resolved, resolved_rel


def _eligible_exact_item(path: Path, text: str) -> bool:
    """Apply the frozen #4 item-eligibility rules to this item only."""
    name = path.name.lower()
    if (
        name.startswith(".")
        or name in {"agents.md", "index.md", "index.template.md"}
        or name.endswith(".template.md")
        or name.startswith("claim__")
        or name.startswith("claim-")
        or "-claim-" in name
    ):
        return False
    fm = parse_simple_frontmatter(text)
    doc_type = str(fm.get("type") or "").strip().lower()
    status = str(fm.get("status") or "").strip().lower()
    tags_value = fm.get("tags", [])
    tags = (
        [str(v).lower() for v in tags_value]
        if isinstance(tags_value, list)
        else [str(tags_value).lower()]
    )
    if doc_type == "raw" or "__raw__" in name or "/raw/" in path.as_posix().lower():
        return False
    return (
        doc_type in {"note", "hypothesis"}
        or status == "synthesized"
        or "__note__" in name
        or any("needs-audit" in tag or "needs-verification" in tag for tag in tags)
    )


def _verify_provenance_bytes(
    source_entries: list[dict[str, Any]], source_bytes: dict[str, bytes]
) -> None:
    for entry in source_entries:
        status = entry.get("resolution_status")
        if status == "blocked_path_escape":
            raise SingleItemIntakeError(
                f"explicit source provenance escapes MainFrame root: {entry.get('raw_ref')}"
            )
        if status != "resolved_local":
            continue
        identity = entry.get("content_identity")
        if not isinstance(identity, str):
            raise SingleItemIntakeError("resolved local source lacks content identity")
        data = source_bytes.get(identity)
        if data is None:
            raise SingleItemIntakeError(
                f"resolved local source bytes unavailable for recorded identity: {identity}"
            )
        if sha256_bytes(data) != identity:
            raise SingleItemIntakeError(
                f"resolved local source provenance identity mismatch: {identity}"
            )


def _terminal_raw_ids(
    source_entries: list[dict[str, Any]], lineage_edges: list[dict[str, Any]]
) -> list[str]:
    direct = [str(row["source_ref_id"]) for row in source_entries]
    terminals = terminal_descendants(direct, source_entries, lineage_edges)
    kind = {
        str(row["source_ref_id"]): row.get("lineage_terminal_kind")
        for row in source_entries
    }
    return sorted(sid for sid in terminals if kind.get(sid) == "raw_local")


def _single_document_inventory(
    *,
    knowledge_path: Path,
    knowledge_text: str,
    mainframe_root: Path,
    adapter: LLMAdapter,
    min_claim_text_length: int,
    max_claims_per_document: int,
) -> tuple[dict[str, Any], str, dict[str, bytes]]:
    """Process the already-admitted item; provenance is recovered before generation."""
    parts = paragraphs(knowledge_text)
    document_identity = sha256_bytes(knowledge_text.encode("utf-8"))
    frontmatter = parse_simple_frontmatter(knowledge_text)
    source_entries, paragraph_sources, frontmatter_ids, source_bytes = collect_source_refs(
        knowledge_text,
        parts,
        knowledge_path=knowledge_path,
        mainframe_root=mainframe_root,
    )
    lineage_edges = trace_explicit_lineage(
        source_entries,
        source_bytes,
        mainframe_root=mainframe_root,
    )
    _verify_provenance_bytes(source_entries, source_bytes)

    raw_ids = _terminal_raw_ids(source_entries, lineage_edges)
    if not raw_ids:
        statuses = sorted(
            {
                str(row.get("resolution_status") or row.get("lineage_terminal_kind") or "unknown")
                for row in source_entries
            }
        )
        raise SingleItemStopped(
            "NO_RESOLVED_RAW_PROVENANCE",
            "selected item has no explicitly resolved raw-local provenance; "
            f"observed states={statuses or ['none']}",
        )

    raw_output = adapter.generate(
        _render_prompt(parts),
        system_prompt=(
            "Reconstruct auditable proposition candidates from synthesized knowledge. "
            "The note is origin material, not evidence. Never decide source support or "
            "invent source references."
        ),
        temperature=0.0,
        json_mode=False,
    )
    from harness.backlog_common import extract_json

    raw_claims = extract_json(raw_output).get("claims", [])
    normalized = _normalize_model_claims(raw_claims)
    kept, rejected = filter_claims(
        normalized,
        min_text_length=min_claim_text_length,
        max_claims=max_claims_per_document,
    )
    claims = [
        _claim_record(
            item,
            document_identity=document_identity,
            paragraph_count=len(parts),
            paragraph_sources=paragraph_sources,
            frontmatter_source_ids=frontmatter_ids,
            source_entries=source_entries,
            lineage_edges=lineage_edges,
        )
        for item in kept
    ]

    document = {
        "knowledge_path": relative_mainframe_path(knowledge_path, mainframe_root),
        "document_identity": document_identity,
        "mainframe_type": frontmatter.get("type"),
        "mainframe_status": frontmatter.get("status"),
        "paragraph_count": len(parts),
        "claims": claims,
        "source_refs": source_entries,
        "source_lineage_edges": lineage_edges,
        "rejected_claims": rejected,
    }
    raw_text = raw_output if isinstance(raw_output, str) else json.dumps(raw_output, sort_keys=True)
    return document, raw_text, source_bytes


def run_single_item_intake(
    mainframe_root: Path,
    adapter: LLMAdapter,
    *,
    allowlist_path: Path,
    output_dir: Path,
    min_claim_text_length: int = 40,
    max_claims_per_document: int = 15,
) -> Path:
    """Run exactly one admitted knowledge item with no tree scan."""
    item, allowlist_identity = _allowlist(allowlist_path)
    root = Path(mainframe_root).resolve(strict=True)
    knowledge_path, resolved_rel = resolve_admitted_document(root, item["knowledge_path"])

    # This is the first private knowledge-document content read in this function.
    raw_bytes = knowledge_path.read_bytes()
    observed_identity = sha256_bytes(raw_bytes)
    if observed_identity != item["document_identity"]:
        raise SingleItemIntakeError(
            "admitted document identity mismatch before model generation: "
            f"expected {item['document_identity']}, observed {observed_identity}"
        )
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SingleItemIntakeError("admitted knowledge document is not UTF-8") from exc
    if not _eligible_exact_item(knowledge_path, text):
        raise SingleItemIntakeError(
            "admitted knowledge document does not satisfy frozen #4 synthesized-item eligibility"
        )

    artifact_dir = Path(output_dir)
    if artifact_dir.exists():
        raise SingleItemIntakeError(f"output directory already exists: {artifact_dir}")

    try:
        document, raw_output, source_bytes = _single_document_inventory(
            knowledge_path=knowledge_path,
            knowledge_text=text,
            mainframe_root=root,
            adapter=adapter,
            min_claim_text_length=min_claim_text_length,
            max_claims_per_document=max_claims_per_document,
        )
    except SingleItemStopped as stop:
        artifact_dir.mkdir(parents=True, exist_ok=False)
        stop_record = {
            "schema": "ers.mainframe_single_item_stop.rc1",
            "terminal_state": "STOPPED",
            "stop_code": stop.code,
            "detail": stop.detail,
            "allowlist_identity": allowlist_identity,
            "knowledge_path": resolved_rel,
            "document_identity": observed_identity,
            "model_generation_calls": 0,
            "mainframe_read_only": True,
            "writes_to_mainframe": 0,
        }
        (artifact_dir / "STOPPED.json").write_bytes(_canonical_bytes(stop_record))
        return artifact_dir

    artifact_dir.mkdir(parents=True, exist_ok=False)
    raw_dir = artifact_dir / "raw-model-output"
    raw_dir.mkdir()
    (raw_dir / "00001.txt").write_text(raw_output, encoding="utf-8")
    write_source_packet(artifact_dir / "sources", document["source_refs"], source_bytes)

    prompt_identity = sha256_bytes(PROMPT_PATH.read_bytes())
    inventory_id = canonical_identity(
        {
            "mode": "exact_single_item",
            "allowlist_identity": allowlist_identity,
            "knowledge_path": resolved_rel,
            "document_identity": observed_identity,
            "prompt_identity": prompt_identity,
            "adapter": adapter.adapter_name,
            "model": adapter.model_name,
            "claim_ids": [row["claim_id"] for row in document["claims"]],
            "source_ref_ids": [row["source_ref_id"] for row in document["source_refs"]],
        },
        "single-item-inventory",
    )
    generated = _now()
    inventory = {
        "schema": INVENTORY_SCHEMA,
        "mode": "exact_single_item",
        "inventory_id": inventory_id,
        "generated_at_utc": generated,
        "mainframe_read_only": True,
        "source_semantics": "UNASSESSED",
        "allowlist_identity": allowlist_identity,
        "knowledge_path": resolved_rel,
        "document_identity": observed_identity,
        "documents": [document],
        "failures": [],
    }
    (artifact_dir / "inventory.json").write_text(
        json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schema": "ers.mainframe_single_item_manifest.rc1",
        "inventory_id": inventory_id,
        "allowlist_identity": allowlist_identity,
        "knowledge_path": resolved_rel,
        "document_identity": observed_identity,
        "prompt_identity": prompt_identity,
        "adapter": adapter.adapter_name,
        "model": adapter.model_name,
        "knowledge_documents_admitted": 1,
        "knowledge_documents_read": 1,
        "knowledge_documents_completed": 1,
        "claims_reconstructed": len(document["claims"]),
        "resolved_local_sources": sum(
            1
            for ref in document["source_refs"]
            if ref.get("resolution_status") == "resolved_local"
        ),
        "writes_to_mainframe": 0,
    }
    (artifact_dir / "manifest.json").write_bytes(_canonical_bytes(manifest))
    sums = []
    for path in sorted(p for p in artifact_dir.rglob("*") if p.is_file()):
        if path.name == "SHA256SUMS":
            continue
        sums.append(
            f"{sha256_bytes(path.read_bytes())}  {path.relative_to(artifact_dir).as_posix()}"
        )
    (artifact_dir / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    return artifact_dir


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Exact single-item read-only MainFrame knowledge intake RC1"
    )
    parser.add_argument("--mainframe-root", required=True, type=Path)
    parser.add_argument("--allowlist", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--model", default="qwen3.5:9b")
    args = parser.parse_args()

    from adapters.ollama import OllamaAdapter

    adapter = OllamaAdapter(args.model)
    if not adapter.health_check():
        raise SystemExit("Ollama adapter is not available; no private knowledge document was read")
    print(
        run_single_item_intake(
            args.mainframe_root,
            adapter,
            allowlist_path=args.allowlist,
            output_dir=args.output_dir,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
