"""Read-only MainFrame synthesized-knowledge backlog intake for CAL Pipeline tests."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from adapters.base import LLMAdapter
from harness.backlog_common import (
    canonical_identity,
    claim_id,
    extract_json,
    is_within,
    normalize_relation,
    paragraphs,
    parse_simple_frontmatter,
    relative_mainframe_path,
    render_numbered_paragraphs,
    sha256_bytes,
    sha256_text,
    validated_refs,
)
from harness.backlog_sources import (
    collect_source_refs,
    terminal_descendants,
    trace_explicit_lineage,
    write_source_packet,
)
from harness.claim_filters import filter_claims

RUNS_DIR = Path(__file__).parent.parent / "runs" / "backlog-intake"
PROMPT_PATH = Path(__file__).parent / "prompts" / "knowledge_backlog_intake.md"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _render_prompt(parts: list[str]) -> str:
    template = PROMPT_PATH.read_text(encoding="utf-8")
    return template.replace("{{ numbered_knowledge }}", render_numbered_paragraphs(parts))


def _scan_paths(mainframe_root: Path, project_tag: str | None) -> list[Path]:
    root = mainframe_root.resolve(strict=True)
    knowledge_root = root / "10_knowledge"
    if project_tag:
        knowledge_root = knowledge_root / project_tag
    if not knowledge_root.exists():
        return []

    result: list[Path] = []
    for path in sorted(knowledge_root.rglob("*.md")):
        name = path.name.lower()
        if (
            name.startswith(".")
            or name in {"agents.md", "index.md", "index.template.md"}
            or name.endswith(".template.md")
            or name.startswith("claim__")
            or name.startswith("claim-")
            or "-claim-" in name
        ):
            continue
        resolved = path.resolve(strict=True)
        if not is_within(resolved, root):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
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
            continue
        if (
            doc_type in {"note", "hypothesis"}
            or status == "synthesized"
            or "__note__" in name
            or any("needs-audit" in tag or "needs-verification" in tag for tag in tags)
        ):
            result.append(path)
    return result


def _normalize_model_claims(raw_claims: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_claims, list):
        raise ValueError("Model output claims field is not a list")
    result: list[dict[str, Any]] = []
    for item in raw_claims:
        if not isinstance(item, dict):
            continue
        result.append(
            {
                "text": str(item.get("text") or "").strip(),
                "origin_relation": normalize_relation(item.get("origin_relation")),
                "origin_refs_raw": item.get("origin_refs", []),
                "lineage_refs_raw": item.get("lineage_refs", []),
            }
        )
    return result


def _claim_record(
    item: dict[str, Any],
    *,
    document_identity: str,
    paragraph_count: int,
    paragraph_sources: dict[str, list[str]],
    frontmatter_source_ids: list[str],
    source_entries: list[dict[str, Any]],
    lineage_edges: list[dict[str, Any]],
) -> dict[str, Any]:
    origin_refs, origin_errors = validated_refs(item.pop("origin_refs_raw", []), paragraph_count)
    lineage_refs, lineage_errors = validated_refs(item.pop("lineage_refs_raw", []), paragraph_count)

    candidate_ids: list[str] = []
    for sid in frontmatter_source_ids:
        if sid not in candidate_ids:
            candidate_ids.append(sid)
    for pref in [*origin_refs, *lineage_refs]:
        for sid in paragraph_sources.get(pref, []):
            if sid not in candidate_ids:
                candidate_ids.append(sid)

    terminal_ids = terminal_descendants(candidate_ids, source_entries, lineage_edges)
    terminal_kind = {
        entry["source_ref_id"]: entry.get("lineage_terminal_kind") for entry in source_entries
    }
    raw_ids = [sid for sid in terminal_ids if terminal_kind.get(sid) == "raw_local"]

    record: dict[str, Any] = {
        "claim_id": claim_id(document_identity, item["text"]),
        "text": item["text"],
        "origin_relation": item["origin_relation"],
        "origin_refs": origin_refs,
        "lineage_refs": lineage_refs,
        "candidate_source_ref_ids": candidate_ids,
        "terminal_source_ref_ids": terminal_ids,
        "resolved_raw_source_ref_ids": raw_ids,
        "source_semantics": "UNASSESSED",
        "lineage_status": (
            "resolved_raw_lineage"
            if raw_ids
            else "candidate_refs_recovered"
            if candidate_ids
            else "no_explicit_source_ref_recovered"
        ),
    }
    errors = [*origin_errors, *lineage_errors]
    if errors:
        record["lineage_validation_errors"] = errors
    return record


def _document_inventory(
    knowledge_path: Path,
    *,
    mainframe_root: Path,
    adapter: LLMAdapter,
    min_claim_text_length: int,
    max_claims_per_document: int,
) -> tuple[dict[str, Any], str, dict[str, bytes]]:
    text = knowledge_path.read_text(encoding="utf-8")
    parts = paragraphs(text)
    document_identity = sha256_text(text)
    frontmatter = parse_simple_frontmatter(text)
    source_entries, paragraph_sources, frontmatter_ids, source_bytes = collect_source_refs(
        text, parts, knowledge_path=knowledge_path, mainframe_root=mainframe_root
    )
    lineage_edges = trace_explicit_lineage(
        source_entries, source_bytes, mainframe_root=mainframe_root
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


def _inventory_identity(
    documents: list[dict[str, Any]],
    failures: list[dict[str, str]],
    *,
    project_tag: str | None,
    prompt_identity: str,
    adapter: LLMAdapter,
) -> str:
    payload = {
        "project_tag": project_tag,
        "prompt_identity": prompt_identity,
        "adapter": adapter.adapter_name,
        "model": adapter.model_name,
        "documents": [
            {
                "knowledge_path": doc["knowledge_path"],
                "document_identity": doc["document_identity"],
                "claim_ids": [claim["claim_id"] for claim in doc["claims"]],
                "source_ref_ids": [ref["source_ref_id"] for ref in doc["source_refs"]],
            }
            for doc in documents
        ],
        "failures": [
            {"knowledge_path": f["knowledge_path"], "error_type": f["error_type"]}
            for f in failures
        ],
    }
    return canonical_identity(payload, "backlog-inventory")


def run_backlog_intake(
    mainframe_root: Path,
    adapter: LLMAdapter,
    *,
    project_tag: str | None = None,
    output_dir: Path | None = None,
    run_id: str | None = None,
    min_claim_text_length: int = 40,
    max_claims_per_document: int = 15,
) -> Path:
    """Scan synthesized knowledge and emit a self-contained, read-only inventory."""
    root = Path(mainframe_root).resolve(strict=True)
    knowledge_paths = _scan_paths(root, project_tag)
    run_id = run_id or datetime.now(timezone.utc).strftime("run-%Y-%m-%d-%H%M%S")
    artifact_dir = Path(output_dir) if output_dir is not None else RUNS_DIR / run_id
    artifact_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = artifact_dir / "raw-model-output"
    raw_dir.mkdir(parents=True, exist_ok=True)

    documents: list[dict[str, Any]] = []
    all_source_bytes: dict[str, bytes] = {}
    failures: list[dict[str, str]] = []
    for idx, path in enumerate(knowledge_paths, start=1):
        rel = relative_mainframe_path(path, root)
        try:
            doc, raw_output, source_bytes = _document_inventory(
                path,
                mainframe_root=root,
                adapter=adapter,
                min_claim_text_length=min_claim_text_length,
                max_claims_per_document=max_claims_per_document,
            )
            documents.append(doc)
            all_source_bytes.update(source_bytes)
            (raw_dir / f"{idx:05d}.txt").write_text(raw_output, encoding="utf-8")
        except Exception as exc:
            failures.append(
                {"knowledge_path": rel, "error_type": type(exc).__name__, "error": str(exc)}
            )

    source_entries = [ref for doc in documents for ref in doc["source_refs"]]
    write_source_packet(artifact_dir / "sources", source_entries, all_source_bytes)
    prompt_identity = sha256_bytes(PROMPT_PATH.read_bytes())
    inventory_id = _inventory_identity(
        documents,
        failures,
        project_tag=project_tag,
        prompt_identity=prompt_identity,
        adapter=adapter,
    )
    generated = _now()
    inventory = {
        "schema": "ers.mainframe_backlog_intake.rc0",
        "inventory_id": inventory_id,
        "generated_at_utc": generated,
        "mainframe_read_only": True,
        "source_semantics": "UNASSESSED",
        "project_tag": project_tag,
        "documents": documents,
        "failures": failures,
    }
    (artifact_dir / "inventory.json").write_text(
        json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "run_id": run_id,
        "inventory_id": inventory_id,
        "generated_at_utc": generated,
        "prompt_identity": prompt_identity,
        "adapter": adapter.adapter_name,
        "model": adapter.model_name,
        "knowledge_documents_seen": len(knowledge_paths),
        "knowledge_documents_completed": len(documents),
        "knowledge_documents_failed": len(failures),
        "claims_reconstructed": sum(len(doc["claims"]) for doc in documents),
        "resolved_local_sources": sum(
            1 for doc in documents for ref in doc["source_refs"]
            if ref.get("resolution_status") == "resolved_local"
        ),
        "writes_to_mainframe": 0,
    }
    (artifact_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
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
    parser = argparse.ArgumentParser(description="Read-only MainFrame knowledge backlog intake")
    parser.add_argument("--mainframe-root", required=True, type=Path)
    parser.add_argument("--project-tag")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--model", default="qwen3.5:9b")
    args = parser.parse_args()
    from adapters.ollama import OllamaAdapter

    adapter = OllamaAdapter(args.model)
    if not adapter.health_check():
        raise SystemExit("Ollama adapter is not available")
    print(
        run_backlog_intake(
            args.mainframe_root,
            adapter,
            project_tag=args.project_tag,
            output_dir=args.output_dir,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
