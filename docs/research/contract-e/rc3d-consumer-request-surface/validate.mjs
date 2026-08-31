import fs from 'node:fs';
import path from 'node:path';

const dir = process.argv[2] || 'docs/research/contract-e/rc3d-consumer-request-surface';
const rc3aDir = path.resolve(dir, '../rc3a-authority-warrant-spec');
const rc3bDir = path.resolve(dir, '../rc3b-authority-basis-binding');
const rc3cDir = path.resolve(dir, '../rc3c-native-wire-currentness');
const load = (p) => JSON.parse(fs.readFileSync(p, 'utf8'));

const spec = load(path.join(rc3aDir, 'SPEC-CANDIDATE.json'));
const shapes = load(path.join(rc3aDir, 'SPEC-SHAPES.json'));
const participantBoundary = load(path.join(rc3aDir, 'SPEC-PARTICIPANT-BOUNDARY.json'));
const inherited = load(path.join(rc3aDir, 'FROZEN-CASES.json'));
const basisSpec = load(path.join(rc3bDir, 'BASIS-BINDING-SPEC.json'));
const registryDoc = load(path.join(rc3bDir, 'AUTHORITY-BASIS-REGISTRY.json'));
const rc3c = load(path.join(rc3cDir, 'RC3C-SPEC.json'));
const rc3cCases = load(path.join(rc3cDir, 'FROZEN-CASES.json'));
const interfaceSpec = load(path.join(dir, 'RC3D-INTERFACE-SPEC.json'));
const materializerSpec = load(path.join(dir, 'VECTOR-MATERIALIZATION-SPEC.json'));
const cases = load(path.join(dir, 'FROZEN-CASES.json'));

const clone = (x) => JSON.parse(JSON.stringify(x));
const ACCEPT = (extra = {}) => ({ decision: 'accept', reason: null, ...extra });
const REJECT = (reason, extra = {}) => ({ decision: 'reject', reason, ...extra });
const MODES = new Set(['new_exercise', 'historical_inspection']);
const PROP_MODES = new Set(spec.common_envelope.propagation_modes);
const IDENTITY_FIELDS = new Set(spec.propagation.identity_provenance_fields);
const NEVER_IMPLICIT = new Set(spec.propagation.never_implicit);
const REESTABLISH = new Set(['decision_mandate', 'task_dispatch']);
const conferringTypes = new Set(basisSpec.authority_reference.authority_conferring_types);
const basisPrecedence = basisSpec.ordering.reason_precedence;
const parentRequired = interfaceSpec.ParentAuthorityRecord.required;
const childRequired = interfaceSpec.DelegationChild.required;
const historicalRequired = shapes.historical_record_shape.required;

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

function isStringArray(v, min = 0) {
  return Array.isArray(v) && v.length >= min && v.every((x) => typeof x === 'string');
}

function validDate(v) {
  return typeof v === 'string' && Number.isFinite(new Date(v).getTime());
}

function validateRegistryDocument(doc) {
  if (!doc || typeof doc !== 'object' || Array.isArray(doc)) return REJECT('malformed_registry_document');
  if (typeof doc.schema !== 'string' || !doc.schema.length) return REJECT('malformed_registry_document');
  if (!doc.records || typeof doc.records !== 'object' || Array.isArray(doc.records)) return REJECT('malformed_registry_document');
  const required = basisSpec.resolved_basis_record.required;
  for (const [key, record] of Object.entries(doc.records)) {
    if (!record || typeof record !== 'object' || Array.isArray(record)) return REJECT('malformed_registry_document');
    if (record.id !== key) return REJECT('malformed_registry_document');
    if (required.some((field) => !(field in record))) return REJECT('malformed_registry_document');
    for (const field of ['subject_ids', 'operations', 'scopes', 'target_classes']) {
      if (!isStringArray(record[field])) return REJECT('malformed_registry_document');
    }
    if ('target_ids' in record && !isStringArray(record.target_ids)) return REJECT('malformed_registry_document');
    if (typeof record.current !== 'boolean') return REJECT('malformed_registry_document');
    if (!validDate(record.valid_from) || !validDate(record.valid_until)) return REJECT('malformed_registry_document');
    if ('revoked_at' in record && record.revoked_at != null && !validDate(record.revoked_at)) return REJECT('malformed_registry_document');
  }
  return ACCEPT({ records: doc.records });
}

