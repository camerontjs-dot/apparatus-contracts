import fs from 'node:fs';
import path from 'node:path';

const rc3bDir = process.argv[2] || 'docs/research/contract-e/rc3b-authority-basis-binding';
const rc3aDir = path.resolve(rc3bDir, '../rc3a-authority-warrant-spec');
const load = (p) => JSON.parse(fs.readFileSync(p, 'utf8'));
const spec = load(path.join(rc3aDir, 'SPEC-CANDIDATE.json'));
const shapes = load(path.join(rc3aDir, 'SPEC-SHAPES.json'));
const participantBoundary = load(path.join(rc3aDir, 'SPEC-PARTICIPANT-BOUNDARY.json'));
const fixtures = load(path.join(rc3aDir, 'FROZEN-CASES.json'));
const basisSpec = load(path.join(rc3bDir, 'BASIS-BINDING-SPEC.json'));
const registry = load(path.join(rc3bDir, 'AUTHORITY-BASIS-REGISTRY.json')).records;
const attacks = load(path.join(rc3bDir, 'FROZEN-BASIS-ATTACKS.json'));

const clone = (x) => JSON.parse(JSON.stringify(x));
const ACCEPT = (extra = {}) => ({ decision: 'accept', reason: null, ...extra });
const REJECT = (reason, extra = {}) => ({ decision: 'reject', reason, ...extra });

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

function materializeRc3aCase(c) {
  const e = clone(fixtures.baselines[c.base]);
  if (c.set) Object.assign(e, clone(c.set));
  if (c.set_path) for (const [p, v] of Object.entries(c.set_path)) setPath(e, p, clone(v));
  if (c.remove) for (const p of c.remove) deletePath(e, p);
  if (c.remove_authority_basis_types) {
    e.authority_basis = (e.authority_basis || []).filter((b) => !c.remove_authority_basis_types.includes(b.type));
  }
  return e;
}

function materializeBasisAttack(c) {
  const e = clone(fixtures.baselines[c.base]);
  if (c.replace_authority_reference) {
    const { old_id, new_ref } = c.replace_authority_reference;
    const idx = e.authority_basis.findIndex((b) => b.id === old_id);
    if (idx < 0) throw new Error(`Frozen attack ${c.id} cannot find ${old_id}`);
    e.authority_basis[idx] = clone(new_ref);
  }
  return e;
}

const conferringTypes = new Set(basisSpec.authority_reference.authority_conferring_types);
const precedence = basisSpec.ordering.reason_precedence;

function basisReferenceCheck(ref, e) {
  const record = registry[ref.id];
  if (!record) return REJECT('unresolvable_authority_basis');
  if (ref.type !== record.type) return REJECT('authority_basis_type_mismatch');
  if (ref.current !== true || record.current !== true) return REJECT('authority_basis_not_current');
  if (!record.subject_ids.includes(e.subject.id)) return REJECT('authority_basis_subject_mismatch');
  if (record.authority_domain !== e.authority_domain) return REJECT('authority_basis_domain_mismatch');
  if (!record.operations.includes(e.operation)) return REJECT('authority_basis_operation_mismatch');
  if (!record.scopes.includes(e.jurisdiction.scope)) return REJECT('authority_basis_scope_mismatch');
  if (!record.target_classes.includes(e.target.class)) return REJECT('authority_basis_target_class_mismatch');
  if (Array.isArray(record.target_ids) && record.target_ids.length && !record.target_ids.includes(e.target.id)) {
    return REJECT('authority_basis_target_id_mismatch');
  }
  const t = new Date(e.evaluated_at);
  if (!(t >= new Date(record.valid_from) && t <= new Date(record.valid_until))) {
    return REJECT('authority_basis_outside_validity_interval');
  }
  return ACCEPT({ record_id: record.id });
}

function validateAuthorityBasis(e) {
  const domainReq = shapes.domain_basis_requirements[e.authority_domain];
  const refs = Array.isArray(e.authority_basis) ? e.authority_basis : [];
  const candidates = refs.filter((r) => conferringTypes.has(r.type) && domainReq.any_of.includes(r.type));
  const alsoConferringWrongTypeForDomain = refs.filter((r) => conferringTypes.has(r.type) && !domainReq.any_of.includes(r.type));
  const considered = candidates.length ? candidates : alsoConferringWrongTypeForDomain;
  if (!considered.length) return REJECT('missing_domain_authority_basis');

  const outcomes = considered.map((ref) => basisReferenceCheck(ref, e));
  const success = outcomes.find((o) => o.decision === 'accept');
  if (success) return success;

  const reasons = outcomes.map((o) => o.reason);
  for (const r of precedence) if (reasons.includes(r)) return REJECT(r);
  return REJECT(reasons[0] || 'missing_domain_authority_basis');
}

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

  const basisResult = validateAuthorityBasis(e);
  if (basisResult.decision !== 'accept') return basisResult;

  const basisReq = shapes.domain_basis_requirements[e.authority_domain];
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

const results = {
  inherited_envelope: [],
  direct_basis_attacks: [],
  propagation: [],
  delegation: [],
  historical: [],
  semantic_invariance: [],
  negative_controls: {},
  key_counterexamples: {}
};
let failures = 0;

