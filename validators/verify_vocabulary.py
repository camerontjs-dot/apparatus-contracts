"""Canonical-vocabulary drift verifier.

Hashes ``schema/vocabulary.yaml`` against the embedded copy in every consumer
(Claim Audit Lab, Evidence Bundler, and future Research Scaffold Harness) and
compares each consumer's ``schema/.contract-version`` pin file against the
canonical contract version.

Exit codes:
    0 - all consumers in sync (or absent and ``--strict`` not set)
    1 - drift detected, pin mismatch, or absent consumers with ``--strict``
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from ._hashing import hash_file
from ._vocabulary import load_canonical, read_pin


@dataclass(frozen=True)
class ConsumerLocation:
    """Where to look for a consumer's embedded vocabulary copy and pin."""

    name: str
    vocab_path: Path
    pin_path: Path


def default_consumers(asset_root: Path) -> list[ConsumerLocation]:
    """Return the default consumer search paths relative to the asset root.

    Looks at ``../<name>/schema/`` in the portfolio's standard sibling layout.
    Callers may override with explicit paths via the CLI ``--consumer`` flag.
    """
    sibling_root = asset_root.parent
    names = ("claim-audit-lab", "evidence-bundler", "research-scaffold-harness")
    locations: list[ConsumerLocation] = []
    for name in names:
        schema_dir = sibling_root / name / "schema"
        locations.append(
            ConsumerLocation(
                name=name,
                vocab_path=schema_dir / "vocabulary.yaml",
                pin_path=schema_dir / ".contract-version",
            )
        )
    return locations


@dataclass(frozen=True)
class ConsumerResult:
    name: str
    status: str  # "ok", "drift", "pin_mismatch", "not_found", "partial"
    detail: str = ""


def check_consumer(
    consumer: ConsumerLocation,
    canonical_hash: str,
    canonical_version: str,
) -> ConsumerResult:
    """Run all drift checks against one consumer."""
    if not consumer.vocab_path.exists() and not consumer.pin_path.exists():
        return ConsumerResult(
            name=consumer.name,
            status="not_found",
            detail=f"neither {consumer.vocab_path} nor {consumer.pin_path} exists",
        )

    problems: list[str] = []

    if not consumer.vocab_path.exists():
        problems.append(f"missing vocabulary file at {consumer.vocab_path}")
    else:
        actual_hash = hash_file(consumer.vocab_path)
        if actual_hash.lower() != canonical_hash.lower():
            problems.append(
                f"SHA-256 mismatch on {consumer.vocab_path.name}: "
                f"expected {canonical_hash}, got {actual_hash}"
            )

    if not consumer.pin_path.exists():
        problems.append(f"missing pin file at {consumer.pin_path}")
    else:
        pin = read_pin(consumer.pin_path)
        if pin != canonical_version:
            problems.append(
                f".contract-version pin is {pin!r}, "
                f"canonical contract version is {canonical_version!r}"
            )

    if not problems:
        return ConsumerResult(name=consumer.name, status="ok")
    status = "partial" if len(problems) > 1 else (
        "pin_mismatch" if "pin" in problems[0] else "drift"
    )
    return ConsumerResult(name=consumer.name, status=status, detail="; ".join(problems))


def run(
    *,
    asset_root: Path | None = None,
    consumer_overrides: dict[str, Path] | None = None,
    strict: bool = False,
) -> int:
    """Execute the verifier and return the exit code.

    Args:
        asset_root: Path to ``apparatus-contracts/``. Defaults to the parent of
            this file's parent.
        consumer_overrides: Map from consumer name to a ``schema/`` directory
            path that should be checked instead of the default sibling path.
        strict: When True, treat ``not_found`` consumers as failures.
    """
    root = asset_root or Path(__file__).resolve().parent.parent
    canonical = load_canonical(root / "schema" / "vocabulary.yaml")
    canonical_hash = hash_file(root / "schema" / "vocabulary.yaml")
    canonical_pin = read_pin(root / "schema" / ".contract-version")

    if canonical_pin != canonical.contract_version:
        print(
            f"FAIL: canonical {root / 'schema' / '.contract-version'} pins to "
            f"{canonical_pin!r} but vocabulary.yaml declares "
            f"contract_version={canonical.contract_version!r}"
        )
        return 1

    consumers = default_consumers(root)
    if consumer_overrides:
        overridden: list[ConsumerLocation] = []
        for consumer in consumers:
            override = consumer_overrides.get(consumer.name)
            if override is None:
                overridden.append(consumer)
            else:
                overridden.append(
                    ConsumerLocation(
                        name=consumer.name,
                        vocab_path=override / "vocabulary.yaml",
                        pin_path=override / ".contract-version",
                    )
                )
        consumers = overridden

    results = [check_consumer(c, canonical_hash, canonical.contract_version) for c in consumers]
    exit_code = 0
    print(f"canonical: contract_version={canonical.contract_version} hash={canonical_hash}")
    for result in results:
        if result.status == "ok":
            print(f"  [OK]        {result.name}")
        elif result.status == "not_found":
            marker = "[MISSING]  " if strict else "[absent]   "
            print(f"  {marker}{result.name}: {result.detail}")
            if strict:
                exit_code = 1
        else:
            label = {
                "drift": "[DRIFT]    ",
                "pin_mismatch": "[PIN-DIFF] ",
                "partial": "[FAIL]     ",
            }[result.status]
            print(f"  {label}{result.name}: {result.detail}")
            exit_code = 1
    if exit_code == 0:
        print("vocabulary verification passed.")
    else:
        print("vocabulary verification FAILED.")
    return exit_code


def _parse_consumer_override(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError(
            "expected name=path, got " + repr(value)
        )
    name, _, path_str = value.partition("=")
    return name, Path(path_str).resolve()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="verify-vocabulary",
        description="Check that every consumer's vocabulary.yaml and "
        ".contract-version pin match the canonical apparatus-contracts copy.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="treat consumers absent from the sibling layout as failures",
    )
    parser.add_argument(
        "--consumer",
        type=_parse_consumer_override,
        action="append",
        default=[],
        metavar="name=path/to/schema",
        help="override a consumer's schema/ path (repeatable)",
    )
    args = parser.parse_args(argv)
    overrides = dict(args.consumer)
    return run(consumer_overrides=overrides or None, strict=args.strict)


if __name__ == "__main__":
    sys.exit(main())
