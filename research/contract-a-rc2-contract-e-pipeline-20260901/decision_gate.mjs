#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  ContractCDecisionError,
  decideContractCToContractD,
} from "../../_external/decision/src/contractCDecision.js";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../..");
const OUT = path.join(ROOT, "artifacts", "contract-a-rc2-contract-e-gate");
const C_AUTHORITY = path.join(ROOT, "_external", "apparatus-c");

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

function writeJson(p, value) {
  fs.writeFileSync(p, JSON.stringify(value, null, 2) + "\n", "utf8");
}

function decide(caseRow, target) {
  const cPath = path.join(ROOT, caseRow.c_path);
  const contractCBytes = fs.readFileSync(cPath);
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
  return {
    context,
    decision: decideContractCToContractD({
      contractCBytes,
      expectedContractCSha256: caseRow.c_sha256,
      contractCAuthorityRoot: C_AUTHORITY,
      expectedContractB: caseRow.b_binding,
      decisionContext: context,
      pythonExecutable: "python",
    }),
  };
}

function expectCode(fn, code) {
  try {
    fn();
  } catch (error) {
    if (!(error instanceof ContractCDecisionError)) throw error;
    if (error.code !== code) {
      throw new Error(`expected ${code}, got ${error.code}: ${error.message}`);
    }
    return;
  }
  throw new Error(`expected ${code} but call succeeded`);
}

const pre = readJson(path.join(OUT, "PREDECISION.json"));
const rows = [];
for (const caseRow of pre.cases) {
  for (const target of caseRow.targets) {
    const got = decide(caseRow, target);
    if (got.decision.target.id !== target.proposition_id) {
      throw new Error("Contract D target proposition identity changed");
    }
    if (got.decision.target.content_sha256 !== target.text_sha256) {
      throw new Error("Contract D target content binding changed");
    }
    if (got.decision.input_authority.immutable_id !== caseRow.c_sha256) {
      throw new Error("Contract D lost exact Contract C whole-object binding");
    }
    rows.push({
      case_name: caseRow.name,
      a_state: caseRow.state,
      a_handoff_id: caseRow.a_handoff_id,
      a_handoff_sha256: caseRow.a_handoff_sha256,
      a_work_id: caseRow.a_work_id,
      a_producer: caseRow.a_producer,
      b_binding: caseRow.b_binding,
      c_result_set_id: caseRow.c_result_set_id,
      c_sha256: caseRow.c_sha256,
      target,
      decision_context: got.context,
      contract_d: got.decision,
    });
  }
}

const baseline = pre.cases.find((row) => row.name === "declared");
const hostile = pre.cases.find((row) => row.name === "declared-hostile-excluded-metadata");
if (!baseline || !hostile) throw new Error("missing declared invariance pair");
if (JSON.stringify(baseline.targets) !== JSON.stringify(hostile.targets)) {
  throw new Error("excluded metadata changed Contract A targets");
}

const probeTarget = baseline.targets[0];
const cBytes = fs.readFileSync(path.join(ROOT, baseline.c_path));
const goodContext = {
  policy: {
    id: "decision-engine.contract-c.supported-claim-verification",
    version: "1.0.0",
  },
  proposition_id: probeTarget.proposition_id,
  target: {
    kind: "claim",
    id: probeTarget.proposition_id,
    content_sha256: probeTarget.text_sha256,
  },
};

expectCode(
  () => decideContractCToContractD({
    contractCBytes: cBytes,
    expectedContractCSha256: baseline.c_sha256,
    contractCAuthorityRoot: C_AUTHORITY,
    expectedContractB: { ...baseline.b_binding, bundle_id: baseline.b_binding.bundle_id + "-substituted" },
    decisionContext: goodContext,
    pythonExecutable: "python",
  }),
  "contract_b_binding_mismatch",
);
expectCode(
  () => decideContractCToContractD({
    contractCBytes: cBytes,
    expectedContractCSha256: baseline.c_sha256,
    contractCAuthorityRoot: C_AUTHORITY,
    expectedContractB: baseline.b_binding,
    decisionContext: {
      ...goodContext,
      target: { ...goodContext.target, content_sha256: "sha256:" + "9".repeat(64) },
    },
    pythonExecutable: "python",
  }),
  "target_binding_mismatch",
);
expectCode(
  () => decideContractCToContractD({
    contractCBytes: cBytes,
    expectedContractCSha256: "sha256:" + "0".repeat(64),
    contractCAuthorityRoot: C_AUTHORITY,
    expectedContractB: baseline.b_binding,
    decisionContext: goodContext,
    pythonExecutable: "python",
  }),
  "contract_c_whole_object_mismatch",
);

const out = {
  schema: "contract-a-rc2-contract-e-decision-stage-v1",
  rows,
  negative_controls: {
    wrong_contract_b_rejected: true,
    wrong_target_hash_rejected: true,
    wrong_contract_c_hash_rejected: true,
  },
};
writeJson(path.join(OUT, "DECISIONS.json"), out);
console.log(JSON.stringify({ status: "PASS", decisions: rows.length, negative_controls: 3 }));
