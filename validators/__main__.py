"""Entry point for ``python -m validators``.

Dispatches to the three subcommands:
    verify-vocabulary           run validators.verify_vocabulary
    verify-spec-vocabulary      run validators.verify_spec_vocabulary
    verify-integrity            run validators.verify_contract_integrity

Invoke without a subcommand to run all three verifiers (verify-vocabulary and
verify-spec-vocabulary; integrity requires an artifact path so it is only run
when a path is provided via the ``--artifact`` flag).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import verify_contract_integrity, verify_spec_vocabulary, verify_vocabulary


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m validators")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("verify-vocabulary", help="Canonical/consumer drift check")
    sub.add_parser("verify-spec-vocabulary", help="Spec table / YAML cross-check")

    integrity = sub.add_parser("verify-integrity", help="Validate an artifact tree")
    integrity.add_argument("artifact", type=Path)
    integrity.add_argument("--against-pin", type=str, default=None)

    all_parser = sub.add_parser("all", help="Run all verifiers (integrity needs --artifact)")
    all_parser.add_argument("--artifact", type=Path, default=None)
    all_parser.add_argument("--strict", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    args, remainder = _build_parser().parse_known_args(argv)

    if args.command == "verify-vocabulary":
        return verify_vocabulary.main(remainder)
    if args.command == "verify-spec-vocabulary":
        return verify_spec_vocabulary.main(remainder)
    if args.command == "verify-integrity":
        return verify_contract_integrity.run(args.artifact, against_pin=args.against_pin)
    if args.command == "all" or args.command is None:
        strict = getattr(args, "strict", False)
        artifact = getattr(args, "artifact", None)
        rc1 = verify_vocabulary.run(strict=strict)
        print()
        rc2 = verify_spec_vocabulary.run()
        rc3 = 0
        if artifact is not None:
            print()
            rc3 = verify_contract_integrity.run(artifact)
        return max(rc1, rc2, rc3)

    print(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
