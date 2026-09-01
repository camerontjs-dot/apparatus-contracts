from __future__ import annotations

import hashlib


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _basis(subject="cal", domain="semantic", operation="interpret", scope="claim", target_class="claim", **extra):
    out = {
        "subject": subject,
        "domain": domain,
        "operation": operation,
        "scope": scope,
        "target_class": target_class,
        "current": True,
        "valid": True,
    }
    out.update(extra)
    return out


def _obs(rid="o1", producer="source_observer"):
    return {"id": rid, "authority_kind": "observation", "status": "established", "producer_type": producer}


def _meas(rid="m1"):
    return {"id": rid, "authority_kind": "measurement", "status": "established", "producer_type": "language_instrument"}


def _sem(rid="s1", lineage=True):
    r = {"id": rid, "authority_kind": "semantic", "status": "established", "producer_type": "semantic_validator"}
    if lineage:
        r["authority_lineage"] = ["o1", "m1", "semantic-basis"]
    return r


def _comp(rid="c1"):
    return {"id": rid, "authority_kind": "composition", "status": "established", "producer_type": "composition_governor"}


def _decision(rid="d1", lineage=True):
    r = {"id": rid, "authority_kind": "decision", "status": "established", "producer_type": "decision_engine"}
    if lineage:
        r["authority_lineage"] = ["semantic", "decision-basis"]
    return r


def _proposal(pid="p1", dimension="role_binding", atom="inspect(auditor,vessel)", embedding=None):
    return {"id": pid, "dimension": dimension, "atom": atom, "embedding": embedding}


def _case(cid, family, source, proposals, receipts, request, expected, *, conflicts=None, residues=None,
          comparisons=None, reason=None, pair_id=None, pair_expectation=None):
    h = _hash(source)
    request = dict(request)
    request.setdefault("source_hash", h)
    return {
        "id": cid,
        "family": family,
        "raw_source": source,
        "source_hash": h,
        "proposals": proposals,
        "receipts": receipts,
        "conflicts": conflicts or [],
        "residues": residues or [],
        "comparison_receipts": comparisons or [],
        "request": request,
        "expected_allowed": expected,
        "expected_reason": reason,
        "pair_id": pair_id,
        "pair_expectation": pair_expectation,
    }


def _semantic_req(pid="p1", embedding=None, *, claim_level="narrator_fact", preserves=False, basis=None,
                  dependencies=None, promotion_source="independent_semantic_validation", **kw):
    b = basis or _basis(semantic_dimensions=["role_binding"], allowed_embeddings=[] if embedding is None else [embedding])
    req = {
        "authority_kind": "semantic",
        "producer_type": "semantic_validator",
        "subject_id": "claim-1",
        "subject": "cal",
        "domain": "semantic",
        "operation": "interpret",
        "scope": "claim",
        "target_class": "claim",
        "proposal_id": pid,
        "claim_level": claim_level,
        "preserves_embedding": preserves,
        "promotion_source": promotion_source,
        "dependencies": dependencies or ["m1"],
        "basis": b,
    }
    req.update(kw)
    return req


CASES = []

# A. Clean semantic authority controls: exact source preserved; independent basis covers the proposal.
for i, (dimension, atom) in enumerate([
    ("role_binding", "review(auditor,packet)"),
    ("membership", "member(mira,reviewers)"),
    ("quantifier", "all(technicians)"),
    ("permission", "may(dana,approve)"),
    ("temporal", "before(review,release)"),
    ("comparison", "greater(temp_a,temp_b)"),
], 1):
    src = f"Fresh authority control {i}: source explicitly warrants {atom}."
    p = _proposal("p1", dimension, atom, None)
    b = _basis(semantic_dimensions=[dimension], allowed_embeddings=[])
    CASES.append(_case(
        f"SEM-POS-{i:02d}", "semantic_positive", src, [p], [_obs(), _meas()],
        _semantic_req("p1", basis=b), True, reason="semantic_authority_established"
    ))

