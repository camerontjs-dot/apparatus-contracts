#!/usr/bin/env python3
"""Consumer A for Contract B RC1 reproducibility.

This consumer deliberately reuses the pinned Evidence Bundler research consumer only
for the narrow semantic-measurement view. The full RC1 intake ledger is normalized
from the verified V1 input according to the RC1 profile. It shares no normalization
code with Consumer B.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

EXPECTED_INPUT = "sha256:a861eeafe9a360e9280e2d2c092bd2bbcdee6661c55412802be6fecbf8c7b2d7"
PROFILE = "contract-b-cal-intake-ledger-rc1"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def state(obj: dict[str, Any], key: str) -> dict[str, Any]:
    if key not in obj or obj[key] is None:
        return {"state": "unknown", "value": None}
    return {"state": "known", "value": deepcopy(obj[key])}


def norm_fact(fact: dict[str, Any]) -> dict[str, Any]:
    provenance = fact.get("provenance") or {}
    return {
        "fact_id": fact["fact_id"],
        "predicate": fact["predicate"],
        "value": deepcopy(fact.get("value")),
        "assertion_mode": fact.get("assertion_mode"),
        "provenance_passage_id": provenance.get("passage_id"),
    }


def norm_anchors(raw: Any) -> list[dict[str, Any]]:
    anchors = [] if raw is None else list(raw)
    result = [{"type": a.get("type"), "value": deepcopy(a.get("value"))} for a in anchors]
    return sorted(result, key=lambda a: (str(a["type"]), canonical_bytes(a["value"])))


def norm_source(source: dict[str, Any], *, semantic: bool = False) -> dict[str, Any]:
    out = {
        "source_id": source["source_id"],
        "title": source.get("title"),
        "source_type": source.get("source_type"),
        "content_hash": source.get("content_hash"),
        "context_facts": sorted(
            [norm_fact(dict(f)) for f in source.get("context_facts", [])],
            key=lambda f: f["fact_id"],
        ),
    }
    if not semantic:
        out["source_trust_level"] = state(source, "source_trust_level")
    return out


def norm_passage(passage: dict[str, Any]) -> dict[str, Any]:
    return {
        "passage_id": passage["passage_id"],
        "source_id": passage.get("source_id"),
        "text": passage.get("text"),
        "passage_hash": passage.get("passage_hash"),
        "anchors": norm_anchors(passage.get("anchors", [])),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--eb-root", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    v1 = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(v1, dict) or v1.get("variant") != "minimal_context":
        raise SystemExit("RC1_INTAKE_FAIL: invalid V1 root/variant")
    input_hash = digest(v1)
    if input_hash != EXPECTED_INPUT:
        raise SystemExit(f"RC1_INTAKE_FAIL: input hash {input_hash}")

    links = [dict(x) for x in v1["links"]]
    accepted_links = [x for x in links if (x.get("review") or {}).get("decision") == "accepted"]
    reviewed_links = [x for x in links if (x.get("review") or {}).get("decision") != "needs-review"]
    derived = {"candidate": len(links), "reviewed": len(reviewed_links), "admitted": len(accepted_links)}
    coverage = dict(v1["coverage"])
    stored = {
        "candidate": coverage.get("candidate_count"),
        "reviewed": coverage.get("reviewed_count"),
        "admitted": coverage.get("admitted_count"),
    }
    if stored != derived:
        raise SystemExit(f"RC1_INTAKE_FAIL: stored counts inconsistent {stored} != {derived}")

    claim = dict(v1["claim"])
    sources = sorted([dict(x) for x in v1["sources"]], key=lambda x: x["source_id"])
    passages = sorted([dict(x) for x in v1["passages"]], key=lambda x: x["passage_id"])

    ledger = {
        "profile": PROFILE,
        "input_identity": {"bundle_id": v1["bundle_id"], "input_sha256": input_hash},
        "claim": {
            "claim_id": claim["claim_id"],
            "claim_text": claim["claim_text"],
            "claim_form": state(claim, "claim_form"),
            "origin": state(claim, "origin"),
            "atomicity": state(claim, "atomicity"),
        },
        "sources": [norm_source(s) for s in sources],
        "passages": [norm_passage(x) for x in passages],
        "preparation_history": {
            "ledger_complete": True,
            "links": [
                {
                    "link_id": x["link_id"],
                    "claim_id": x["claim_id"],
                    "passage_id": x["passage_id"],
                    "nomination": deepcopy(x.get("nomination")),
                    "review": deepcopy(x.get("review")),
                }
                for x in sorted(links, key=lambda x: x["link_id"])
            ],
            "derived_counts": derived,
        },
        "aperture": {
            "search_scope": deepcopy(coverage.get("search_scope")),
            "outcome": state(coverage, "outcome"),
            "limitations": sorted(deepcopy(coverage.get("limitations", [])), key=canonical_bytes),
        },
    }

    # Existing pinned Consumer A semantics are used only for the semantic subset.
    sys.path.insert(0, str((args.eb_root / "src").resolve()))
    from evidence_bundler.experiments.contract_b_seam_probe import build_cal_measurement_view  # noqa: PLC0415

    measurement = build_cal_measurement_view(v1)
    semantic = {
        "bundle_id": measurement["bundle_id"],
        "claim_id": measurement["claim"]["claim_id"],
        "claim_text": measurement["claim"]["claim_text"],
        "admitted_sources": [norm_source(dict(s), semantic=True) for s in measurement["sources"]],
        "admitted_passages": [norm_passage(dict(x)) for x in measurement["admitted_passages"]],
    }
    semantic["admitted_sources"] = sorted(semantic["admitted_sources"], key=lambda x: x["source_id"])
    semantic["admitted_passages"] = sorted(semantic["admitted_passages"], key=lambda x: x["passage_id"])

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "consumer_a_ledger.json").write_bytes(canonical_bytes(ledger) + b"\n")
    (args.out / "consumer_a_semantic.json").write_bytes(canonical_bytes(semantic) + b"\n")
    result = {
        "consumer": "A",
        "input_sha256": input_hash,
        "ledger_sha256": digest(ledger),
        "semantic_sha256": digest(semantic),
    }
    (args.out / "consumer_a_result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
