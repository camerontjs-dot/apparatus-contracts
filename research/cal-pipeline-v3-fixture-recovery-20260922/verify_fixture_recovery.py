from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

CASES = ("PIPE01", "PIPE02", "PIPE03")
REQUIRED = (
    "cal/contract-c.json",
    "consumer-inputs.json",
    "decision-target.json",
    "contract-d.json",
)

EXPECTED = {
    "PIPE01": {
        "cal/contract-c.json": "sha256:ba02ec570b0048832a2fc9f6b958f426b11e5dc0fe73cf1e12ae515d38ea23a0",
        "contract-d.json": "sha256:509862ec4b28ba211406eb21d9398f1fab7e153e0c7e12595d6ab8476d053e24",
    },
    "PIPE02": {
        "cal/contract-c.json": "sha256:60328dc4413a436b4559a975a60fe35e67e3e1253289ad7c63bca512af41374d",
        "contract-d.json": "sha256:8c7b28718691d6a84ecda4172051172e1c9ecf1d106cbc7e4a9132fda5ff9230",
    },
    "PIPE03": {
        "cal/contract-c.json": "sha256:f152754526aa7ea3b47401e9ae956786c73ae6795a53bfabc2a163474bc7f526",
        "contract-d.json": "sha256:12d9619bb4afc449ab5d8b01089940a9917ec28670fd4ed5e6602dd283abe55e",
    },
}

HISTORICAL_RESULT = "sha256:2ef133c504cd33bf5b9912acb06e154b43d7060b967dd4230081d4a8ad4f9753"


def digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def require_file(root: Path, case: str, rel: str) -> Path:
    path = root / case / rel
    if not path.is_file():
        raise RuntimeError(f"missing_required_fixture:{case}:{rel}:{path}")
    return path


def historical_candidates(root: Path, case: str, rel: str) -> list[Path]:
    suffix = Path(case) / rel
    return sorted(
        p for p in root.rglob(Path(rel).name)
        if p.is_file() and tuple(p.parts[-len(suffix.parts):]) == suffix.parts
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-a", required=True, type=Path)
    parser.add_argument("--run-b", required=True, type=Path)
    parser.add_argument("--result-a", required=True, type=Path)
    parser.add_argument("--result-b", required=True, type=Path)
    parser.add_argument("--historical-artifact", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    run_a = args.run_a.resolve()
    run_b = args.run_b.resolve()
    result_a = args.result_a.resolve()
    result_b = args.result_b.resolve()
    out = args.out.resolve()

    raw_result_a = result_a.read_bytes()
    raw_result_b = result_b.read_bytes()
    if raw_result_a != raw_result_b:
        raise RuntimeError("composition_result_not_byte_identical")
    if digest(raw_result_a) != HISTORICAL_RESULT:
        raise RuntimeError(
            f"historical_composition_result_mismatch:{digest(raw_result_a)}"
        )

    artifact_root = (
        args.historical_artifact.resolve()
        if args.historical_artifact is not None
        else None
    )

    if out.exists():
        raise RuntimeError(f"output_exists:{out}")
    out.mkdir(parents=True)

    manifest: dict[str, Any] = {
        "schema": "cal-pipeline-v3-complete-fixture-recovery/1",
        "classification": "research-infrastructure",
        "generator": {
            "repository": "camerontjs-dot/apparatus-contracts",
            "commit": "e68e5ab387e9779b0be62d92766b76e475964790",
            "path": "research/cal_pipeline_production_composition_rc0_20260920/run_composition.py",
        },
        "historical_run": {
            "run_id": 35479370533,
            "artifact_id": 10594929710,
            "artifact_digest": "sha256:bab1e7522a69e404208d9e65d9edae89d860827ef08fd3da1ad01813554b0841",
            "composition_result_sha256": HISTORICAL_RESULT,
        },
        "reproduction": {
            "two_fresh_roots": True,
            "composition_results_byte_identical": True,
            "composition_result_matches_historical_digest": True,
            "all_required_fixture_files_byte_identical_between_runs": True,
        },
        "cases": {},
        "nonclaim": (
            "A twice-reconstructed file is not labeled an original historical byte "
            "unless a surviving historical artifact copy was directly compared."
        ),
    }

    for case in CASES:
        case_out: dict[str, Any] = {}
        for rel in REQUIRED:
            a = require_file(run_a, case, rel)
            b = require_file(run_b, case, rel)
            raw_a = a.read_bytes()
            raw_b = b.read_bytes()
            if raw_a != raw_b:
                raise RuntimeError(f"fixture_reproduction_mismatch:{case}:{rel}")

            actual = digest(raw_a)
            expected = EXPECTED.get(case, {}).get(rel)
            if expected is not None and actual != expected:
                raise RuntimeError(
                    f"historical_identity_mismatch:{case}:{rel}:expected={expected}:actual={actual}"
                )

            historical_status = "no_preserved_historical_reference"
            historical_path = None
            if artifact_root is not None:
                candidates = historical_candidates(artifact_root, case, rel)
                if len(candidates) > 1:
                    raise RuntimeError(
                        f"ambiguous_historical_artifact_path:{case}:{rel}:{candidates}"
                    )
                if len(candidates) == 1:
                    historical_path = candidates[0]
                    historical_raw = historical_path.read_bytes()
                    if historical_raw != raw_a:
                        raise RuntimeError(
                            f"historical_artifact_byte_mismatch:{case}:{rel}"
                        )
                    historical_status = "byte_matched_to_surviving_pr123_artifact"

            destination = out / case / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(raw_a)
            case_out[rel] = {
                "sha256": actual,
                "bytes": len(raw_a),
                "reproduction_a_equals_b": True,
                "recorded_historical_identity_match": (
                    True if expected is not None else "NOT_RECORDED"
                ),
                "historical_artifact_status": historical_status,
                "historical_artifact_path": (
                    str(historical_path.relative_to(artifact_root))
                    if historical_path is not None and artifact_root is not None
                    else None
                ),
            }
        manifest["cases"][case] = case_out

    (out / "FIXTURE_MANIFEST.json").write_bytes(canonical(manifest))
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