function wireCheckEnvelope(e) {
  if (!Array.isArray(e?.authority_basis)) return REJECT('malformed_authority_basis_shape');
  if (!Array.isArray(e?.competence)) return REJECT('malformed_competence_shape');
  if (typeof e?.jurisdiction?.scope !== 'string') return REJECT('malformed_jurisdiction_scope_shape');
  for (const q of e.competence) if (typeof q?.scope !== 'string') return REJECT('malformed_qualification_scope_shape');
  return ACCEPT();
}

function basisReferenceCheck(ref, e, records, mode) {
  const record = records[ref.id];
  if (!record) return REJECT('unresolvable_authority_basis');
  if (ref.type !== record.type) return REJECT('authority_basis_type_mismatch');
  if (mode === 'new_exercise') {
    if (ref.current !== true || record.current !== true) return REJECT('authority_basis_not_current');
    const t = new Date(e.evaluated_at);
    if (record.revoked_at && t >= new Date(record.revoked_at)) return REJECT('authority_basis_not_current');
    if (!(t >= new Date(record.valid_from) && t <= new Date(record.valid_until))) return REJECT('authority_basis_outside_validity_interval');
  }
  if (!record.subject_ids.includes(e.subject.id)) return REJECT('authority_basis_subject_mismatch');
  if (record.authority_domain !== e.authority_domain) return REJECT('authority_basis_domain_mismatch');
  if (!record.operations.includes(e.operation)) return REJECT('authority_basis_operation_mismatch');
  if (!record.scopes.includes(e.jurisdiction.scope)) return REJECT('authority_basis_scope_mismatch');
  if (!record.target_classes.includes(e.target.class)) return REJECT('authority_basis_target_class_mismatch');
  if (Array.isArray(record.target_ids) && record.target_ids.length && !record.target_ids.includes(e.target.id)) return REJECT('authority_basis_target_id_mismatch');
  return ACCEPT({ record });
}

function validateAuthorityBasis(e, records, mode) {
  const req = shapes.domain_basis_requirements[e.authority_domain];
  if (!req) return REJECT('unknown_authority_domain');
  const refs = e.authority_basis;
  const candidates = refs.filter((r) => conferringTypes.has(r.type) && req.any_of.includes(r.type));
  const wrongDomainType = refs.filter((r) => conferringTypes.has(r.type) && !req.any_of.includes(r.type));
  const considered = candidates.length ? candidates : wrongDomainType;
  if (!considered.length) return REJECT('missing_domain_authority_basis');
  const outcomes = considered.map((ref) => basisReferenceCheck(ref, e, records, mode));
  const success = outcomes.find((o) => o.decision === 'accept');
  if (success) return success;
  const reasons = outcomes.map((o) => o.reason);
  for (const r of basisPrecedence) if (reasons.includes(r)) return REJECT(r);
  return REJECT(reasons[0] || 'missing_domain_authority_basis');
}

function validateEnvelope(e, registry, mode) {
  if (!MODES.has(mode)) return REJECT('unknown_evaluation_mode');
  const reg = validateRegistryDocument(registry);
  if (reg.decision !== 'accept') return reg;
  const wire = wireCheckEnvelope(e);
  if (wire.decision !== 'accept') return wire;
  if (Object.prototype.hasOwnProperty.call(e, 'authorized') && spec.normative_rules.generic_authorized_boolean_forbidden) return REJECT('generic_authorized_forbidden');
  const required = [...spec.common_envelope.required, ...participantBoundary.common_envelope_additional_required, 'competence'];
  for (const field of required) if (!(field in e)) return REJECT('missing_required_field');
  if (!e.subject || spec.common_envelope.subject_required.some((f) => !(f in e.subject))) return REJECT('missing_required_field');
  if (!e.target || spec.common_envelope.target_required.some((f) => !(f in e.target))) return REJECT('missing_required_field');
  if (!e.jurisdiction || spec.common_envelope.jurisdiction_required.some((f) => !(f in e.jurisdiction))) return REJECT('missing_required_field');
  if (!Array.isArray(e.non_implications) || !e.non_implications.every((x) => typeof x === 'string')) return REJECT('missing_required_field');
  if (!validDate(e.evaluated_at)) return REJECT('missing_required_field');
  const domain = spec.authority_domains[e.authority_domain];
  if (!domain) return REJECT('unknown_authority_domain');
  if (!domain.operations.includes(e.operation)) return REJECT('domain_operation_mismatch');
  const participant = spec.participant_declarations[e.participant];
  if (!participant) return REJECT('unknown_participant');
  if (!participant.accepted_domains.includes(e.authority_domain)) return REJECT('participant_domain_out_of_scope');
  if (!participant.accepted_operations.includes(e.operation)) return REJECT('participant_operation_out_of_scope');
  if (e.jurisdiction.applicable !== true) return REJECT('jurisdiction_inapplicable');
  if (e.jurisdiction.current !== true) return REJECT('jurisdiction_not_current');
  const basis = validateAuthorityBasis(e, reg.records, mode);
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
    if (w.applicable !== true) return REJECT('warrant_inapplicable');
    if (w.current !== true) return REJECT('warrant_not_current');
    if (w.target_id !== e.target.id) return REJECT('warrant_target_mismatch');
    if (w.target_hash !== e.target.current_hash) return REJECT('warrant_target_hash_mismatch');
  } else if (e.warrant && !domain.warrant_allowed) return REJECT('warrant_not_allowed_for_domain');
  return ACCEPT();
}

