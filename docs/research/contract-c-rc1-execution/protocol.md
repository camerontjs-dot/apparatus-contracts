# Contract C RC1 Final Execution Protocol

**Research class:** Draft research experiment. No production behavior, Contract B artifact, or Contract C version is changed by this work.

## Decision supported

Determine whether the RC1 C1 semantic result package is sufficiently expressive and sufficiently minimal to justify a future Contract C promotion program, versus C0 full trace, C2 destination-specific projection, or C3 human report authority.

## Pinned live state used

| Repository / surface | Exact SHA used | Role |
|---|---|---|
| `camerontjs-dot/apparatus-contracts` `main` | `c314e53bd91c0736aa4370a364673b069aceb43e` | locked Contract B 1.2.0 production baseline |
| Apparatus RC1 research branch before execution artifacts | `eb7017710866997a2d4ceb1ed5a71cbdfebe2428` | umbrella preregistration and F1-F7/T1-T15 design |
| `camerontjs-dot/evidence-bundler` `main` | `c8189c31adbab11729c31430c2070126224a2d42` | locked Contract B producer baseline |
| `camerontjs-dot/claim-audit-lab` `main` | `33a928db97316a3652d57df9cafb8ca240305233` | production CAL semantic inventory |
| CAL RC1 research branch | `a1f8b216e3f163bce55867ded07eee0d5b0ebeb7` | producer-side research design note |
| `camerontjs-dot/decision-engine` `main` | `55f108c196ead020b5965c7d4d737464c92bc4a0` | current downstream production baseline |
| Decision Engine RC1 research branch | `2ade117f35bcbae8ca1ce1a85790afa493f8694d` | consumer/runtime architecture audit |

Contract B version is frozen at `1.2.0`. Contract B was not modified.

## Actual CAL implementation evidence inventoried before candidate construction

At CAL production SHA `33a928d...` the execution inspected:

- `src/claim_audit_lab/v1/models.py`: `AuditTrace`, verdict axes, `audit_config_hash`, `library_version`, source-boundary semantics, model revisions;
- `src/claim_audit_lab/v1/evidence_state.py`: explicit `unmeasured | no_evidence | read_silent | support_only | refutation_only | mixed` state;
- `src/claim_audit_lab/v1/decision_model.py`: additive `EvidenceDecisionTrace` separating measurements, eligibility, semantic validity, aperture, retained contributions, decided/abstained disposition, typed reasons, and exact basis IDs;
- `src/claim_audit_lab/models.py`: existing structured `AuditReport` used as a report-rendering precedent.

The synthetic C1 used below is therefore grounded in current CAL concepts, but **is not a claim that production CAL already emits this exact schema**.

## Frozen representation hypotheses

- **C0:** C1 semantic state plus implementation telemetry such as retrieval scores, raw logits, feature ordering, and debug prose.
- **C1:** semantic result package with F1-F7 families.
- **C2:** deliberately thin MainFrame-style projection containing only a subset of fields needed by one consumer.
- **C3:** Markdown human report only, with no hidden machine payload.

## Frozen consumer policies

The policies were made materially different before the final decisive run.

| Policy | Destination decision | CAL-result facts it reads | Destination context kept outside C1 |
|---|---|---|---|
| P1 MainFrame knowledge posture | eligible for operator review / hold / human review / not eligible as written | execution, disposition/verdict, eligibility, semantic validity, aperture, counterevidence, unknowns | whether operator review is required |
| P2 publication/website claim | publishable as written / review-or-narrow / withhold | execution, semantic validity, verdict, retained deciding support, counterevidence, aperture, temporal applicability, unknowns | publication materiality/context |
| P3 SOP requirement conformance | conformance supported / nonconformance supported / indeterminate / not applicable | execution, temporal applicability, eligibility, semantic validity, CAL disposition/verdict | requirement identity and procedural context |
| P4 deviation/investigation readiness | decision ready / further investigation / adverse condition established | execution, counterevidence, unknowns, aperture, semantic validity, temporal applicability, evidence requests | investigation stage/procedural policy |

P3 explicitly treats absent or insufficient evidence as **indeterminate**, not nonconformance. P4 preserves unresolved evidence requests rather than laundering them into a binary finding.

## Freeze identities

- Final fixture bytes: `sha256:fce13ea19b627a9a4a20e44c521ec224188468149b7dfe0f3786758d621f1570`
- Final harness bytes: `sha256:8084646e18c3c4b2776898c0505879b73a38b0fb83cfadb93c0a7de0f750d16a`
- Python: `3.13.5`
- ReportLab: `4.4.9`

The final decisive run was executed only after the fixture/harness corrections described in `apparatus-deviations.md`.

## Acceptance / falsification logic

C1 support required all of the following within the frozen suite:

1. every legitimate C0 policy distinction remains available from C1;
2. same-headline-verdict cases with materially different residual state remain distinguishable;
3. missing material state fails closed rather than becoming a substantive adverse or favorable finding;
4. destination policy can change while C1 bytes remain unchanged;
5. telemetry mutations do not change semantic C1 or legitimate decisions;
6. reports derive deterministically from C1 and do not become a second machine authority;
7. partial execution, no-result, epistemic unknown, failed execution, and recomputation/supersession remain distinguishable;
8. field-family ablation identifies what is necessary rather than retaining fields because current code emits them.

Promotion readiness additionally requires the preregistered independent-consumer and held-out negative-control gates. Those gates were not waived.