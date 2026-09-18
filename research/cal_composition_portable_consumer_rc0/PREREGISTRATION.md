# CAL Composition Portable Consumer RC0 — Preregistration

Date: 2026-09-18

Classification: Draft Research / independent cross-repository consumer.

## Producer authority

- repository: `camerontjs-dot/claim-audit-lab`;
- portable-vector PR: #175;
- exact producer head: `6eff362645da14eb49e1e5261c47cd03be5ce29f`;
- exact vectors SHA-256: `11818e585780ff70b5bf00fe519463fb487dba9d191abb7810946ad43afebf39`;
- qualified composition-carrier candidate: `faf2825ee13fe0aea2fa68a520194d847f95f3ab`;
- carrier terminal result: `865bbeb30ae672c290be98f023b3c4711aba22a4`.

## Question

Can an independently written consumer in Apparatus Contracts verify the exact frozen CAL composition vectors without importing CAL code, producer-private Python objects, or producer implementation modules?

## Frozen input

The file `vectors.json` in this directory must be byte-identical to the producer file from CAL PR #175.

The independent consumer must not change expected receipt values or vector bytes to obtain a pass.

## Consumer obligations

For every frozen vector, the consumer must independently:

1. verify the bounded canonicalization profile declaration;
2. recompute `semantic_input_sha256`;
3. recompute `modifier_state_sha256`;
4. recompute `query_sha256`;
5. reconstruct the exact receipt material;
6. recompute `receipt_id`;
7. require exact equality with the frozen expected receipt;
8. reject mutations to every bound receipt field.

The consumer may use only the Python standard library plus repository test infrastructure.

## Import firewall

The consumer and its tests must import no module from `claim_audit_lab`, the CAL research tree, or any checked-out CAL source.

## Interpretation

A pass establishes bounded cross-repository byte portability for the frozen profile and vector domain only.

It does not select a final production wire schema, establish arbitrary JSON canonicalization, authorize Contract C changes, or promote CAL production behavior.
