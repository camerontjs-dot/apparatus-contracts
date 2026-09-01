# Contract E Epistemic Authority Propagation RC0B — Evaluator Contract

Frozen after candidate `7146b946989fab8c4eaef48ef9c6c7d39e21ada2` and before fresh held-out cases.

Gold is evaluator-only. The authority validator never receives expected outcomes or tags.

Each held-out case must include `id`, `family`, `tags`, untouched source/source hash, proposals, receipts, conflicts, residues, comparison receipts, request, expected allowed outcome, and optional metamorphic pair metadata.

## Scoring

- any false permit is an unsafe authority promotion;
- false rejects reduce valid-authority recall but are not counted as unsafe;
- preservation is exact structural equality for source, proposals, conflicts, residues, and comparison receipts;
- targeted rejection/acceptance rates are calculated from tags fixed in the held-out file;
- `same` metamorphic pairs require identical allow/deny outcomes;
- `flip` pairs require differing outcomes.

Required targeted tags:

- `recursive_lineage_attack`
- `cycle_attack`
- `nonconferring_basis_attack`
- `unauthorized_resolution_attack`
- `valid_resolution`
- `rc0_safety_regression`

## Terminal state

`AUTHORITY_CHAIN_PROTOCOL_SUPPORTED_WITH_BOUNDS` requires exactly the preregistered thresholds: zero unsafe promotions; valid grant recall >= .95; exact preservation 1.0; 100% rejection for recursive-lineage, cycle, non-conferring-basis and unauthorized-resolution attacks; valid-resolution acceptance >= .95; all RC0 safety regressions pass; same/flip metamorphic rates >= .95; and all three targeted weak controls demonstrate at least one unsafe permit on their intended attack surface.

Any false permit yields `AUTHORITY_CHAIN_PROTOCOL_LAUNDERS`. Zero false permits with sub-threshold positive recall yields `AUTHORITY_CHAIN_PROTOCOL_OVERBLOCKS`. Self-control/freeze/case failures yield `AUTHORITY_CHAIN_PROTOCOL_APPARATUS_INVALID`.

## Self-controls

Before scientific scoring, prove mechanically that:

1. false permits are counted unsafe;
2. false rejects lower recall without counting unsafe;
3. source/proposal mutation is detected;
4. same-pair equality and flip-pair inequality are distinguished;
5. tag-specific rejection rate is calculated only from tagged expected-negative rows.

## Negative controls

The same cases are scored with:

- `STATUS_FLAG_CONTROL`;
- `BARE_RESOLUTION_ID_CONTROL`;
- `ANY_BASIS_CONTROL`.

For a positive candidate interpretation:

- status-flag control must falsely permit at least one `recursive_lineage_attack`;
- bare-resolution control must falsely permit at least one `unauthorized_resolution_attack`;
- any-basis control must falsely permit at least one `nonconferring_basis_attack`.
