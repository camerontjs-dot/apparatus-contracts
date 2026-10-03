# Deviation: run 02 residue classified producer ids as semantic change

Preserved successor: `b7912df29b03dfbbf77c7341b74cb3a8fc7b94df`
Preserved harness blob: `672dde8b49506a08ff37c14affe7d4111525f695`

Run 02 disposition: `FALSIFIED_POLARITY_SUCCESSOR_DOWNSTREAM_CONFORMANCE`
Error: `PIPE01 parent semantic residue changed: semantic_implementation_sha`
`847cc970642bb648dc994b929c2053b5c9d4648c` to
`caa0048f8f511ec3c4aa1ce713766f2219a04bc1`

Decisive exposure occurred. PIPE01 was the only case executed. Before the
residue comparison, that case had already matched parent `supported`, Decision
`clear`, consumer `candidate_for_authorization`, reason code
`contract_c_supported`, and the unchanged decision target. The Contract D
residue diff was empty. The only structured diffs against the historical arm
were the successor semantic implementation and the successor resolver commit.
Contract C whole-object bytes differed, as required.

The exposed residue pattern matched 64-hex digests and missed 40-hex Git ids.
That mislabeled an expected provenance change as a semantic falsification.
The exposed evaluator is unchanged at the preserved successor. This successor
treats exact 40-hex and 64-hex tokens as provenance identities in the residue,
and it checks the unchanged recomposition freeze and semantic-source commits
explicitly. Expected outcomes are unchanged.
