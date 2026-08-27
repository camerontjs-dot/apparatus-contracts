#!/usr/bin/env node
// Standalone Consumer B for Contract B RC1 reproducibility.
// No Evidence Bundler or CAL implementation code is imported.

import fs from 'node:fs';
import crypto from 'node:crypto';

const EXPECTED_INPUT = 'sha256:a861eeafe9a360e9280e2d2c092bd2bbcdee6661c55412802be6fecbf8c7b2d7';
const PROFILE = 'contract-b-cal-intake-ledger-rc1';

function canonicalValue(value) {
  if (Array.isArray(value)) return value.map(canonicalValue);
  if (value && typeof value === 'object') {
    const out = {};
    for (const key of Object.keys(value).sort()) out[key] = canonicalValue(value[key]);
    return out;
  }
  if (typeof value === 'number' && !Number.isFinite(value)) throw new Error('non-finite number');
  return value;
}
function canonicalString(value) { return JSON.stringify(canonicalValue(value)); }
function digest(value) { return 'sha256:' + crypto.createHash('sha256').update(Buffer.from(canonicalString(value), 'utf8')).digest('hex'); }
function state(obj, key) {
  if (!Object.prototype.hasOwnProperty.call(obj, key) || obj[key] === null) return {state: 'unknown', value: null};
  return {state: 'known', value: structuredClone(obj[key])};
}
function normFact(f) {
  const p = f.provenance ?? {};
  return {
    fact_id: f.fact_id,
    predicate: f.predicate,
    value: structuredClone(f.value),
    assertion_mode: f.assertion_mode ?? null,
    provenance_passage_id: p.passage_id ?? null,
  };
}
function normAnchors(raw) {
  const arr = (raw ?? []).map(a => ({type: a.type ?? null, value: structuredClone(a.value)}));
  arr.sort((a,b) => {
    const ak = `${String(a.type)}\u0000${canonicalString(a.value)}`;
    const bk = `${String(b.type)}\u0000${canonicalString(b.value)}`;
    return ak < bk ? -1 : ak > bk ? 1 : 0;
  });
  return arr;
}
function normSource(s, semantic=false) {
  const facts = (s.context_facts ?? []).map(normFact).sort((a,b) => a.fact_id.localeCompare(b.fact_id));
  const out = {
    source_id: s.source_id,
    title: s.title ?? null,
    source_type: s.source_type ?? null,
    content_hash: s.content_hash ?? null,
    context_facts: facts,
  };
  if (!semantic) out.source_trust_level = state(s, 'source_trust_level');
  return out;
}
function normPassage(p) {
  return {
    passage_id: p.passage_id,
    source_id: p.source_id ?? null,
    text: p.text ?? null,
    passage_hash: p.passage_hash ?? null,
    anchors: normAnchors(p.anchors ?? []),
  };
}

const args = process.argv.slice(2);
function arg(name) {
  const i = args.indexOf(name);
  if (i < 0 || i + 1 >= args.length) throw new Error(`missing ${name}`);
  return args[i+1];
}
const inputPath = arg('--input');
const outDir = arg('--out');
const v1 = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
if (!v1 || typeof v1 !== 'object' || Array.isArray(v1) || v1.variant !== 'minimal_context') {
  throw new Error('RC1_INTAKE_FAIL: invalid V1 root/variant');
}
const inputHash = digest(v1);
if (inputHash !== EXPECTED_INPUT) throw new Error(`RC1_INTAKE_FAIL: input hash ${inputHash}`);

const links = v1.links.map(x => structuredClone(x));
const reviewed = links.filter(x => (x.review ?? {}).decision !== 'needs-review');
const accepted = links.filter(x => (x.review ?? {}).decision === 'accepted');
const derived = {candidate: links.length, reviewed: reviewed.length, admitted: accepted.length};
const coverage = structuredClone(v1.coverage);
const stored = {candidate: coverage.candidate_count, reviewed: coverage.reviewed_count, admitted: coverage.admitted_count};
if (canonicalString(stored) !== canonicalString(derived)) throw new Error('RC1_INTAKE_FAIL: stored counts inconsistent');

const claim = structuredClone(v1.claim);
const sources = v1.sources.map(x => structuredClone(x)).sort((a,b) => a.source_id.localeCompare(b.source_id));
const passages = v1.passages.map(x => structuredClone(x)).sort((a,b) => a.passage_id.localeCompare(b.passage_id));

const ledger = {
  profile: PROFILE,
  input_identity: {bundle_id: v1.bundle_id, input_sha256: inputHash},
  claim: {
    claim_id: claim.claim_id,
    claim_text: claim.claim_text,
    claim_form: state(claim, 'claim_form'),
    origin: state(claim, 'origin'),
    atomicity: state(claim, 'atomicity'),
  },
  sources: sources.map(s => normSource(s, false)),
  passages: passages.map(normPassage),
  preparation_history: {
    ledger_complete: true,
    links: links.sort((a,b) => a.link_id.localeCompare(b.link_id)).map(x => ({
      link_id: x.link_id,
      claim_id: x.claim_id,
      passage_id: x.passage_id,
      nomination: structuredClone(x.nomination ?? null),
      review: structuredClone(x.review ?? null),
    })),
    derived_counts: derived,
  },
  aperture: {
    search_scope: structuredClone(coverage.search_scope ?? null),
    outcome: state(coverage, 'outcome'),
    limitations: structuredClone(coverage.limitations ?? []).sort((a,b) => canonicalString(a).localeCompare(canonicalString(b))),
  },
};

const sourceById = new Map(sources.map(s => [s.source_id, s]));
const passageById = new Map(passages.map(p => [p.passage_id, p]));
const admittedPassageIds = accepted.map(x => x.passage_id).sort();
const admittedSourceIds = [...new Set(admittedPassageIds.map(id => passageById.get(id).source_id))].sort();
const semantic = {
  bundle_id: v1.bundle_id,
  claim_id: claim.claim_id,
  claim_text: claim.claim_text,
  admitted_sources: admittedSourceIds.map(id => normSource(sourceById.get(id), true)),
  admitted_passages: admittedPassageIds.map(id => normPassage(passageById.get(id))),
};

fs.mkdirSync(outDir, {recursive: true});
fs.writeFileSync(`${outDir}/consumer_b_ledger.json`, canonicalString(ledger) + '\n', 'utf8');
fs.writeFileSync(`${outDir}/consumer_b_semantic.json`, canonicalString(semantic) + '\n', 'utf8');
const result = {consumer: 'B', input_sha256: inputHash, ledger_sha256: digest(ledger), semantic_sha256: digest(semantic)};
fs.writeFileSync(`${outDir}/consumer_b_result.json`, JSON.stringify(result, null, 2) + '\n', 'utf8');
console.log(JSON.stringify(result));
