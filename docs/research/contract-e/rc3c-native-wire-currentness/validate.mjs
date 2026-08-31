import fs from 'node:fs';
import path from 'node:path';

const dir = process.argv[2] || 'docs/research/contract-e/rc3c-native-wire-currentness';
const rc3aDir = path.resolve(dir, '../rc3a-authority-warrant-spec');
const rc3bDir = path.resolve(dir, '../rc3b-authority-basis-binding');
const load = (p) => JSON.parse(fs.readFileSync(p, 'utf8'));
const spec = load(path.join(rc3aDir, 'SPEC-CANDIDATE.json'));
const shapes = load(path.join(rc3aDir, 'SPEC-SHAPES.json'));
const participantBoundary = load(path.join(rc3aDir, 'SPEC-PARTICIPANT-BOUNDARY.json'));
const inherited = load(path.join(rc3aDir, 'FROZEN-CASES.json'));
const basisSpec = load(path.join(rc3bDir, 'BASIS-BINDING-SPEC.json'));
const baseRegistry = load(path.join(rc3bDir, 'AUTHORITY-BASIS-REGISTRY.json')).records;
const amendment = load(path.join(dir, 'RC3C-SPEC.json'));
const cases = load(path.join(dir, 'FROZEN-CASES.json'));

const clone = (x) => JSON.parse(JSON.stringify(x));
const ACCEPT = () => ({ decision: 'accept', reason: null });
const REJECT = (reason) => ({ decision: 'reject', reason });

function setPath(obj, dotted, value) {
  const parts = dotted.split('.');
  let cur = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    const p = parts[i];
    cur = cur[/^\d+$/.test(p) ? Number(p) : p];
  }
  const last = parts.at(-1);
  cur[/^\d+$/.test(last) ? Number(last) : last] = clone(value);
}

function deletePath(obj, dotted) {
  const parts = dotted.split('.');
  let cur = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    const p = parts[i];
    cur = cur[/^\d+$/.test(p) ? Number(p) : p];
    if (cur == null) return;
  }
  const last = parts.at(-1);
  delete cur[/^\d+$/.test(last) ? Number(last) : last];
}

function materializeEnvelopeCase(c) {
  const e = clone(inherited.baselines[c.base]);
  if (c.set) Object.assign(e, clone(c.set));
  if (c.set_path) for (const [p, v] of Object.entries(c.set_path)) setPath(e, p, v);
  if (c.remove) for (const p of c.remove) deletePath(e, p);
  if (c.remove_authority_basis_types) {
    e.authority_basis = (e.authority_basis || []).filter((b) => !c.remove_authority_basis_types.includes(b.type));
  }
  return e;
}

function findInheritedEnvelopeCase(id) {
  const c = inherited.envelope_cases.find((x) => x.id === id);
  if (!c) throw new Error(`missing inherited envelope case ${id}`);
  return materializeEnvelopeCase(c);
}

function findInheritedPropagationCase(id) {
  const c = inherited.propagation_cases.find((x) => x.id === id);
  if (!c) throw new Error(`missing inherited propagation case ${id}`);
  return clone(c);
}

function findInheritedDelegationCase(id) {
  const c = inherited.delegation_cases.find((x) => x.id === id);
  if (!c) throw new Error(`missing inherited delegation case ${id}`);
  return clone(c);
}

function wireCheck(e) {
  if (!Array.isArray(e.authority_basis)) return REJECT('malformed_authority_basis_shape');
  if (!Array.isArray(e.competence)) return REJECT('malformed_competence_shape');
  if (typeof e?.jurisdiction?.scope !== 'string') return REJECT('malformed_jurisdiction_scope_shape');
  for (const q of e.competence) {
    if (typeof q?.scope !== 'string') return REJECT('malformed_qualification_scope_shape');
  }
  return ACCEPT();
}

const conferringTypes = new Set(basisSpec.authority_reference.authority_conferring_types);
const basisPrecedence = basisSpec.ordering.reason_precedence;

