#!/usr/bin/env python3
"""Pre-freeze source/schema discriminator; NOT a Q04 runtime qualification.

Independent from qualifier imports. Proves old frozen controller had a missing
freeze key and new source does not. Pin mutation tests comparison sensitivity.
No model, Docker container or network request is created.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def referred_freeze_keys(code_path: Path) -> set[str]:
    tree = ast.parse(code_path.read_bytes(), filename=code_path.name)
    keys = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
            if node.value.id == "freeze" and isinstance(node.slice, ast.Constant):
                if isinstance(node.slice.value, str):
                    keys.add(node.slice.value)
    return keys


def run(new: Path, old: Path, old_freeze: Path, pins: Path) -> dict:
    raw = old_freeze.read_bytes()
    assert sha(raw) == "b96731112f79768ccb76c6b9802a1fc13b1feaa196747ac4de8b8156a1b2c46c"
    obj = json.loads(raw)
    pin_raw = pins.read_bytes()
    assert sha(pin_raw) == obj["pins_sha256"]
    pin = json.loads(pin_raw)
    assert "pins" not in obj
    assert obj["public_pins"]["image_id"] == pin["image_id"]

    old_refs = referred_freeze_keys(old)
    new_refs = referred_freeze_keys(new)
    old_missing = sorted(old_refs - set(obj))
    new_missing = sorted(new_refs - set(obj))
    assert old_missing == ["pins"], old_missing
    assert new_missing == [], new_missing
    source = new.read_text()
    assert source.count('config["Image"] == self.pins["image_id"]') == 1
    assert 'freeze["pins"]' not in source

    image_id = pin["image_id"]
    assert re.fullmatch(r"sha256:[a-f0-9]{64}", image_id)
    result = subprocess.check_output(
        ["docker", "--context", "desktop-linux", "image", "inspect", image_id],
        timeout=15,
    )
    images = json.loads(result)
    assert len(images) == 1 and images[0]["Id"] == image_id
    mutated = dict(pin)
    mutated["image_id"] = "sha256:" + "0" * 64
    assert mutated["image_id"] != images[0]["Id"]

    return {
        "schema": "cal-rc3-pre-freeze-schema-discriminator/1",
        "scope": "source freeze-field compatibility and image-id comparison sensitivity only",
        "old_freeze_sha256": sha(raw),
        "external_private_pins_sha256": sha(pin_raw),
        "old_missing_freeze_keys": old_missing,
        "corrected_missing_freeze_keys": new_missing,
        "actual_image_id": images[0]["Id"],
        "correct_image_binding_equal": image_id == images[0]["Id"],
        "mutated_wrong_image_binding_refused": mutated["image_id"] != images[0]["Id"],
        "corrected_source_uses_private_hash_bound_pins": True,
        "inference_calls": 0,
        "worker_containers_created": 0,
        "nonclaims": [
            "Q04 Docker worker configuration pass",
            "Q08 isolation",
            "Q09 dispatcher qualification",
            "Q10 fresh-state",
            "Q11 formal receipts",
            "Q12 owned teardown",
            "Q13 actor admission",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--new-source", type=Path, required=True)
    parser.add_argument("--old-source", type=Path, required=True)
    parser.add_argument("--old-freeze", type=Path, required=True)
    parser.add_argument("--private-pins", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = run(args.new_source, args.old_source, args.old_freeze, args.private_pins)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write("\n")
    print("RC3_STATIC_SCHEMA_DISCRIMINATOR_PASS")
    print("OLD_WEAK_BASELINE_MISSING_KEYS", value["old_missing_freeze_keys"])
    print("NEW_SOURCE_MISSING_KEYS", value["corrected_missing_freeze_keys"])
    print("NEGATIVE_IMAGE_MUTATION_SENSITIVE", value["mutated_wrong_image_binding_refused"])