function validatePropagation(request) {
  if (!request || typeof request !== 'object' || Array.isArray(request)) return REJECT('malformed_propagation_request');
  if ('requested_fields' in request) return REJECT('malformed_propagation_request');
  const mode = request.mode;
  if (!PROP_MODES.has(mode)) return REJECT('unknown_propagation_mode');
  if (mode === 'explicit' && !('fields' in request)) return REJECT('malformed_propagation_request');
  const fields = 'fields' in request ? request.fields : [];
  if (!isStringArray(fields)) return REJECT('malformed_propagation_request');
  if ('separately_reauthorized' in request && typeof request.separately_reauthorized !== 'boolean') return REJECT('malformed_propagation_request');
  const reauthorized = request.separately_reauthorized === true;
  if (mode === 'none') return fields.length ? REJECT('propagation_not_allowed') : ACCEPT();
  if (mode === 'identity_provenance_only') {
    for (const field of fields) {
      if (!IDENTITY_FIELDS.has(field)) {
        if (NEVER_IMPLICIT.has(field)) return REJECT('forbidden_authority_propagation');
        return REJECT('non_provenance_field_not_propagable');
      }
    }
    return ACCEPT();
  }
  if (reauthorized) return ACCEPT();
  for (const field of fields) if (REESTABLISH.has(field)) return REJECT('authority_requires_reestablishment');
  for (const field of fields) if (NEVER_IMPLICIT.has(field)) return REJECT('forbidden_authority_propagation');
  return ACCEPT();
}

function parentShape(parent) {
  if (!parent || typeof parent !== 'object' || Array.isArray(parent)) return REJECT('missing_required_field');
  if (parentRequired.some((f) => !(f in parent))) return REJECT('missing_required_field');
  if (!isStringArray(parent.operations, 1)) return REJECT('malformed_delegation_operations_shape');
  if (!isStringArray(parent.scope, 1)) return REJECT('malformed_delegation_scope_shape');
  if (typeof parent.current !== 'boolean') return REJECT('missing_required_field');
  if ('valid_until' in parent && parent.valid_until != null && !validDate(parent.valid_until)) return REJECT('missing_required_field');
  return ACCEPT();
}

function childShape(child) {
  if (!child || typeof child !== 'object' || Array.isArray(child)) return REJECT('missing_required_field');
  if (childRequired.some((f) => !(f in child))) return REJECT('missing_required_field');
  if (!isStringArray(child.operations, 1)) return REJECT('malformed_delegation_operations_shape');
  if (!isStringArray(child.scope, 1)) return REJECT('malformed_delegation_scope_shape');
  if (typeof child.current !== 'boolean') return REJECT('missing_required_field');
  if ('valid_until' in child && child.valid_until != null && !validDate(child.valid_until)) return REJECT('missing_required_field');
  return ACCEPT();
}

