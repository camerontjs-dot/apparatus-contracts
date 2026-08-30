# RC3B Authority-Basis Compatibility Matrix — Hardening Preregistration

## Purpose

The first RC3B hosted execution passed the frozen hand-selected basis attacks. Before terminal disposition, run a broader compatibility matrix without changing the RC3B candidate specification, registry, inherited RC3A cases, or direct attack cases.

This hardening is intended to detect accidental overlap among otherwise legitimate authority-conferring basis records.

## Frozen candidate remains unchanged

- RC3B candidate freeze: `e16dc38b4b99ce854280bacb6a953506007a4a26`
- basis spec blob: `63c952c9c28f1be2173e69c79976c7dfe5880c10`
- registry blob: `76ea333ee0460d9614e9899edb69e6865e48eccb`
- direct attack blob: `c726fb0ef914a850620e545131a70d427f4027bd`
- inherited RC3A case blob: `85bc7805d02a04c5a10b48b43a5f5a89f4e2f32a`

No candidate field or authority record may be changed for this hardening pass.

## Matrix

For each of the nine positive RC3A baseline envelopes, replace only its authority-conferring grant/policy reference with every frozen authority-conferring record in the RC3B registry.

The only allowed accepting basis for each baseline is:

- `source_access_ok` -> `grant:source-read`
- `evidence_admission_ok` -> `policy:evidence-admission`
- `assessment_ok` -> `policy:cal-assessment`
- `numeric_ok` -> `grant:numeric-validation`
- `source_boundary_ok` -> `policy:source-boundary`
- `decision_ok` -> `policy:decision-v1`
- `citation_ok` -> `grant:citation-use`
- `task_ok` -> `grant:task-dispatch`
- `verify_ok` -> `grant:verify`

Every other frozen grant/policy record must be rejected.

Supporting artifact references already present on citation/task envelopes remain unchanged and may not satisfy the authority requirement.

## Additional reference-type mutation

For each canonical accepting basis, replace only the envelope reference `type` with each other authority-conferring type while preserving its ID. Every mismatched type must be rejected as `authority_basis_type_mismatch`.

## Acceptance

- zero false accepts across the full basis compatibility matrix;
- zero false rejects for the nine canonical matches;
- all type-only mutations rejected;
- exact RC3B candidate/registry/case hashes verified before execution;
- original RC3B validator suite still passes unchanged in the same hosted run.

A failure is scientific evidence against the frozen RC3B candidate. Do not widen or rewrite the frozen registry/spec under this RC3B freeze to make the matrix pass.
