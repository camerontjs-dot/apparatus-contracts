from __future__ import annotations

import argparse
import json
from pathlib import Path

OPS = ("validate", "canonical", "identity", "consume")


def first_exception(rows, op):
    for row in rows:
        if row[op]["status"] != "ok":
            return row["depth"], row[op].get("type", "exception")
    return None, None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--reference", type=Path, required=True)
    p.add_argument("--independent", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    ref = json.loads(args.reference.read_text())
    ind = json.loads(args.independent.read_text())
    ref_by = {x["depth"]: x for x in ref["rows"]}
    ind_by = {x["depth"]: x for x in ind["rows"]}

    thresholds = {}
    for name, payload in (("reference", ref), ("independent", ind)):
        thresholds[name] = {op: first_exception(payload["rows"], op) for op in OPS}

    divergences = []
    for depth in sorted(set(ref_by) & set(ind_by)):
        for op in OPS:
            r, i = ref_by[depth][op], ind_by[depth][op]
            rs = (r["status"], r.get("type"), r.get("value"))
            ins = (i["status"], i.get("type"), i.get("value"))
            if rs != ins:
                divergences.append({"depth": depth, "operation": op, "reference": r, "independent": i})

    payload = {
        "schema": "contract-d-depth-comparison-summary-v1",
        "python": ref["python"],
        "thresholds": thresholds,
        "divergences": divergences,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.with_suffix(".json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    lines = ["# Frozen implementation depth comparison", "", f"Python: `{ref['python']}`", "",
             "| Implementation | Validate first exception | Canonical first exception | Identity first exception | Consume first exception |",
             "|---|---|---|---|---|"]
    for name in ("reference", "independent"):
        vals = []
        for op in OPS:
            depth, typ = thresholds[name][op]
            vals.append("none" if depth is None else f"{depth} ({typ})")
        lines.append(f"| {name} | " + " | ".join(vals) + " |")
    lines += ["", f"Cross-implementation differing cells: **{len(divergences)}**", ""]
    for d in divergences:
        lines.append(
            f"- depth {d['depth']} `{d['operation']}`: reference `{d['reference']}` vs independent `{d['independent']}`"
        )
    args.out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