function validateDelegation(parent, child, mode) {
  if (!MODES.has(mode)) return REJECT('unknown_evaluation_mode');
  const pshape = parentShape(parent); if (pshape.decision !== 'accept') return pshape;
  const cshape = childShape(child); if (cshape.decision !== 'accept') return cshape;
  if (child.parent_authority_id !== parent.id) return REJECT('delegation_parent_mismatch');
  if (child.authority_domain !== parent.authority_domain) return REJECT('delegation_domain_amplification');
  if (mode === 'new_exercise' && (parent.current !== true || child.current !== true)) return REJECT('delegation_not_current');
  if (child.operations.some((op) => !parent.operations.includes(op))) return REJECT('delegation_operation_amplification');
  if (child.scope.some((s) => !parent.scope.includes(s))) return REJECT('delegation_scope_amplification');
  if (parent.valid_until) {
    if (!child.valid_until || new Date(child.valid_until) > new Date(parent.valid_until)) return REJECT('delegation_expiry_amplification');
  }
  return ACCEPT();
}

function validateHistorical(record, mode) {
  if (!MODES.has(mode)) return REJECT('unknown_evaluation_mode');
  if (!record || typeof record !== 'object' || Array.isArray(record)) return REJECT('missing_required_field');
  if (historicalRequired.some((f) => !(f in record))) return REJECT('missing_required_field');
  if (mode === 'historical_inspection') return record.authority_was_valid_at_time === true ? ACCEPT() : REJECT('not_valid_at_time');
  return REJECT('authority_basis_not_current');
}

function evaluate(request) {
  if (!request || typeof request !== 'object' || Array.isArray(request)) return REJECT('unknown_evaluation_kind');
  const kind = request.kind;
  if (!interfaceSpec.EvaluationRequest.kind.enum.includes(kind)) return REJECT('unknown_evaluation_kind');
  if (kind === 'envelope') return validateEnvelope(request.envelope, request.registry, request.mode);
  if (kind === 'propagation') return validatePropagation(request.request);
  if (kind === 'delegation') return validateDelegation(request.parent, request.child, request.mode);
  if (kind === 'historical') return validateHistorical(request.record, request.mode);
  return REJECT('unknown_evaluation_kind');
}

function materializeEnvelopeCase(c, registry = registryDoc) {
  const e = clone(inherited.baselines[c.base]);
  if (c.set) Object.assign(e, clone(c.set));
  if (c.set_path) for (const [p, v] of Object.entries(c.set_path)) setPath(e, p, v);
  if (c.remove) for (const p of c.remove) deletePath(e, p);
  if (c.remove_authority_basis_types) e.authority_basis = (e.authority_basis || []).filter((b) => !c.remove_authority_basis_types.includes(b.type));
  if (c.replace_authority_reference) {
    const { old_id, new_ref } = c.replace_authority_reference;
    const idx = e.authority_basis.findIndex((b) => b.id === old_id);
    if (idx < 0) throw new Error(`cannot find basis ${old_id}`);
    e.authority_basis[idx] = clone(new_ref);
  }
  if (c.replace_path_with_first_item) {
    const value = c.replace_path_with_first_item.split('.').reduce((cur, p) => cur[/^\d+$/.test(p) ? Number(p) : p], e);
    setPath(e, c.replace_path_with_first_item, clone(value[0]));
  }
  const localRegistry = clone(registry);
  if (c.record_override) Object.assign(localRegistry.records[c.record_override.id], clone(c.record_override.set));
  return { kind: 'envelope', envelope: e, registry: localRegistry, mode: 'new_exercise' };
}

function materializePropagationCase(c) {
  return { kind: 'propagation', request: { mode: c.mode, fields: clone(c.requested_fields || []) } };
}

function materializeDelegationCase(c) {
  return { kind: 'delegation', parent: clone(c.parent), child: clone(c.child), mode: 'new_exercise' };
}

function materializeHistoricalCase(c) {
  const map = materializerSpec.rules.historical_case.mode_mapping;
  if (!(c.mode in map)) throw new Error(`unknown fixture historical mode ${c.mode}`);
  return { kind: 'historical', record: clone(c.historical_record), registry: clone(registryDoc), mode: map[c.mode] };
}

function findEnvelopeCase(id) { const c = inherited.envelope_cases.find((x) => x.id === id); if (!c) throw new Error(`missing envelope ${id}`); return c; }
function findPropagationCase(id) { const c = inherited.propagation_cases.find((x) => x.id === id); if (!c) throw new Error(`missing propagation ${id}`); return c; }
function findDelegationCase(id) { const c = inherited.delegation_cases.find((x) => x.id === id); if (!c) throw new Error(`missing delegation ${id}`); return c; }
function findHistoricalCase(id) { const c = inherited.historical_cases.find((x) => x.id === id); if (!c) throw new Error(`missing historical ${id}`); return c; }

