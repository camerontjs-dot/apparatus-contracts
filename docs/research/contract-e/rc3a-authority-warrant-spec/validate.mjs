import fs from 'node:fs';
import path from 'node:path';

const dir = process.argv[2] || 'docs/research/contract-e/rc3a-authority-warrant-spec';
const load = (name) => JSON.parse(fs.readFileSync(path.join(dir, name), 'utf8'));
const spec = load('SPEC-CANDIDATE.json');
const shapes = load('SPEC-SHAPES.json');
const participantBoundary = load('SPEC-PARTICIPANT-BOUNDARY.json');
const fixtures = load('FROZEN-CASES.json');

const clone = (x) => JSON.parse(JSON.stringify(x));

function setPath(obj, dotted, value) {
  const parts = dotted.split('.');
  let cur = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    const p = parts[i];
    cur = cur[/^\d+$/.test(p) ? Number(p) : p];
  }
  const last = parts.at(-1);
  cur[/^\d+$/.test(last) ? Number(last) : last] = value;
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

function materializeCase(c) {
  const e = clone(fixtures.baselines[c.base]);
  if (c.set) Object.assign(e, clone(c.set));
  if (c.set_path) for (const [p, v] of Object.entries(c.set_path)) setPath(e, p, clone(v));
  if (c.remove) for (const p of c.remove) deletePath(e, p);
  if (c.remove_authority_basis_types) {
    e.authority_basis = (e.authority_basis || []).filter((b) => !c.remove_authority_basis_types.includes(b.type));
  }
  return e;
}

const ACCEPT = (extra = {}) => ({ decision: 'accept', reason: null, ...extra });
const REJECT = (reason, extra = {}) => ({ decision: 'reject', reason, ...extra });

function validateEnvelope(e) {
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

  const basisReq = shapes.domain_basis_requirements[e.authority_domain];
  const basis = Array.isArray(e.authority_basis) ? e.authority_basis : [];
  const requiredPresent = basis.filter((b) => basisReq.any_of.includes(b.type));
  if (requiredPresent.length && !requiredPresent.some((b) => b.current)) return REJECT('authority_basis_not_current');
  if (!requiredPresent.some((b) => b.current)) return REJECT('missing_domain_authority_basis');

  if (basisReq.qualification) {
    const quals = Array.isArray(e.competence) ? e.competence : [];
    if (!quals.length) return REJECT('missing_required_qualification');
    const exactType = quals.filter((q) => q.type === basisReq.qualification);
    if (!exactType.length) return REJECT('qualification_type_mismatch');
    if (!exactType.some((q) => q.current)) return REJECT('qualification_not_current');
    if (!exactType.some((q) => q.subject_id === e.subject.id)) return REJECT('qualification_subject_mismatch');
    if (!exactType.some((q) => q.scope === e.jurisdiction.scope)) return REJECT('qualification_scope_mismatch');
  }

  if (basisReq.warrant) {
    if (!e.warrant) return REJECT('missing_required_warrant');
    const w = e.warrant;
    if (w.authority_domain !== e.authority_domain) return REJECT('warrant_domain_mismatch');
    if (w.operation !== e.operation) return REJECT('warrant_operation_mismatch');
    if (w.type !== basisReq.warrant) return REJECT('warrant_type_mismatch');
    if (!w.applicable) return REJECT('warrant_inapplicable');
    if (!w.current) return REJECT('warrant_not_current');
    if (w.target_id !== e.target.id) return REJECT('warrant_target_mismatch');
    if (w.target_hash !== e.target.current_hash) return REJECT('warrant_target_hash_mismatch');
  } else if (e.warrant && !domain.warrant_allowed) {
    return REJECT('warrant_not_allowed_for_domain');
  }

  if (!spec.common_envelope.propagation_modes.includes(e.propagation.mode)) return REJECT('unknown_propagation_mode');
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
  if (d.parent_authority_id !== p.id) return REJECT('delegation_parent_mismatch');
  if (d.authority_domain !== p.authority_domain) return REJECT('delegation_domain_amplification');
  if (d.operations.some((op) => !p.operations.includes(op))) return REJECT('delegation_operation_amplification');
  if (d.scope.some((s) => !p.scope.includes(s))) return REJECT('delegation_scope_amplification');
  if (new Date(d.valid_until) > new Date(p.valid_until)) return REJECT('delegation_expiry_amplification');
  if (!p.current || !d.current) return REJECT('delegation_not_current');
  return ACCEPT();
}

function validateHistorical(c) {
  const h = c.historical_record;
  if (!h.evaluated_at || !Array.isArray(h.authority_basis_ids) || typeof h.authority_was_valid_at_time !== 'boolean') {
    return REJECT('malformed_historical_record');
  }
  if (c.mode === 'historical_record') return h.authority_was_valid_at_time ? ACCEPT({ currently_valid: c.current_authority.current }) : REJECT('not_valid_at_time');
  if (c.mode === 'new_exercise') return c.current_authority.current ? ACCEPT() : REJECT('current_authority_required');
  return REJECT('unknown_historical_mode');
}