# B. Embedded semantics are allowed only when the semantic object preserves the embedding.
for i, emb in enumerate(["quantifier", "modality", "permission", "conditional", "attribution", "quantitative", "exception", "negation"], 1):
    src = f"Embedded control {i}: proposition appears under {emb} scope."
    p = _proposal("p1", "role_binding", f"event_{i}", emb)
    b = _basis(semantic_dimensions=["role_binding"], allowed_embeddings=[emb])
    CASES.append(_case(
        f"EMB-POS-{i:02d}", "semantic_positive", src, [p], [_obs(), _meas()],
        _semantic_req("p1", embedding=emb, claim_level="embedded_semantic", preserves=True, basis=b), True,
        reason="semantic_authority_established"
    ))
    CASES.append(_case(
        f"EMB-NEG-{i:02d}", "scope_embedding", src, [p], [_obs(), _meas()],
        _semantic_req("p1", embedding=emb, claim_level="narrator_fact", preserves=False, basis=b), False,
        reason="embedding_scope_laundering"
    ))

# C. Agreement is evidence about measurements, not source truth.
for i in range(1, 5):
    src = f"Agreement trap {i}: two independent readers share the same unsupported reading."
    proposals = [_proposal("p1", "role_binding", f"wrong_atom_{i}"), _proposal("p2", "role_binding", f"wrong_atom_{i}")]
    receipts = [_obs(), _meas("m1"), _meas("m2")]
    req = _semantic_req("p1", dependencies=["m1", "m2"], promotion_source="comparison_agreement")
    CASES.append(_case(f"AGR-NEG-{i:02d}", "agreement", src, proposals, receipts, req, False,
                       comparisons=[{"id": f"cmp{i}", "relation": "EXACT_AGREEMENT"}],
                       reason="agreement_has_no_truth_authority"))

# D. A jurisdiction/coverage disagreement does not invalidate an independently warranted surviving claim.
for i in range(1, 5):
    src = f"Coverage asymmetry {i}: one qualified measurement recovers a warranted claim and another abstains."
    p = _proposal("p1", "membership", f"member_{i}")
    b = _basis(semantic_dimensions=["membership"], allowed_embeddings=[])
    CASES.append(_case(
        f"JUR-POS-{i:02d}", "semantic_positive", src, [p], [_obs(), _meas("m1")],
        _semantic_req("p1", basis=b, dependencies=["m1"]), True,
        comparisons=[{"id": f"jur{i}", "relation": "JURISDICTION_DISAGREEMENT"}],
        reason="semantic_authority_established"
    ))

# E. Relevant unresolved scope conflict blocks promotion; irrelevant residue is preserved but does not block.
for i in range(1, 4):
    src = f"Scope conflict {i}: the attachment of a modifier remains unresolved."
    p = _proposal("p1", "role_binding", f"scope_atom_{i}")
    CASES.append(_case(
        f"RES-NEG-{i:02d}", "scope_embedding", src, [p], [_obs(), _meas()], _semantic_req("p1"), False,
        residues=[{"id": f"r{i}", "status": "unresolved", "relevant": True, "kind": "scope"}],
        reason="relevant_residue_unresolved"
    ))
    CASES.append(_case(
        f"RES-POS-{i:02d}", "semantic_positive", src + " Editorial residue is also present.", [p], [_obs(), _meas()],
        _semantic_req("p1"), True,
        residues=[{"id": f"ir{i}", "status": "unresolved", "relevant": False, "kind": "editorial"}],
        reason="semantic_authority_established"
    ))

# F. Fresh resolution-forgery attacks: naming a residue/conflict id as resolved is not itself resolution authority.
for i in range(1, 4):
    src = f"Forged residue discharge {i}: relevant semantic uncertainty has no resolver receipt."
    p = _proposal("p1", "role_binding", f"forged_residue_atom_{i}")
    CASES.append(_case(
        f"RES-FORGE-{i:02d}", "cross_stage", src, [p], [_obs(), _meas()],
        _semantic_req("p1", resolved_residue_ids=[f"fr{i}"]), False,
        residues=[{"id": f"fr{i}", "status": "unresolved", "relevant": True, "kind": "scope"}],
        reason="resolution_requires_authorized_resolver"
    ))