for (const c of fixtures.envelope_cases) {
  const e = materializeRc3aCase(c);
  const got = validateEnvelope(e);
  const isPositive = c.expected === 'accept';
  let ok = isPositive ? got.decision === 'accept' : got.decision === 'reject';
  if (c.id === 'N13-supported-does-not-cite') ok = got.decision === 'reject' && got.reason === 'authority_basis_domain_mismatch';
  if (c.id === 'N14-decision-does-not-execute') ok = got.decision === 'reject' && got.reason === 'authority_basis_domain_mismatch';
  results.inherited_envelope.push({ id: c.id, expected: c.expected, prior_reason: c.reason || null, observed: got.decision, observed_reason: got.reason, pass: ok });
  if (!ok) failures++;
}

for (const c of attacks.cases) {
  const e = materializeBasisAttack(c);
  const got = validateEnvelope(e);
  const ok = got.decision === c.expected && (c.expected === 'accept' || got.reason === c.reason);
  results.direct_basis_attacks.push({ id: c.id, expected: c.expected, expected_reason: c.reason || null, observed: got.decision, observed_reason: got.reason, pass: ok });
  if (!ok) failures++;
}

for (const c of fixtures.propagation_cases) {
  const got = validatePropagation(c);
  const ok = got.decision === c.expected && (c.expected === 'accept' || got.reason === c.reason);
  results.propagation.push({ id: c.id, pass: ok, observed: got });
  if (!ok) failures++;
}
for (const c of fixtures.delegation_cases) {
  const got = validateDelegation(c);
  const ok = got.decision === c.expected && (c.expected === 'accept' || got.reason === c.reason);
  results.delegation.push({ id: c.id, pass: ok, observed: got });
  if (!ok) failures++;
}
for (const c of fixtures.historical_cases) {
  const got = validateHistorical(c);
  const ok = got.decision === c.expected && (c.expected === 'accept' || got.reason === c.reason);
  results.historical.push({ id: c.id, pass: ok, observed: got });
  if (!ok) failures++;
}

const variants = [
  { status: 'supported', confidence: 1.0, success: true },
  { status: 'contradicted', confidence: 0.0, success: false },
  { status: 'unknown', arbitrary_nested_semantics: { x: [1, 2, 3] } }
];
for (const [name, base] of Object.entries(fixtures.baselines)) {
  const reference = validateEnvelope(base);
  for (let i = 0; i < variants.length; i++) {
    const e = clone(base);
    e.result = variants[i];
    const got = validateEnvelope(e);
    const ok = got.decision === reference.decision && got.reason === reference.reason;
    results.semantic_invariance.push({ base: name, variant: i + 1, pass: ok, observed: got });
    if (!ok) failures++;
  }
}

const collapsedUnsafe = fixtures.negative_controls.collapsed_objects.filter(naiveCollapsed).map((x) => x.id);
const transitiveUnsafe = naiveTransitive(fixtures.negative_controls.transitive_chain);
const qNoMandate = materializeRc3aCase(fixtures.envelope_cases.find((x) => x.id === 'N01-qualified-no-mandate'));
const credentialUnsafe = naiveCredentialOnly(qNoMandate);
results.negative_controls = {
  collapsed_authority_unsafe_permits: collapsedUnsafe,
  transitive_inheritance_unsafe_downstream: transitiveUnsafe,
  credential_only_unsafe_permit: credentialUnsafe,
  intended_direction: collapsedUnsafe.length > 0 && transitiveUnsafe.length > 0 && credentialUnsafe === true
};
if (!results.negative_controls.intended_direction) failures++;

const n13 = results.inherited_envelope.find((x) => x.id === 'N13-supported-does-not-cite');
const n14 = results.inherited_envelope.find((x) => x.id === 'N14-decision-does-not-execute');
results.key_counterexamples = { n13, n14 };

const commonSource = [validateAuthorityBasis, basisReferenceCheck, validateEnvelope].map((f) => f.toString()).join('\n');
const forbiddenSemanticTokens = ['.result', 'reported_verdict', '.confidence', 'execution_report'];
const semanticTokenHits = forbiddenSemanticTokens.filter((token) => commonSource.includes(token));
if (semanticTokenHits.length) failures++;

results.summary = {
  scientific_failures: failures,
  inherited_envelope_cases: results.inherited_envelope.length,
  direct_basis_attack_cases: results.direct_basis_attacks.length,
  propagation_cases: results.propagation.length,
  delegation_cases: results.delegation.length,
  historical_cases: results.historical.length,
  semantic_invariance_cases: results.semantic_invariance.length,
  semantic_token_hits_in_common_validator: semanticTokenHits,
  negative_controls_failed_safely: results.negative_controls.intended_direction,
  n13_reason: n13?.observed_reason || null,
  n14_reason: n14?.observed_reason || null,
  terminal_signal: failures === 0 ? 'CANDIDATE_SURVIVED_RC3B' : 'CANDIDATE_FAILED_RC3B'
};

fs.writeFileSync(path.join(rc3bDir, 'RESULTS.json'), JSON.stringify(results, null, 2) + '\n');
console.log(JSON.stringify(results.summary, null, 2));
for (const group of ['inherited_envelope', 'direct_basis_attacks', 'propagation', 'delegation', 'historical', 'semantic_invariance']) {
  for (const r of results[group].filter((x) => !x.pass)) console.log(`${group.toUpperCase()}_FAILURE`, JSON.stringify(r));
}
process.exitCode = failures === 0 ? 0 : 1;