function basisReferenceCheck(ref, e, registry) {
  const record = registry[ref.id];
  if (!record) return REJECT('unresolvable_authority_basis');
  if (ref.type !== record.type) return REJECT('authority_basis_type_mismatch');
  if (ref.current !== true || record.current !== true) return REJECT('authority_basis_not_current');
  const evaluatedAt = new Date(e.evaluated_at);
  if (record.revoked_at && evaluatedAt >= new Date(record.revoked_at)) return REJECT('authority_basis_not_current');
  if (!record.subject_ids.includes(e.subject.id)) return REJECT('authority_basis_subject_mismatch');
  if (record.authority_domain !== e.authority_domain) return REJECT('authority_basis_domain_mismatch');
  if (!record.operations.includes(e.operation)) return REJECT('authority_basis_operation_mismatch');
  if (!record.scopes.includes(e.jurisdiction.scope)) return REJECT('authority_basis_scope_mismatch');
  if (!record.target_classes.includes(e.target.class)) return REJECT('authority_basis_target_class_mismatch');
  if (Array.isArray(record.target_ids) && record.target_ids.length && !record.target_ids.includes(e.target.id)) {
    return REJECT('authority_basis_target_id_mismatch');
  }
  if (!(evaluatedAt >= new Date(record.valid_from) && evaluatedAt <= new Date(record.valid_until))) {
    return REJECT('authority_basis_outside_validity_interval');
  }
  return ACCEPT();
}

function validateAuthorityBasis(e, registry) {
  const domainReq = shapes.domain_basis_requirements[e.authority_domain];
  if (!domainReq) return REJECT('unknown_authority_domain');
  const refs = e.authority_basis;
  const candidates = refs.filter((r) => conferringTypes.has(r.type) && domainReq.any_of.includes(r.type));
  const wrongDomainType = refs.filter((r) => conferringTypes.has(r.type) && !domainReq.any_of.includes(r.type));
  const considered = candidates.length ? candidates : wrongDomainType;
  if (!considered.length) return REJECT('missing_domain_authority_basis');
  const outcomes = considered.map((ref) => basisReferenceCheck(ref, e, registry));
  if (outcomes.some((o) => o.decision === 'accept')) return ACCEPT();
  const reasons = outcomes.map((o) => o.reason);
  for (const r of basisPrecedence) if (reasons.includes(r)) return REJECT(r);
  return REJECT(reasons[0] || 'missing_domain_authority_basis');
}

function validateEnvelope(e, registry = baseRegistry) {
  const wire = wireCheck(e);
  if (wire.decision !== 'accept') return wire;
  if (Object.prototype.hasOwnProperty.call(e, 'authorized') && spec.normative_rules.generic_authorized_boolean_forbidden) {
    return REJECT('generic_authorized_forbidden');
  }
  const required = [...spec.common_envelope.required, ...participantBoundary.common_envelope_additional_required];
  for (const field of required) if (!(field in e)) return REJECT(`missing_required_field:${field}`);
  const domain = spec.authority_domains[e.authority_domain];
  if (!domain) return REJECT('unknown_authority_domain');
  if (!domain.operations.includes(e.operation)) return REJECT('domain_operation_mismatch');
  const participant = spec.participant_declarations[e.participant];
  if (!participant) return REJECT('unknown_participant');
  if (!participant.accepted_domains.includes(e.authority_domain)) return REJECT('participant_domain_out_of_scope');
  if (!participant.accepted_operations.includes(e.operation)) return REJECT('participant_operation_out_of_scope');
  if (!e.jurisdiction.applicable) return REJECT('jurisdiction_inapplicable');
  if (!e.jurisdiction.current) return REJECT('jurisdiction_not_current');
  const basis = validateAuthorityBasis(e, registry);
  if (basis.decision !== 'accept') return basis;
  const req = shapes.domain_basis_requirements[e.authority_domain];
  if (req.qualification) {
    if (!e.competence.length) return REJECT('missing_required_qualification');
    const exact = e.competence.filter((q) => q.type === req.qualification);
    if (!exact.length) return REJECT('qualification_type_mismatch');
    if (!exact.some((q) => q.current === true)) return REJECT('qualification_not_current');
    if (!exact.some((q) => q.subject_id === e.subject.id)) return REJECT('qualification_subject_mismatch');
    if (!exact.some((q) => q.scope === e.jurisdiction.scope)) return REJECT('qualification_scope_mismatch');
  }
  if (req.warrant) {
    if (!e.warrant) return REJECT('missing_required_warrant');
    const w = e.warrant;
    if (w.authority_domain !== e.authority_domain) return REJECT('warrant_domain_mismatch');
    if (w.operation !== e.operation) return REJECT('warrant_operation_mismatch');
    if (w.type !== req.warrant) return REJECT('warrant_type_mismatch');
    if (!w.applicable) return REJECT('warrant_inapplicable');
    if (!w.current) return REJECT('warrant_not_current');
    if (w.target_id !== e.target.id) return REJECT('warrant_target_mismatch');
    if (w.target_hash !== e.target.current_hash) return REJECT('warrant_target_hash_mismatch');
  } else if (e.warrant && !domain.warrant_allowed) {
    return REJECT('warrant_not_allowed_for_domain');
  }
  return ACCEPT();
}

