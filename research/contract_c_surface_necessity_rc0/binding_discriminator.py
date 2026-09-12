"""Corrected binding discriminator after the preserved RC0 evaluator deviation.

The first evaluator mutated a causal member to residual while retaining an
independent-alternatives form, accidentally creating an invalid semantic object.
This discriminator changes only the causal form between two already-supported
forms over the exact same two causal evidence members. Both objects are locally
well-formed; only immutable external object authority should distinguish them.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Callable

from validators import contract_c as released_c
from research.contract_c_surface_necessity_rc0 import consumer, vessel
from research.contract_c_surface_necessity_rc0.evaluate import _build_shapes, _fixture, _reidentity

SCHEMA = "contract-c-surface-necessity-binding-discriminator-v1"


def _succeeds(fn: Callable[[], Any]) -> bool:
    try:
        fn()
    except Exception:
        return False
    return True


def _fails(fn: Callable[[], Any]) -> bool:
    return not _succeeds(fn)


def execute(out: Path) -> dict[str, Any]:
    contract_c, contract_c_bytes, index, refs, states = _fixture()
    shapes = _build_shapes(contract_c, contract_c_bytes, refs, states)
    baseline = shapes["independent"]
    baseline_bytes = vessel.canonical_bytes(baseline)
    baseline_sha = vessel.sha256_id(baseline_bytes)

    baseline_internal = consumer.verify_internal_integrity(
        contract_c=contract_c,
        contract_c_bytes=contract_c_bytes,
        contract_b_index=index,
        vessel=baseline,
    )
    baseline_authorized = consumer.verify_authorized(
        contract_c=contract_c,
        contract_c_bytes=contract_c_bytes,
        contract_b_index=index,
        vessel=baseline,
        vessel_bytes=baseline_bytes,
        expected_vessel_sha256=baseline_sha,
    )

    coherent_substitution = deepcopy(baseline)
    coherent_substitution["evidence_causal_form"] = "jointly_sufficient"
    coherent_substitution = _reidentity(coherent_substitution)
    substituted_bytes = vessel.canonical_bytes(coherent_substitution)
    substituted_sha = vessel.sha256_id(substituted_bytes)

    internal_accepts_substitution = _succeeds(
        lambda: consumer.verify_internal_integrity(
            contract_c=contract_c,
            contract_c_bytes=contract_c_bytes,
            contract_b_index=index,
            vessel=coherent_substitution,
        )
    )
    authorized_digest_rejects_substitution = _fails(
        lambda: consumer.verify_authorized(
            contract_c=contract_c,
            contract_c_bytes=contract_c_bytes,
            contract_b_index=index,
            vessel=coherent_substitution,
            vessel_bytes=substituted_bytes,
            expected_vessel_sha256=baseline_sha,
        )
    )
    attacker_selected_new_digest_mechanically_accepts = _succeeds(
        lambda: consumer.verify_authorized(
            contract_c=contract_c,
            contract_c_bytes=contract_c_bytes,
            contract_b_index=index,
            vessel=coherent_substitution,
            vessel_bytes=substituted_bytes,
            expected_vessel_sha256=substituted_sha,
        )
    )

    baseline_reconstruction = consumer.reconstruct(
        contract_c=contract_c,
        vessel=baseline,
        contract_b_index=index,
    )
    substituted_reconstruction = consumer.reconstruct(
        contract_c=contract_c,
        vessel=coherent_substitution,
        contract_b_index=index,
    )

    checks = {
        "baseline_internal_valid": baseline_internal is True,
        "baseline_authorized_valid": baseline_authorized is True,
        "same_exact_evidence_members": baseline_reconstruction["causal"] == substituted_reconstruction["causal"],
        "semantic_form_changed": baseline_reconstruction["evidence_causal_form"] == "independent_sufficient_alternatives" and substituted_reconstruction["evidence_causal_form"] == "jointly_sufficient",
        "internal_self_consistency_accepts_coherent_substitution": internal_accepts_substitution,
        "previously_authorized_digest_rejects_coherent_substitution": authorized_digest_rejects_substitution,
        "attacker_selected_new_digest_mechanically_accepts": attacker_selected_new_digest_mechanically_accepts,
        "internal_receipt_changed": baseline["receipt_id"] != coherent_substitution["receipt_id"],
        "whole_object_digest_changed": baseline_sha != substituted_sha,
    }
    result = {
        "schema": SCHEMA,
        "checks": checks,
        "passed": all(checks.values()),
        "baseline": {
            "receipt_id": baseline["receipt_id"],
            "sha256": baseline_sha,
            "causal_form": baseline["evidence_causal_form"],
        },
        "coherent_substitution": {
            "receipt_id": coherent_substitution["receipt_id"],
            "sha256": substituted_sha,
            "causal_form": coherent_substitution["evidence_causal_form"],
        },
        "interpretation": {
            "self_consistent_receipt_is_external_authority": False,
            "digest_value_without_independent_expected_binding_is_external_authority": False,
            "independently_supplied_expected_whole_object_digest_discriminates_exact_object": True,
        },
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "BINDING_DISCRIMINATOR.json").write_bytes(released_c.canonical_bytes(result))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = execute(args.out)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
