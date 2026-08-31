#!/usr/bin/env node
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';
import path from 'node:path';

const root = process.cwd();
const p = (...xs) => path.join(root, ...xs);
const read = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));
const blob = (file) => execFileSync('git', ['hash-object', file], {encoding:'utf8'}).trim();

const sources = {
  rc3a: {
    path: p('docs/research/contract-e/rc3a-authority-warrant-spec/SPEC-CANDIDATE.json'),
    blob: '9c1090335d87eb5e4885a755542923b453c45317'
  },
  shapes: {
    path: p('docs/research/contract-e/rc3a-authority-warrant-spec/SPEC-SHAPES.json'),
    blob: 'c3f293430ae6ddb87523d83ea6e5380b8b832136'
  },
  participant: {
    path: p('docs/research/contract-e/rc3a-authority-warrant-spec/SPEC-PARTICIPANT-BOUNDARY.json'),
    blob: '8b1d292a240300388949d502e7b656e7a23a0b8e'
  },
  basis: {
    path: p('docs/research/contract-e/rc3b-authority-basis-binding/BASIS-BINDING-SPEC.json'),
    blob: '63c952c9c28f1be2173e69c79976c7dfe5880c10'
  },
  rc3c: {
    path: p('docs/research/contract-e/rc3c-native-wire-currentness/RC3C-SPEC.json'),
    blob: 'f05feac88128fd693cca2fb25a0b2951654377eb'
  },
  rc3d: {
    path: p('docs/research/contract-e/rc3d-consumer-request-surface/RC3D-INTERFACE-SPEC.json'),
    blob: '61f46b09d391e7da4aed2491e428ec2ed226fe93'
  }
};

for (const [name, src] of Object.entries(sources)) {
  const actual = blob(src.path);
  if (actual !== src.blob) throw new Error(`${name} blob mismatch: ${actual} != ${src.blob}`);
  src.json = read(src.path);
}

const A = sources.rc3a.json;
const S = sources.shapes.json;
const P = sources.participant.json;
const B = sources.basis.json;
const C = sources.rc3c.json;
const D = sources.rc3d.json;

const unique = (xs) => [...new Set(xs)];