function validatePropagation(c) {
  const never = new Set(spec.propagation.never_implicit);
  const identity = new Set(spec.propagation.identity_provenance_fields);
  if (c.mode === 'none') return c.requested_fields.length ? REJECT('propagation_not_allowed') : ACCEPT();
  for (const field of c.requested_fields) {
    if (never.has(field)) return REJECT(c.mode === 'explicit' ? 'authority_requires_reestablishment' : 'forbidden_authority_propagation');
    if (c.mode === 'identity_provenance_only' && !identity.has(field)) return REJECT('non_provenance_field_not_propagable');
  }
  return ACCEPT();
}

function validateDelegation(c) {
  const p = c.parent;
  const d = c.child;
  if (!Array.isArray(d.operations)) return REJECT('malformed_delegation_operations_shape');
  if (!Array.isArray(d.scope)) return REJECT('malformed_delegation_scope_shape');
  if (!Array.isArray(p.operations)) return REJECT('malformed_delegation_operations_shape');
  if (!Array.isArray(p.scope)) return REJECT('malformed_delegation_scope_shape');
  if (d.parent_authority_id !== p.id) return REJECT('delegation_parent_mismatch');
  if (d.authority_domain !== p.authority_domain) return REJECT('delegation_domain_amplification');
  if (d.operations.some((op) => !p.operations.includes(op))) return REJECT('delegation_operation_amplification');
  if (d.scope.some((s) => !p.scope.includes(s))) return REJECT('delegation_scope_amplification');
  if (d.valid_until && p.valid_until && new Date(d.valid_until) > new Date(p.valid_until)) return REJECT('delegation_expiry_amplification');
  if (!p.current || !d.current) return REJECT('delegation_not_current');
  return ACCEPT();
}

const results = { currentness: [], wire: [], delegation_wire: [], reasons: [], semantic_metamorphic: [], summary: {} };
let failures = 0;

for (const c of cases.currentness_cases) {
  const e = clone(inherited.baselines[c.base]);
  if (c.set) Object.assign(e, clone(c.set));
  if (c.set_path) for (const [p, v] of Object.entries(c.set_path)) setPath(e, p, v);
  const registry = clone(baseRegistry);
  if (c.record_override) Object.assign(registry[c.record_override.id], clone(c.record_override.set));
  const got = validateEnvelope(e, registry);
  const ok = got.decision === c.expected && (c.expected === 'accept' || got.reason === c.reason);
  results.currentness.push({ id: c.id, expected: c.expected, expected_reason: c.reason || null, observed: got, pass: ok });
  if (!ok) failures++;
}

