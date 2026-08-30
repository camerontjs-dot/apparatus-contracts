import fs from 'node:fs';
import path from 'node:path';

const rc3bDir = process.argv[2] || 'docs/research/contract-e/rc3b-authority-basis-binding';
const rc3aDir = path.resolve(rc3bDir, '../rc3a-authority-warrant-spec');
const load = (p) => JSON.parse(fs.readFileSync(p, 'utf8'));

const fixtures = load(path.join(rc3aDir, 'FROZEN-CASES.json'));
const basisSpec = load(path.join(rc3bDir, 'BASIS-BINDING-SPEC.json'));
const registry = load(path.join(rc3bDir, 'AUTHORITY-BASIS-REGISTRY.json')).records;

const canonical = {
  source_access_ok: 'grant:source-read',
  evidence_admission_ok: 'policy:evidence-admission',
  assessment_ok: 'policy:cal-assessment',
  numeric_ok: 'grant:numeric-validation',
  source_boundary_ok: 'policy:source-boundary',
  decision_ok: 'policy:decision-v1',
  citation_ok: 'grant:citation-use',
  task_ok: 'grant:task-dispatch',
  verify_ok: 'grant:verify'
};

const conferringTypes = new Set(basisSpec.authority_reference.authority_conferring_types);
const records = Object.values(registry).filter((r) => conferringTypes.has(r.type));
const clone = (x) => JSON.parse(JSON.stringify(x));

function recordCovers(record, ref, envelope) {
  if (!record) return { ok: false, reason: 'unresolvable_authority_basis' };
  if (ref.type !== record.type) return { ok: false, reason: 'authority_basis_type_mismatch' };
  if (ref.current !== true || record.current !== true) return { ok: false, reason: 'authority_basis_not_current' };
  if (!record.subject_ids.includes(envelope.subject.id)) return { ok: false, reason: 'authority_basis_subject_mismatch' };
  if (record.authority_domain !== envelope.authority_domain) return { ok: false, reason: 'authority_basis_domain_mismatch' };
  if (!record.operations.includes(envelope.operation)) return { ok: false, reason: 'authority_basis_operation_mismatch' };
  if (!record.scopes.includes(envelope.jurisdiction.scope)) return { ok: false, reason: 'authority_basis_scope_mismatch' };
  if (!record.target_classes.includes(envelope.target.class)) return { ok: false, reason: 'authority_basis_target_class_mismatch' };
  if (Array.isArray(record.target_ids) && record.target_ids.length && !record.target_ids.includes(envelope.target.id)) {
    return { ok: false, reason: 'authority_basis_target_id_mismatch' };
  }
  const t = new Date(envelope.evaluated_at);
  if (!(t >= new Date(record.valid_from) && t <= new Date(record.valid_until))) {
    return { ok: false, reason: 'authority_basis_outside_validity_interval' };
  }
  return { ok: true, reason: null };
}

function replaceConferringReference(base, record) {
  const e = clone(base);
  const idx = e.authority_basis.findIndex((r) => conferringTypes.has(r.type));
  if (idx < 0) throw new Error(`No authority-conferring reference in baseline ${e.participant}/${e.operation}`);
  e.authority_basis[idx] = { type: record.type, id: record.id, current: true };
  return e;
}

const matrix = [];
let failures = 0;
let canonicalAccepts = 0;
let falseAccepts = 0;
let falseRejects = 0;

for (const [baselineName, allowedId] of Object.entries(canonical)) {
  const base = fixtures.baselines[baselineName];
  if (!base) throw new Error(`Missing frozen baseline ${baselineName}`);

  for (const record of records) {
    const e = replaceConferringReference(base, record);
    const ref = e.authority_basis.find((r) => r.id === record.id && conferringTypes.has(r.type));
    const observed = recordCovers(record, ref, e);
    const expectedAccept = record.id === allowedId;
    const pass = observed.ok === expectedAccept;
    if (!pass) {
      failures++;
      if (observed.ok) falseAccepts++;
      else falseRejects++;
    }
    if (expectedAccept && observed.ok) canonicalAccepts++;
    matrix.push({ baseline: baselineName, basis_id: record.id, expected: expectedAccept ? 'accept' : 'reject', observed: observed.ok ? 'accept' : 'reject', reason: observed.reason, pass });
  }
}

const typeMutations = [];
const allConferringTypes = [...conferringTypes].sort();
for (const [baselineName, allowedId] of Object.entries(canonical)) {
  const base = fixtures.baselines[baselineName];
  const record = registry[allowedId];
  for (const wrongType of allConferringTypes.filter((t) => t !== record.type)) {
    const e = replaceConferringReference(base, record);
    const idx = e.authority_basis.findIndex((r) => r.id === allowedId);
    e.authority_basis[idx].type = wrongType;
    const observed = recordCovers(record, e.authority_basis[idx], e);
    const pass = !observed.ok && observed.reason === 'authority_basis_type_mismatch';
    if (!pass) failures++;
    typeMutations.push({ baseline: baselineName, basis_id: allowedId, mutated_type: wrongType, observed: observed.ok ? 'accept' : 'reject', reason: observed.reason, pass });
  }
}

const output = {
  candidate_registry_records_tested: records.length,
  baselines_tested: Object.keys(canonical).length,
  compatibility_matrix_cases: matrix.length,
  canonical_accepts: canonicalAccepts,
  false_accepts: falseAccepts,
  false_rejects: falseRejects,
  type_mutation_cases: typeMutations.length,
  scientific_failures: failures,
  matrix,
  type_mutations: typeMutations,
  terminal_signal: failures === 0 ? 'RC3B_HARDENING_PASS' : 'RC3B_HARDENING_FAIL'
};

fs.writeFileSync(path.join(rc3bDir, 'HARDENING-RESULTS.json'), JSON.stringify(output, null, 2) + '\n');
console.log(JSON.stringify({
  candidate_registry_records_tested: output.candidate_registry_records_tested,
  baselines_tested: output.baselines_tested,
  compatibility_matrix_cases: output.compatibility_matrix_cases,
  canonical_accepts: output.canonical_accepts,
  false_accepts: output.false_accepts,
  false_rejects: output.false_rejects,
  type_mutation_cases: output.type_mutation_cases,
  scientific_failures: output.scientific_failures,
  terminal_signal: output.terminal_signal
}, null, 2));
for (const row of matrix.filter((x) => !x.pass)) console.log('MATRIX_FAILURE', JSON.stringify(row));
for (const row of typeMutations.filter((x) => !x.pass)) console.log('TYPE_FAILURE', JSON.stringify(row));
process.exitCode = failures === 0 ? 0 : 1;
