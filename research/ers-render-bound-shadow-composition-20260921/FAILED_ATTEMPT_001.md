# Preserved failed successor attempt

The first ERS render-bound candidate was frozen locally at:

- commit: `3de1835885a22147d8e930e03448df402661fc3d`
- tree: `f176b9663b28913d81e04b24fac955ec42b3c63a`

Its deterministic render tests passed and the cross-repository run reached the
positive Contract E/ERS shadow boundary. The independent receipt harness then
failed while computing an ERS shadow-result identity: the successor result
included an informational integer payload-length field, while the inherited
ERS canonical identity helper intentionally supports only the existing
string/bool/null identity subset.

Observed failure:

`unsupported_identity_value`

No authorization was widened, no executor ran, no payload was written, and no
MainFrame path was touched. This candidate is preserved unchanged. The next
successor changes only that informational receipt field to a string so the
existing identity machinery remains unchanged; it is frozen and qualified as
a new commit rather than amending this candidate.