for (const c of cases.wire_cases) {
  const e = clone(inherited.baselines[c.base]);
  if (c.set_path) for (const [p, v] of Object.entries(c.set_path)) setPath(e, p, v);
  if (c.replace_path_with_first_item) e[c.replace_path_with_first_item] = clone(e[c.replace_path_with_first_item][0]);
  const got = validateEnvelope(e);
  const ok = got.decision === c.expected && (c.expected === 'accept' || got.reason === c.reason);
  results.wire.push({ id: c.id, expected: c.expected, expected_reason: c.reason || null, observed: got, pass: ok });
  if (!ok) failures++;
}

for (const c of cases.delegation_wire_cases) {
  const d = findInheritedDelegationCase(c.source_case);
  if (c.set_path) for (const [p, v] of Object.entries(c.set_path)) setPath(d, p, v);
  const got = validateDelegation(d);
  const ok = got.decision === c.expected && (c.expected === 'accept' || got.reason === c.reason);
  results.delegation_wire.push({ id: c.id, expected: c.expected, expected_reason: c.reason || null, observed: got, pass: ok });
  if (!ok) failures++;
}

for (const c of cases.reason_cases) {
  let got;
  if (c.source_envelope_case) got = validateEnvelope(findInheritedEnvelopeCase(c.source_envelope_case));
  else if (c.source_propagation_case) got = validatePropagation(findInheritedPropagationCase(c.source_propagation_case));
  else throw new Error(`reason case lacks source ${c.id}`);
  const ok = got.decision === c.expected && got.reason === c.reason;
  results.reasons.push({ id: c.id, expected: c.expected, expected_reason: c.reason, observed: got, pass: ok });
  if (!ok) failures++;
}

for (const baseName of cases.semantic_metamorphic.bases) {
  const base = clone(inherited.baselines[baseName]);
  const reference = validateEnvelope(base);
  for (let i = 0; i < cases.semantic_metamorphic.variants.length; i++) {
    const e = clone(base);
    e.result = clone(cases.semantic_metamorphic.variants[i]);
    const got = validateEnvelope(e);
    const changed = got.decision !== reference.decision || got.reason !== reference.reason;
    const ok = !changed;
    results.semantic_metamorphic.push({ base: baseName, variant: i + 1, changed, observed: got, pass: ok });
    if (!ok) failures++;
  }
}

const amendmentShapeChecks = [
  amendment.currentness.reference_false_must_reject_even_when_record_current === true,
  amendment.currentness.reference_true_cannot_override_noncurrent_record === true,
  amendment.currentness.validity_interval_bounds === 'inclusive',
  amendment.canonical_wire.silent_singular_plural_coercion_forbidden === true,
  amendment.canonical_wire.common_envelope.authority_basis.json_type === 'array',
  amendment.canonical_wire.common_envelope.competence.json_type === 'array',
  amendment.canonical_wire.Delegation.operations.json_type === 'array',
  amendment.canonical_wire.Delegation.scope.json_type === 'array',
  amendment.reason_contract.inherited_rc3a_reason_strings === 'historical_non_normative_unless_explicitly_relisted'
];
if (!amendmentShapeChecks.every(Boolean)) failures++;

const semanticAuthorityChanges = results.semantic_metamorphic.filter((x) => x.changed).length;
results.summary = {
  currentness_cases: results.currentness.length,
  wire_cases: results.wire.length,
  delegation_wire_cases: results.delegation_wire.length,
  reason_cases: results.reasons.length,
  semantic_metamorphic_cases: results.semantic_metamorphic.length,
  semantic_authority_changes: semanticAuthorityChanges,
  scientific_failures: failures,
  terminal_signal: failures === 0 ? 'CANDIDATE_SURVIVED_RC3C' : 'CANDIDATE_FAILED_RC3C'
};

fs.writeFileSync(path.join(dir, 'RESULTS.json'), JSON.stringify(results, null, 2) + '\n');
console.log(JSON.stringify(results.summary, null, 2));
for (const group of ['currentness', 'wire', 'delegation_wire', 'reasons', 'semantic_metamorphic']) {
  for (const r of results[group].filter((x) => !x.pass)) console.log(`${group.toUpperCase()}_FAILURE`, JSON.stringify(r));
}
if (failures) process.exit(1);
