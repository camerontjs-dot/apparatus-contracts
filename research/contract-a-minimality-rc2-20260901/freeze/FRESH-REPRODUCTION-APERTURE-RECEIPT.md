# Contract A RC2 Fresh-Reproduction Aperture Receipt

Status: **PREPARED / NOT EXECUTED IN THIS CONTEXT**

This receipt records the sanitized pre-freeze aperture prepared after the Contract A RC2 candidate/reference/evaluator freeze.

## Independent repository

Repository: `camerontjs-dot/research-scaffold-harness`

Branch: `research/contract-a-rc2-fresh-reproduction-aperture-20260901`

Base before aperture materialization: `548bfa81f65290eda15af658f647497679b840ef`

Prepared aperture head: `711347313ee4bd9b425d36e63d339133043d92b5`

Prepared repository tree: `fb09cdb2d5b556013ed5daacac31d8bc8651e045`

Aperture subtree:

`research/contract-a-rc2-fresh-reproduction/` → `ca271469da3aebcb8e8d94a20fa83aedf5006157`

Public normative subtree:

`research/contract-a-rc2-fresh-reproduction/public/` → `8662988f600a086b78f571c035eba21885024fcd`

## Exact aperture files

- `APERTURE-MANIFEST.md` → Git blob `a889ad650262afbfd2bf1702e6319bec59966a74`
- `LAUNCH.md` → Git blob `0247f381a7c49db48c952ebc70b232b32de7f585`
- `public/SPEC.md` → Git blob `2e7c37fca9aa6bdd1090fb527a663bdbe606ebcb`
- `public/schema.json` → Git blob `ff5cddfeacf4511136a3dd3b47db1a794b631cd9`

The public specification and schema blobs are byte-identical to the frozen Apparatus candidate authority.

## Sanitization boundary

The aperture does not copy or authorize:

- the frozen reference validator;
- the frozen evaluator;
- reference valid/invalid fixtures;
- field-family/ablation outcomes;
- normal-context compatibility conclusions;
- prior Contract A reasoning or conversation context;
- promotion conclusions;
- the sealed post-freeze comparison authority.

The underlying RSH repository contains unrelated historical files because the branch starts from repository `main`. `APERTURE-MANIFEST.md` explicitly makes those files non-authoritative and out of aperture for this reproduction.

## Launch behavior

The context-free packet requires the fresh implementer to:

- verify exact normative blob identities before implementation;
- derive behavior only from public `SPEC.md` and `schema.json`;
- implement and independently test a small Contract A consumer;
- freeze implementation and prereveal tests immutably before reference reveal;
- stop at `PRE_REVEAL_FROZEN`;
- wait for a separate explicit post-freeze reveal authorization.

## Post-freeze comparison preparation

A separate sealed comparison authority has been prepared outside the fresh aperture. Its content and location are intentionally not part of this receipt's clean-room handoff surface.

It must not be exposed to the fresh implementer before a verified prereveal freeze.

## Execution boundary

No fresh independent implementation was executed in the normal-context Contract A RC2 thread. The thread is contaminated by reference design and evidence and is not eligible to perform the independent reproduction itself.