const resolved = {
  schema: 'contract-e-resolved-semantic-view-v1-research',
  status: 'research-only-resolved-view-not-semantic-amendment',
  purpose: 'single-document authority for interpretation-only semantic recoverability testing',
  source_blobs: Object.fromEntries(Object.entries(sources).map(([k,v]) => [k, v.blob])),
  resolution_policy: {
    deterministic_view_only: true,
    later_amendments_govern_only_their_declared_scope: true,
    no_hidden_evaluator_rules_imported: true,
    no_prior_implementation_behavior_imported: true,
    underdetermined_points_remain_underdetermined: true
  },
  effective_contract: {
    core_non_implications_and_fail_closed_rules: A.normative_rules,
    common_envelope: {
      required_fields: unique([...A.common_envelope.required, ...P.common_envelope_additional_required, 'competence']),
      subject_required: A.common_envelope.subject_required,
      target_required: A.common_envelope.target_required,
      jurisdiction_required: A.common_envelope.jurisdiction_required,
      authority_basis_entry_required: A.common_envelope.authority_basis_entry_required,
      canonical_wire: C.canonical_wire.common_envelope,
      participant_rules: P.rules,
      warrant_field_cardinality: 'UNDERDETERMINED_BY_SOURCE_SET'
    },
    authority_domains: A.authority_domains,
    participant_declarations: A.participant_declarations,
    domain_basis_requirements: S.domain_basis_requirements,
    qualification: {
      semantic_shape: S.qualification_shape,
      canonical_wire: C.canonical_wire.Qualification
    },
    warrant: {
      semantic_shape: S.warrant_shape,
      warrant_types: A.warrant_types,
      envelope_field_cardinality: 'UNDERDETERMINED_BY_SOURCE_SET'
    },
    authority_basis: {
      authority_reference: B.authority_reference,
      resolved_basis_record: B.resolved_basis_record,
      canonical_wire_reference: C.canonical_wire.AuthorityReference,
      canonical_wire_resolved_record: C.canonical_wire.ResolvedBasisRecord,
      matching_rules: B.matching_rules,
      ordering: B.ordering,
      non_implications: B.non_implications,
      registry_resolution_of_nonconferring_supporting_artifacts: 'UNDERDETERMINED_BY_SOURCE_SET'
    },
    currentness: C.currentness,
    propagation: {
      core: A.propagation,
      shape: S.propagation_shape,
      canonical_interface: D.PropagationRequest,
      default_authority_propagation: C.unchanged_invariants.default_authority_propagation
    },
    delegation: {
      inherited_semantics: S.delegation_shape,
      canonical_wire: C.canonical_wire.Delegation,
      parent_authority_record: D.ParentAuthorityRecord,
      child: D.DelegationChild,
      request: D.delegation_request
    },
    historical_authority: {
      inherited: A.historical_validity,
      record_shape: S.historical_record_shape,
      request: D.HistoricalRequest,
      later_revocation_rewrites_history: D.unchanged_invariants.historical_validity_rewritten_by_later_revocation
    },
    result_payload: S.result_shape,
    evaluation_interface: {
      EvaluationRequest: D.EvaluationRequest,
      envelope_request: D.envelope_request,
      RegistryDocument: D.RegistryDocument,
      consumer_requirements: D.consumer_requirements,
      fixture_materialization_boundary: D.fixture_materialization_boundary
    },
    reason_semantics: {
      rc3b_basis_precedence: B.ordering.reason_precedence,
      rc3c: C.reason_contract,
      rc3c_malformed_wire_reasons: C.malformed_wire_reasons,
      rc3d_interface: D.interface_reason_contract
    }
  },
  explicit_open_normative_questions: [
    {
      id: 'OPEN-WARRANT-CARDINALITY',
      question: 'Is the envelope-level warrant field exactly one Warrant object, an array of Warrant objects, or another cardinality?',
      status: 'UNDERDETERMINED_BY_SOURCE_SET',
      evidence: [
        'SPEC-SHAPES.json#/warrant_shape defines Warrant structure but not envelope cardinality',
        'RC3C-SPEC.json#/canonical_wire does not freeze warrant cardinality'
      ]
    },
    {
      id: 'OPEN-SUPPORTING-ARTIFACT-RESOLUTION',
      question: 'Must a non-authority-conferring supporting artifact reference present in the broader basis chain resolve through RegistryDocument.records?',
      status: 'UNDERDETERMINED_BY_SOURCE_SET',
      evidence: [
        'BASIS-BINDING-SPEC.json#/authority_reference/authority_conferring_types lists grant, policy, delegation',
        'BASIS-BINDING-SPEC.json#/non_implications states supporting artifacts may be part of the basis chain without satisfying the authority requirement',
        'No source blob explicitly states the registry-resolution obligation for non-conferring supporting-artifact references'
      ]
    }
  ],
  provenance_index: {
    '/effective_contract/core_non_implications_and_fail_closed_rules': ['rc3a#/normative_rules'],
    '/effective_contract/common_envelope': ['rc3a#/common_envelope','participant#/common_envelope_additional_required','participant#/rules','rc3c#/canonical_wire/common_envelope'],
    '/effective_contract/authority_domains': ['rc3a#/authority_domains'],
    '/effective_contract/participant_declarations': ['rc3a#/participant_declarations'],
    '/effective_contract/domain_basis_requirements': ['shapes#/domain_basis_requirements'],
    '/effective_contract/qualification': ['shapes#/qualification_shape','rc3c#/canonical_wire/Qualification'],
    '/effective_contract/warrant': ['shapes#/warrant_shape','rc3a#/warrant_types'],
    '/effective_contract/authority_basis': ['basis#/authority_reference','basis#/resolved_basis_record','basis#/matching_rules','basis#/ordering','basis#/non_implications','rc3c#/canonical_wire/AuthorityReference','rc3c#/canonical_wire/ResolvedBasisRecord'],
    '/effective_contract/currentness': ['rc3c#/currentness'],
    '/effective_contract/propagation': ['rc3a#/propagation','shapes#/propagation_shape','rc3d#/PropagationRequest'],
    '/effective_contract/delegation': ['shapes#/delegation_shape','rc3c#/canonical_wire/Delegation','rc3d#/ParentAuthorityRecord','rc3d#/DelegationChild','rc3d#/delegation_request'],
    '/effective_contract/historical_authority': ['rc3a#/historical_validity','shapes#/historical_record_shape','rc3d#/HistoricalRequest'],
    '/effective_contract/result_payload': ['shapes#/result_shape'],
    '/effective_contract/evaluation_interface': ['rc3d#/EvaluationRequest','rc3d#/envelope_request','rc3d#/RegistryDocument','rc3d#/consumer_requirements','rc3d#/fixture_materialization_boundary'],
    '/effective_contract/reason_semantics': ['basis#/ordering/reason_precedence','rc3c#/reason_contract','rc3c#/malformed_wire_reasons','rc3d#/interface_reason_contract']
  }
};

const out = process.argv[2] ?? p('docs/research/contract-e/semantic-recoverability-audit/RESOLVED-CONTRACT.json');
fs.writeFileSync(out, JSON.stringify(resolved, null, 2) + '\n');
console.log(out);