function naiveCollapsed(o) {
  return Boolean(o.authorized || (o.trusted && o.confidence >= 0.9) || o.success);
}

function naiveTransitive(chain) {
  return chain.upstream_authority_fields.length > 0 ? [...chain.downstream_requested] : [];
}

function naiveCredentialOnly(e) {
  return Array.isArray(e.competence) && e.competence.some((q) => q.current === true);
}

const results = { envelope: [], propagation: [], delegation: [], historical: [], negative_controls: {}, semantic_invariance: [] };
let scientificFailures = 0;

for (const c of fixtures.envelope_cases) {
  const e = materializeCase(c);
  const got = validateEnvelope(e);
  const expectedOk = got.decision === c.expected && (c.expected === 'accept' || got.reason === c.reason);
  results.envelope.push({ id: c.id, expected: c.expected, expected_reason: c.reason || null, observed: got.decision, observed_reason: got.reason, pass: expectedOk });
  if (!expectedOk) scientificFailures++;
}

for (const c of fixtures.propagation_cases) {
  const got = validatePropagation(c);
  const ok = got.decision === c.expected && (c.expected === 'accept' || got.reason === c.reason);
  results.propagation.push({ id: c.id, expected: c.expected, observed: got.decision, observed_reason: got.reason, pass: ok });
  if (!ok) scientificFailures++;
}

for (const c of fixtures.delegation_cases) {
  const got = validateDelegation(c);
  const ok = got.decision === c.expected && (c.expected === 'accept' || got.reason === c.reason);
  results.delegation.push({ id: c.id, expected: c.expected, observed: got.decision, observed_reason: got.reason, pass: ok });
  if (!ok) scientificFailures++;
}

for (const c of fixtures.historical_cases) {
  const got = validateHistorical(c);
  const ok = got.decision === c.expected && (c.expected === 'accept' || got.reason === c.reason);
  results.historical.push({ id: c.id, expected: c.expected, observed: got.decision, observed_reason: got.reason, pass: ok });
  if (!ok) scientificFailures++;
}

const resultVariants = [
  { status: 'supported', confidence: 1.0, success: true },
  { status: 'contradicted', confidence: 0.0, success: false },
  { status: 'unknown', arbitrary_nested_semantics: { x: [1, 2, 3] } }
];
for (const [name, base] of Object.entries(fixtures.baselines)) {
  const reference = validateEnvelope(base);
  for (let i = 0; i < resultVariants.length; i++) {
    const mutated = clone(base);
    mutated.result = resultVariants[i];
    const got = validateEnvelope(mutated);
    const ok = got.decision === reference.decision && got.reason === reference.reason;
    results.semantic_invariance.push({ base: name, variant: i + 1, pass: ok, observed: got });
    if (!ok) scientificFailures++;
  }
}

const collapsedUnsafe = fixtures.negative_controls.collapsed_objects.filter(naiveCollapsed).map((x) => x.id);
const transitiveUnsafe = naiveTransitive(fixtures.negative_controls.transitive_chain);
const qualifiedNoMandate = materializeCase(fixtures.envelope_cases.find((x) => x.id === 'N01-qualified-no-mandate'));
const credentialUnsafe = naiveCredentialOnly(qualifiedNoMandate);
results.negative_controls = {
  collapsed_authority_unsafe_permits: collapsedUnsafe,
  transitive_inheritance_unsafe_downstream: transitiveUnsafe,
  credential_only_unsafe_permit: credentialUnsafe,
  intended_direction: collapsedUnsafe.length > 0 && transitiveUnsafe.length > 0 && credentialUnsafe === true
};
if (!results.negative_controls.intended_direction) scientificFailures++;

results.summary = {
  scientific_failures: scientificFailures,
  envelope_cases: results.envelope.length,
  propagation_cases: results.propagation.length,
  delegation_cases: results.delegation.length,
  historical_cases: results.historical.length,
  semantic_invariance_cases: results.semantic_invariance.length,
  negative_controls_failed_safely: results.negative_controls.intended_direction,
  terminal_signal: scientificFailures === 0 ? 'CANDIDATE_SURVIVED_RC3A' : 'CANDIDATE_FAILED_RC3A'
};

fs.writeFileSync(path.join(dir, 'RESULTS.json'), JSON.stringify(results, null, 2) + '\n');
console.log(JSON.stringify(results.summary, null, 2));
for (const r of results.envelope.filter((x) => !x.pass)) console.log('ENVELOPE_FAILURE', JSON.stringify(r));
for (const r of results.propagation.filter((x) => !x.pass)) console.log('PROPAGATION_FAILURE', JSON.stringify(r));
for (const r of results.delegation.filter((x) => !x.pass)) console.log('DELEGATION_FAILURE', JSON.stringify(r));
for (const r of results.historical.filter((x) => !x.pass)) console.log('HISTORICAL_FAILURE', JSON.stringify(r));
process.exitCode = scientificFailures === 0 ? 0 : 1;