const results = {
  inherited_materialized: { envelope: [], propagation: [], delegation: [], historical: [] },
  rc3c_materialized: { currentness: [], wire: [], delegation: [], reasons: [], semantic: [] },
  rc3d_interface: [],
  materializer_assertions: [],
  summary: {}
};
let failures = 0;

function record(group, id, expected, got, expectedReason = null, reasonNormative = false) {
  const outcomeOk = got.decision === expected;
  const reasonOk = !reasonNormative || expected === 'accept' || got.reason === expectedReason;
  const pass = outcomeOk && reasonOk;
  group.push({ id, expected, expected_reason: expectedReason, observed: got.decision, observed_reason: got.reason, reason_normative: reasonNormative, pass });
  if (!pass) failures++;
}

for (const c of inherited.envelope_cases) record(results.inherited_materialized.envelope, c.id, c.expected, evaluate(materializeEnvelopeCase(c)), c.reason || null, false);
for (const c of inherited.propagation_cases) record(results.inherited_materialized.propagation, c.id, c.expected, evaluate(materializePropagationCase(c)), c.reason || null, false);
for (const c of inherited.delegation_cases) record(results.inherited_materialized.delegation, c.id, c.expected, evaluate(materializeDelegationCase(c)), c.reason || null, false);
for (const c of inherited.historical_cases) record(results.inherited_materialized.historical, c.id, c.expected, evaluate(materializeHistoricalCase(c)), c.reason || null, false);

for (const c of rc3cCases.currentness_cases) record(results.rc3c_materialized.currentness, c.id, c.expected, evaluate(materializeEnvelopeCase(c)), c.reason || null, true);
for (const c of rc3cCases.wire_cases) record(results.rc3c_materialized.wire, c.id, c.expected, evaluate(materializeEnvelopeCase(c)), c.reason || null, true);
for (const c of rc3cCases.delegation_wire_cases) {
  const base = clone(findDelegationCase(c.source_case));
  if (c.set_path) for (const [p, v] of Object.entries(c.set_path)) setPath(base, p, v);
  record(results.rc3c_materialized.delegation, c.id, c.expected, evaluate(materializeDelegationCase(base)), c.reason || null, true);
}
for (const c of rc3cCases.reason_cases) {
  let req;
  if (c.source_envelope_case) req = materializeEnvelopeCase(findEnvelopeCase(c.source_envelope_case));
  else if (c.source_propagation_case) req = materializePropagationCase(findPropagationCase(c.source_propagation_case));
  else throw new Error(`reason case lacks source ${c.id}`);
  record(results.rc3c_materialized.reasons, c.id, c.expected, evaluate(req), c.reason, true);
}
for (const baseName of rc3cCases.semantic_metamorphic.bases) {
  const base = clone(inherited.baselines[baseName]);
  const reference = evaluate({ kind: 'envelope', envelope: base, registry: clone(registryDoc), mode: 'new_exercise' });
  for (let i = 0; i < rc3cCases.semantic_metamorphic.variants.length; i++) {
    const e = clone(base); e.result = clone(rc3cCases.semantic_metamorphic.variants[i]);
    const got = evaluate({ kind: 'envelope', envelope: e, registry: clone(registryDoc), mode: 'new_exercise' });
    const pass = got.decision === reference.decision && got.reason === reference.reason;
    results.rc3c_materialized.semantic.push({ base: baseName, variant: i + 1, observed: got, pass });
    if (!pass) failures++;
  }
}

for (const c of cases.interface_cases) {
  let req;
  if (c.request) req = clone(c.request);
  else if (c.source_envelope_baseline) {
    const e = clone(inherited.baselines[c.source_envelope_baseline]);
    const registry = clone(registryDoc);
    if (c.registry_mutation?.remove) for (const p of c.registry_mutation.remove) deletePath(registry, p);
    if (c.registry_mutation?.set_path) for (const [p, v] of Object.entries(c.registry_mutation.set_path)) setPath(registry, p, v);
    req = { kind: 'envelope', envelope: e, registry, mode: c.mode };
  } else if (c.source_delegation_case) {
    const d = clone(findDelegationCase(c.source_delegation_case));
    if (c.set_path) for (const [p, v] of Object.entries(c.set_path)) setPath(d, p, v);
    req = materializeDelegationCase(d);
  } else if (c.source_historical_case) {
    const h = clone(findHistoricalCase(c.source_historical_case));
    req = { kind: 'historical', record: h.historical_record, registry: clone(registryDoc), mode: c.mode };
  } else throw new Error(`cannot materialize rc3d case ${c.id}`);
  record(results.rc3d_interface, c.id, c.expected, evaluate(req), c.reason || null, Boolean(c.reason));
}