for i in range(1, 3):
    src = f"Forged conflict discharge {i}: contradictory semantic readings lack an authorized resolution."
    p = _proposal("p1", "role_binding", f"forged_conflict_atom_{i}")
    CASES.append(_case(
        f"CON-FORGE-{i:02d}", "cross_stage", src, [p], [_obs(), _meas()],
        _semantic_req("p1", resolved_conflict_ids=[f"fc{i}"]), False,
        conflicts=[{"id": f"fc{i}", "status": "contested", "relevant": True, "kind": "contradiction"}],
        reason="resolution_requires_authorized_resolver"
    ))

# G. Composition requires established semantic components and an exact composition rule.
for i in range(1, 4):
    src = f"Composition positive {i}: two bounded semantic facts are independently established."
    receipts = [_sem("s1"), _sem("s2")]
    b = _basis(domain="composition", operation="compose", scope="claim", target_class="claim",
               component_dimensions=["role_binding", "temporal"], composition_rule=f"rule-{i}")
    req = {
        "authority_kind": "composition", "producer_type": "composition_governor", "subject_id": "comp-1",
        "subject": "cal", "domain": "composition", "operation": "compose", "scope": "claim", "target_class": "claim",
        "dependencies": ["s1", "s2"], "component_dimensions": ["role_binding", "temporal"], "basis": b,
    }
    CASES.append(_case(f"COMP-POS-{i:02d}", "composition_positive", src, [], receipts, req, True,
                       reason="composition_authority_established"))

for i in range(1, 4):
    src = f"Composition negative {i}: components are established but no rule covers their combination."
    receipts = [_sem("s1"), _sem("s2")]
    b = _basis(domain="composition", operation="compose", scope="claim", target_class="claim",
               component_dimensions=["role_binding", "temporal"])
    req = {
        "authority_kind": "composition", "producer_type": "composition_governor", "subject_id": "comp-1",
        "subject": "cal", "domain": "composition", "operation": "compose", "scope": "claim", "target_class": "claim",
        "dependencies": ["s1", "s2"], "component_dimensions": ["role_binding", "temporal"], "basis": b,
    }
    CASES.append(_case(f"COMP-NEG-{i:02d}", "composition", src, [], receipts, req, False,
                       reason="composition_rule_missing"))

# H. Producer ceilings: a lower-authority producer cannot emit a higher-authority receipt.
for i, (producer, kind) in enumerate([
    ("language_instrument", "semantic"),
    ("comparison_engine", "semantic"),
    ("semantic_validator", "decision"),
    ("decision_engine", "action"),
], 1):
    src = f"Ceiling attack {i}: producer {producer} attempts {kind}."
    req = {"authority_kind": kind, "producer_type": producer, "subject_id": "x", "dependencies": [],
           "subject": "cal", "domain": "semantic", "operation": "interpret", "scope": "claim", "target_class": "claim",
           "basis": _basis()}
    CASES.append(_case(f"CEIL-NEG-{i:02d}", "ceiling", src, [], [], req, False,
                       reason="producer_authority_ceiling"))

# I. Cross-stage lineage attacks: an established-looking receipt without traceable authority lineage must not be trusted.
for i in range(1, 5):
    src = f"Lineage attack {i}: a semantic receipt is marked established but carries no authority lineage."
    forged = _sem("s1", lineage=False)
    b = _basis(domain="decision", operation="decide", scope="claim", target_class="decision")
    req = {
        "authority_kind": "decision", "producer_type": "decision_engine", "subject_id": "decision-1",
        "subject": "cal", "domain": "decision", "operation": "decide", "scope": "claim", "target_class": "decision",
        "dependencies": ["s1"], "basis": b,
    }
    CASES.append(_case(f"LIN-NEG-{i:02d}", "cross_stage", src, [], [forged], req, False,
                       reason="dependency_authority_lineage_missing"))

# J. Valid decision authority and invalid decision->action laundering.
for i in range(1, 4):
    src = f"Decision positive {i}: established semantic authority and matching decision policy."
    b = _basis(domain="decision", operation="decide", scope="claim", target_class="decision")
    req = {
        "authority_kind": "decision", "producer_type": "decision_engine", "subject_id": "decision-1",
        "subject": "cal", "domain": "decision", "operation": "decide", "scope": "claim", "target_class": "decision",
        "dependencies": ["s1"], "basis": b,
    }
    CASES.append(_case(f"DEC-POS-{i:02d}", "decision_positive", src, [], [_sem("s1")], req, True,
                       reason="decision_authority_established"))

