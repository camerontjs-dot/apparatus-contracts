"""Run the preregistered Contract-C RC2 producer information-sufficiency gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from research_contract_c_rc2.producer_gate import run_experiment


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eb-root", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--rc2d-suite", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    summary = run_experiment(
        eb_root=args.eb_root,
        fixture=args.fixture,
        rc2d_suite_path=args.rc2d_suite,
        out_dir=args.out,
    )
    print("CONTRACT_C_RC2_PRODUCER_GATE=" + summary["producer_gate"])
    print("CONTRACT_C_RC2_SUMMARY=" + json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