for (const a of cases.materializer_assertions) {
  let pass = false;
  let observed = null;
  if (a.source_propagation_case) {
    const req = materializePropagationCase(findPropagationCase(a.source_propagation_case));
    observed = evaluate(req); pass = observed.decision === a.expected && 'fields' in req.request && !('requested_fields' in req.request);
  } else if (a.source_delegation_case) {
    const source = findDelegationCase(a.source_delegation_case); const req = materializeDelegationCase(source);
    observed = evaluate(req); pass = observed.decision === a.expected && parentRequired.every((f) => f in req.parent) && !('delegator' in req.parent) && !('delegate' in req.parent) && !('parent_authority_id' in req.parent);
  } else if (a.source_historical_case) {
    const req = materializeHistoricalCase(findHistoricalCase(a.source_historical_case));
    observed = evaluate(req); pass = observed.decision === a.expected && req.mode === 'historical_inspection';
  } else if (a.source_registry) {
    observed = validateRegistryDocument(registryDoc); pass = observed.decision === 'accept' && interfaceSpec.RegistryDocument.comparison_must_not_extract_records_before_consumer_call === true;
  }
  results.materializer_assertions.push({ id: a.id, observed, pass }); if (!pass) failures++;
}

const interfaceShapeChecks = [
  materializerSpec.canonical_interface_blob === '61f46b09d391e7da4aed2491e428ec2ed226fe93',
  interfaceSpec.PropagationRequest.forbidden_native_aliases.includes('requested_fields'),
  interfaceSpec.ParentAuthorityRecord.not_required.includes('delegator'),
  interfaceSpec.HistoricalRequest.fixture_only_tokens.includes('historical_record'),
  interfaceSpec.RegistryDocument.comparison_must_not_extract_records_before_consumer_call === true,
  interfaceSpec.fixture_materialization_boundary.fixture_dsl_is_not_native_consumer_wire === true
];
if (!interfaceShapeChecks.every(Boolean)) failures++;

const semanticChanges = results.rc3c_materialized.semantic.filter((x) => !x.pass).length;
results.summary = {
  inherited_envelope_cases: results.inherited_materialized.envelope.length,
  inherited_propagation_cases: results.inherited_materialized.propagation.length,
  inherited_delegation_cases: results.inherited_materialized.delegation.length,
  inherited_historical_cases: results.inherited_materialized.historical.length,
  rc3c_currentness_cases: results.rc3c_materialized.currentness.length,
  rc3c_wire_cases: results.rc3c_materialized.wire.length,
  rc3c_delegation_cases: results.rc3c_materialized.delegation.length,
  rc3c_reason_cases: results.rc3c_materialized.reasons.length,
  rc3c_semantic_cases: results.rc3c_materialized.semantic.length,
  rc3d_interface_cases: results.rc3d_interface.length,
  materializer_assertions: results.materializer_assertions.length,
  semantic_authority_changes: semanticChanges,
  scientific_failures: failures,
  terminal_signal: failures === 0 ? 'CANDIDATE_SURVIVED_RC3D' : 'CANDIDATE_FAILED_RC3D'
};

fs.writeFileSync(path.join(dir, 'RESULTS.json'), JSON.stringify(results, null, 2) + '\n');
console.log(JSON.stringify(results.summary, null, 2));
for (const [groupName, group] of Object.entries({
  inherited_envelope: results.inherited_materialized.envelope,
  inherited_propagation: results.inherited_materialized.propagation,
  inherited_delegation: results.inherited_materialized.delegation,
  inherited_historical: results.inherited_materialized.historical,
  rc3c_currentness: results.rc3c_materialized.currentness,
  rc3c_wire: results.rc3c_materialized.wire,
  rc3c_delegation: results.rc3c_materialized.delegation,
  rc3c_reasons: results.rc3c_materialized.reasons,
  rc3d_interface: results.rc3d_interface,
  materializer: results.materializer_assertions
})) {
  for (const r of group.filter((x) => !x.pass)) console.log(`${groupName.toUpperCase()}_FAILURE`, JSON.stringify(r));
}
if (failures) process.exitCode = 1;