for i in range(1, 4):
    src = f"Decision-to-action laundering {i}: a valid decision exists but no execution-domain basis exists."
    b = _basis(domain="action", operation="execute", scope="task", target_class="task")
    req = {
        "authority_kind": "action", "producer_type": "action_authorizer", "subject_id": "task-1",
        "subject": "cal", "domain": "action", "operation": "execute", "scope": "task", "target_class": "task",
        "dependencies": ["d1"], "basis": b,
    }
    CASES.append(_case(f"ACT-NEG-{i:02d}", "decision_action", src, [], [_decision("d1")], req, False,
                       reason="decision_does_not_confer_execution_authority"))

for i in range(1, 3):
    src = f"Action positive {i}: decision exists and a separate current execution basis covers the task."
    b = _basis(domain="action", operation="execute", scope="task", target_class="task", authority_domain="execution")
    req = {
        "authority_kind": "action", "producer_type": "action_authorizer", "subject_id": "task-1",
        "subject": "cal", "domain": "action", "operation": "execute", "scope": "task", "target_class": "task",
        "dependencies": ["d1"], "basis": b,
    }
    CASES.append(_case(f"ACT-POS-{i:02d}", "action_positive", src, [], [_decision("d1")], req, True,
                       reason="action_authority_established"))

# K. Executor reports do not create verification authority; independent outcome observations can be verified.
for i in range(1, 4):
    src = f"Executor-report trap {i}: executor says the action succeeded."
    b = _basis(domain="verification", operation="verify", scope="outcome", target_class="outcome", authority_domain="verification")
    req = {
        "authority_kind": "verification", "producer_type": "outcome_verifier", "subject_id": "outcome-1",
        "subject": "cal", "domain": "verification", "operation": "verify", "scope": "outcome", "target_class": "outcome",
        "dependencies": ["o1"], "basis": b,
    }
    CASES.append(_case(f"VER-NEG-{i:02d}", "execution_verification", src, [], [_obs("o1", producer="executor_reporter")], req, False,
                       reason="executor_report_not_verification_authority"))

for i in range(1, 3):
    src = f"Independent verification {i}: an outcome observer records state independently of the executor."
    b = _basis(domain="verification", operation="verify", scope="outcome", target_class="outcome", authority_domain="verification")
    req = {
        "authority_kind": "verification", "producer_type": "outcome_verifier", "subject_id": "outcome-1",
        "subject": "cal", "domain": "verification", "operation": "verify", "scope": "outcome", "target_class": "outcome",
        "dependencies": ["o1"], "basis": b,
    }
    CASES.append(_case(f"VER-POS-{i:02d}", "verification_positive", src, [], [_obs("o1", producer="source_observer")], req, True,
                       reason="verification_authority_established"))

# L. Contract-E style basis attacks: stale, relabeled, and supporting-artifact substitutions.
for i, mutation in enumerate(["stale", "invalid", "domain_relabel", "supporting_artifact"], 1):
    src = f"Authority basis attack {i}: {mutation}."
    b = _basis(semantic_dimensions=["role_binding"], allowed_embeddings=[])
    if mutation == "stale":
        b["current"] = False
    elif mutation == "invalid":
        b["valid"] = False
    elif mutation == "domain_relabel":
        b["domain"] = "citation"
    elif mutation == "supporting_artifact":
        b["basis_type"] = "supporting_artifact"
        b["authority_conferring"] = False
    p = _proposal("p1", "role_binding", f"basis_atom_{i}")
    req = _semantic_req("p1", basis=b)
    CASES.append(_case(f"BASIS-NEG-{i:02d}", "cross_stage", src, [p], [_obs(), _meas()], req, False,
                       reason="authority_basis_invalid_or_nonconferring"))

