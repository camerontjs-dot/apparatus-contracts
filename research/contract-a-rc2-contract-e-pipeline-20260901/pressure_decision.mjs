#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { decideContractCToContractD } from "../../_external/decision/src/contractCDecision.js";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../..");
const OUT = path.join(ROOT, "artifacts", "contract-a-rc2-contract-e-gate");
const C_AUTHORITY = path.join(ROOT, "_external", "apparatus-c");

const doc = JSON.parse(fs.readFileSync(path.join(OUT, "PRESSURE-PROJECTIONS.json"), "utf8"));
const rows = [];
for (const projection of doc.projections) {
  for (const target of projection.targets) {
    const context = {
      policy: {
        id: "decision-engine.contract-c.supported-claim-verification",
        version: "1.0.0",
      },
      proposition_id: target.proposition_id,
      target: {
        kind: "claim",
        id: target.proposition_id,
        content_sha256: target.text_sha256,
      },
    };
    const contractCBytes = fs.readFileSync(path.join(ROOT, projection.c_path));
    const decision = decideContractCToContractD({
      contractCBytes,
      expectedContractCSha256: projection.c_sha256,
      contractCAuthorityRoot: C_AUTHORITY,
      expectedContractB: projection.b_binding,
      decisionContext: context,
      pythonExecutable: "python",
    });
    if (decision.target.id !== target.proposition_id) throw new Error("target id changed");
    if (decision.target.content_sha256 !== target.text_sha256) throw new Error("target hash changed");
    if (decision.input_authority.immutable_id !== projection.c_sha256) throw new Error("Contract C binding changed");
    rows.push({
      projection: projection.projection,
      a_handoff_sha256: projection.a_handoff_sha256,
      a_work_id: projection.a_work_id,
      c_sha256: projection.c_sha256,
      c_result_set_id: projection.c_result_set_id,
      b_binding: projection.b_binding,
      target,
      contract_d: decision,
    });
  }
}
fs.writeFileSync(
  path.join(OUT, "PRESSURE-DECISIONS.json"),
  JSON.stringify({ schema: "contract-a-rc2-parent-atom-pressure-decisions-v1", rows }, null, 2) + "\n",
  "utf8",
);
console.log(JSON.stringify({ status: "PASS", decisions: rows.length }));
