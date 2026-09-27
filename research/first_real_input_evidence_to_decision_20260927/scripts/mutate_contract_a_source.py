#!/usr/bin/env python3
"""Create a deliberate Contract A source-byte substitution without resealing hashes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("contract_a", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args()
    value = json.loads(args.contract_a.read_text(encoding="utf-8"))
    sources = value.get("sources")
    if not isinstance(sources, list) or not sources:
        raise SystemExit("Contract A has no source to substitute")
    sources[0]["content"] = sources[0]["content"] + "\nSUBSTITUTION_CONTROL"
    # Intentionally do not update source content hash or handoff hash.
    args.output.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
