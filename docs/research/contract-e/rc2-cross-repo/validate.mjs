import fs from "node:fs";
import assert from "node:assert/strict";

const data = JSON.parse(fs.readFileSync(
  new URL("./FROZEN-NATIVE-OUTPUTS.json", import.meta.url),
  "utf8",
));

function stageEnvelope(d) {
  return {
    subject: d.actor,
    domain: d.authority_domain,
    operation: d.operation,
    target_id: d.target_id,
    current_ref: d.current_hash,
    applicable: true,
  };
}

function semanticEnvelope(r) {
  return {
    subject: r.receipt_id,
    domain: r.domain,
    operation: r.operation,
    target_id: r.target_id,
    current_ref: r.current ? "current" : "stale",
    applicable: r.applicable,
  };
}

function canExercise(envelope, required) {
  return (
    envelope.domain === required.domain
    && envelope.operation === required.operation
    && envelope.target_id === required.target_id
    && envelope.applicable
    && envelope.current_ref !== "stale"
  );
}

const stages = data.stage_descriptors.map(stageEnvelope);
const semantic = data.semantic_receipts.map(semanticEnvelope);

for (const e of [...stages, ...semantic]) {
  assert.equal(typeof e.subject, "string");
  assert.equal(typeof e.domain, "string");
  assert.equal(typeof e.operation, "string");
  assert.equal(typeof e.target_id, "string");
  assert.equal(typeof e.current_ref, "string");
  assert.equal(typeof e.applicable, "boolean");
}

// Exact-domain positives.
for (const e of stages) {
  assert.equal(canExercise(e, {
    domain: e.domain,
    operation: e.operation,
    target_id: e.target_id,
  }), true);
}
for (const e of semantic.filter((x) => x.applicable)) {
  assert.equal(canExercise(e, {
    domain: e.domain,
    operation: e.operation,
    target_id: e.target_id,
  }), true);
}

// Cross-stage laundering attempts.
const source = stages.find((x) => x.domain === "source_access");
const admission = stages.find((x) => x.domain === "evidence_admission");
const assessment = stages.find((x) => x.domain === "assessment_mandate");
const decision = stages.find((x) => x.domain === "decision_mandate");
const numeric = semantic.find((x) => x.domain === "numeric_relation" && x.applicable);
const boundary = semantic.find((x) => x.domain === "source_boundary" && x.applicable);

assert.equal(canExercise(source, {
  domain: admission.domain,
  operation: admission.operation,
  target_id: admission.target_id,
}), false);

assert.equal(canExercise(admission, {
  domain: assessment.domain,
  operation: assessment.operation,
  target_id: assessment.target_id,
}), false);

assert.equal(canExercise(assessment, {
  domain: numeric.domain,
  operation: numeric.operation,
  target_id: numeric.target_id,
}), false);

assert.equal(canExercise(numeric, {
  domain: decision.domain,
  operation: decision.operation,
  target_id: decision.target_id,
}), false);

assert.equal(canExercise(decision, {
  domain: boundary.domain,
  operation: boundary.operation,
  target_id: boundary.target_id,
}), false);

assert.equal(canExercise(boundary, {
  domain: numeric.domain,
  operation: numeric.operation,
  target_id: numeric.target_id,
}), false);

// Inapplicable and stale semantic authority cannot decide.
const wrongScope = semantic.find((x) => !x.applicable);
assert.equal(canExercise(wrongScope, {
  domain: wrongScope.domain,
  operation: wrongScope.operation,
  target_id: wrongScope.target_id,
}), false);

// Effect-specific participant domains remain distinct even under common envelope.
const citation = stages.find((x) => x.operation === "citation.use");
const task = stages.find((x) => x.operation === "task.dispatch");
assert.equal(canExercise(citation, {
  domain: task.domain,
  operation: task.operation,
  target_id: task.target_id,
}), false);

console.log(JSON.stringify({
  independent_consumer: "PASS",
  stage_descriptors: stages.length,
  semantic_receipts: semantic.length,
  cross_domain_laundering_rejected: 7,
  common_structural_envelope: true,
  universal_authority_evaluator_claimed: false,
}, null, 2));