# M. Metamorphic same-authority pairs: payload/confidence changes must not change authority outcome.
for i in range(1, 4):
    pid = f"META-SAME-{i}"
    for suffix, payload in [("A", "negative/low-confidence"), ("B", "success/high-confidence")]:
        src = f"Metamorphic payload {i}-{suffix}: {payload}; authority fields are identical."
        p = _proposal("p1", "role_binding", f"meta_atom_{i}")
        b = _basis(semantic_dimensions=["role_binding"], allowed_embeddings=[])
        CASES.append(_case(f"{pid}-{suffix}", "semantic_positive", src, [p], [_obs(), _meas()], _semantic_req("p1", basis=b), True,
                           pair_id=pid, pair_expectation="same", reason="semantic_authority_established"))

# N. Authority-sensitive flip pairs: currentness, domain, and embedding preservation must change outcome.
for i, kind in enumerate(["currentness", "domain", "embedding"], 1):
    pid = f"META-FLIP-{i}"
    if kind == "currentness":
        for suffix, current, expected in [("A", True, True), ("B", False, False)]:
            src = f"Currentness flip {suffix}: only basis currentness differs."
            p = _proposal("p1", "role_binding", "flip_current")
            b = _basis(semantic_dimensions=["role_binding"], allowed_embeddings=[])
            b["current"] = current
            CASES.append(_case(f"{pid}-{suffix}", "cross_stage", src, [p], [_obs(), _meas()], _semantic_req("p1", basis=b), expected,
                               pair_id=pid, pair_expectation="flip"))
    elif kind == "domain":
        for suffix, domain, expected in [("A", "semantic", True), ("B", "citation", False)]:
            src = f"Domain flip {suffix}: only basis domain differs."
            p = _proposal("p1", "role_binding", "flip_domain")
            b = _basis(domain=domain, semantic_dimensions=["role_binding"], allowed_embeddings=[])
            CASES.append(_case(f"{pid}-{suffix}", "cross_stage", src, [p], [_obs(), _meas()], _semantic_req("p1", basis=b), expected,
                               pair_id=pid, pair_expectation="flip"))
    else:
        for suffix, level, preserves, expected in [("A", "embedded_semantic", True, True), ("B", "narrator_fact", False, False)]:
            src = f"Embedding flip {suffix}: only requested semantic level differs."
            p = _proposal("p1", "role_binding", "flip_embedding", "permission")
            b = _basis(semantic_dimensions=["role_binding"], allowed_embeddings=["permission"])
            CASES.append(_case(f"{pid}-{suffix}", "scope_embedding", src, [p], [_obs(), _meas()],
                               _semantic_req("p1", embedding="permission", claim_level=level, preserves=preserves, basis=b), expected,
                               pair_id=pid, pair_expectation="flip"))

# O. Explicit comparison receipts are legal only as measurement-relation authority.
for i, relation in enumerate(["EXACT_AGREEMENT", "SCOPE_ATTACHMENT_DISAGREEMENT", "JURISDICTION_DISAGREEMENT"], 1):
    src = f"Comparison relation {i}: {relation}."
    req = {
        "authority_kind": "comparison", "producer_type": "comparison_engine", "subject_id": f"cmp-{i}",
        "dependencies": ["m1", "m2"], "relation": relation,
    }
    CASES.append(_case(f"CMP-POS-{i:02d}", "comparison_positive", src, [], [_meas("m1"), _meas("m2")], req, True,
                       reason="measurement_relation_established"))

# P. Correct-looking terminal outcome through an invalid action chain still fails.
for i in range(1, 3):
    src = f"Correct-outcome invalid-chain {i}: final task result is correct but action authority basis is absent."
    req = {
        "authority_kind": "action", "producer_type": "action_authorizer", "subject_id": "task-correct",
        "subject": "cal", "domain": "action", "operation": "execute", "scope": "task", "target_class": "task",
        "dependencies": ["d1"], "basis": {}, "terminal_outcome": "correct",
    }
    CASES.append(_case(f"CHAIN-NEG-{i:02d}", "cross_stage", src, [], [_decision("d1")], req, False,
                       reason="correct_outcome_does_not_repair_invalid_authority_chain"))

# Stable identity sentinel. The corpus is intentionally frozen after candidate/evaluator.
CASE_IDS = tuple(c["id"] for c in CASES)
assert len(CASE_IDS) == len(set(CASE_IDS))
assert len(CASES) >= 70
