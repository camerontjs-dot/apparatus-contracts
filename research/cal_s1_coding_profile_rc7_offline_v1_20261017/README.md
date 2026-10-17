# CAL S1 source-only coding profile v1

This research adapter exercises exact packet reads, bounded candidate writes and
a fixed development-test interface using synthetic runtime and observer fixtures.
Its disposition is **OFFLINE_PROFILE_PREPARATION_ONLY / Q13_NOT_ADMITTED**.
The RC7 qualification remains **BLOCKED_PREFLIGHT_TOOL_SAFETY_DENIAL**.

The base is Draft [#183](https://github.com/camerontjs-dot/apparatus-contracts/pull/183)
at `beb4477dc3e87b03cec9eaa186a17042b4cac765`. Its three stop records and every
predecessor remain unchanged. Owner: [#173](https://github.com/camerontjs-dot/apparatus-contracts/issues/173).
Only this additive research directory changes.

## Fixed interface

`offline_profile.py` accepts UTF-8 JSON envelopes containing exactly `version`,
`name` and `arguments`. Version `cal-s1-lines-v1` has three operations:

| Operation | Arguments | Controller boundary |
| --- | --- | --- |
| `read_packet_file` | `path` | Exactly seven sorted, hash-pinned profile paths; regular single-link entries and clean ancestors; exact UTF-8 bytes, no newline repair. |
| `write_candidate_lines` | `path: candidate.py`, `lines` | Only the named candidate; UTF-8 byte limit 32,768; independent readback must equal the serialized bytes. |
| `run_development_tests` | Empty object | Controller-selected evaluator/case identities and immutable candidate-byte snapshot. No command, shell, endpoint, cwd, environment or evaluator selector is accepted. |

The new line-array representation joins literal lines with LF and adds one final
LF. An empty array means an empty file; `[""]` means a single LF. Embedded line
terminators and unencodable surrogates refuse. Literal backslashes, quotes,
indentation, empty lines and Unicode survive unchanged. This representation
does not reinterpret or repair the RC5/RC6 arguments.

Only controller code constructs the immutable `Profile`, adapter, transport and
observer. The executor receives no observation callback. `Witness` requires a
separate observer object with the profile-declared identity; its returned events must
match fresh run, profile, candidate, evaluator and observer identities, the
consumed candidate hash, and every ordered case start/finish. Missing, extra,
replayed, failed or malformed events refuse. Runtime stdout, exit zero, counts,
hashes and complete-looking receipt objects cannot provide these events.
`completion_check.py` imports no adapter, runtime or candidate code.

`Adapter.finalize` is a controller-only check of the current candidate and the
last accepted observation. Rewriting the candidate invalidates it. Run history,
dispatch history, inputs, candidate bytes, feedback and events have explicit
bounds. Missing interfaces and stale scratch fail closed.

## Evidence boundary

The tests execute Python's stdlib unittest engine. Adapter operations use
`FakeRuntime`; the separate in-process `FakeObserver` supplies synthetic transcripts.
Neither executes candidate Python or a CAL evaluator. The fixture evaluator and
observer identity tokens both use the test module's SHA-256. There is no evaluator
implementation behind that token. The adapter compares the provider's declared
identity attribute; it does not authenticate the provider's source or binary.

This checks the protocol's refusal behavior. It does not establish that a real
evaluator or case ran, or that candidate bytes were causally consumed. A trusted
observer that lies can fabricate a complete transcript; no in-process Python
object provides host isolation. A live binding must independently observe the
actual immutable execution artifact, evaluator and cases outside candidate and
executor report control. No such binding is implemented here. The adapter
explicitly refuses an observer claiming a live evidence layer.
Same-instance executor/observer wiring also refuses; this catches accidental
aliasing, not malicious collaboration between in-process objects. Size checks
bound accepted objects after serialization. A live transport must bound raw
response bytes before decoding to protect memory.

The retained #175 packet builder and code-isolated checker are imported unchanged
for fresh seven-file synthetic filesystem fixtures, including an unlisted
source-only file, extra staged bytes and stale scratch. They remain packet
custody tools, not execution checkers. RC4's non-root/read-only/network-none
worker design remains the proposed runtime substrate; no worker code is run.
RC6's identity/sequence reconstruction informed the checker. Nothing transfers
their results to this new profile.

An initial 50-test pass and later 71-test pass preceded source review. Review
found that the executor could supply the whole first witness transcript. That
initial design was insufficient for independent execution attribution despite
green tests. It was replaced with the separate observer interface. Review and
development failures are preserved in `evidence/DEVELOPMENT-HISTORY.json`;
unmodified initial source snapshots and original logs remain in the dedicated
controller output directory. This is source-informed development, not a blind
scientific qualification.

## Reproduce the offline controls

From the Apparatus repository root, with an existing Python 3.11+ interpreter:

```sh
python3 -B research/cal_s1_coding_profile_rc7_offline_v1_20261017/run_offline_tests.py --output /tmp/cal-rc7-offline-fresh-output
```

The output must not exist. No package installation, container or model is used.
`RESULTS.json` records source/dependency hashes, per-test outcomes, Python version
and log hash. Published final receipts are under `evidence/final/`.

## Preserved failures and remaining authority

RC4's frozen subject remains `e53fc412a0db007ba87c4d1720cee66b781fc89c`.
RC5 and RC6 retain their first byte-exact failures: 31 supplied bytes versus the
required 32 including terminal LF. RC5's missing-field checker failure also
remains. RC6's first external checker was 41/45. The earlier RC0 platform-control
failure, Q08 observability stop, Q03 failure and tool-safety denials are not
superseded by this work.

Dependent CAL Draft #214 is only a metadata reference at
`a10e61f0d4be26ebb93a2b798d1a5f46470cc42c`; seven-file staging manifest
`de1df6d7da410ea3e58607d4ff967024bdf2cf6e28123961e1ad84e1c4aa62b4`.
Its source bodies, calibration/held-out material and labels were not accessed.
This directory contains synthetic fixtures only and no CAL candidate.

A live attempt still requires a documented platform-supported resolution of the
denied preflight through safety-review owner #177, separately reviewed exact
profile/run authority, frozen runtime/provider/model/image and tool inventory,
actual independent execution observations, effective read/write/network/host
negative controls, adversarial model-source behavior, reset/teardown and external
receipts. Required failures, UNKNOWN or NOT_RUN block admission. Q13 needs its
own explicit exact-profile decision after that evidence. No builder-launch
instruction is issued. `NEXT_OWNER_PROMPT.md` is limited to reviewing these
remaining prerequisites.
