# Fixed CAL Ollama launcher RC3: Q04 frozen-pin schema successor

**Owner:** [apparatus-contracts #173](https://github.com/camerontjs-dot/apparatus-contracts/issues/173).
**Ancestor evidence head:** `81bc96b72aeff5267d07c354a8a01f9fe1ade94b` (Draft #179).
**Previous RC2 frozen candidate:** `290bee5a163f70f5d7bb42662131dd5b0375a761`,
first Q04 `KeyError('pins')` after bounded Q01/Q02/Q03 passes. Keep its
`b96731112f79768ccb76c6b9802a1fc13b1feaa196747ac4de8b8156a1b2c46c`
freeze and 196 raw indexed receipts immutable.

This is a new, separately frozen public-synthetic **zero-model** Q01–Q13
research-infrastructure candidate. No scientific CAL run, production integration,
G89 tool-safety retry, broader host permission, arbitrary Docker command exposed
to a model, or actual model-inference actor is authorized.

## Transfer and exact difference

The full prior Q01–Q13 expected outcomes and limits are retained in
`PARENT-PROTOCOL.md`, verbatim SHA-256 `7422f658cbde1ebb24d2201ced25171eed2b8560d37a2b825d441e82bba845cf`. It governs any
details not further restricted here. Q03's actual two-tool MODEL-REQUEST,
the full expected rendered prompt, FixedAdapter, Docker worker-control probe,
receipt checker, meaningful Q08 network checks, Q09 dispatcher negatives, and
Q10–Q12 controls are **byte-identical** to RC2. Previous actual Q01–Q03 results
do not transfer as new passes; RC3 must exercise all required cells itself.

**Only scientific runner behavior correction:** Q04 now checks the actual
Docker `config["Image"]` against `self.pins["image_id"]`, the validated
SHA-256-bound *external controller-private* `PINS.json` value. It must not
read absent `freeze["pins"]`; the public frozen manifest binds only the
external pin file's SHA and a safe summary.

New exact manifest/experiment ID: `cal-fixed-ollama-public-synthetic-rc3-20261010`.
New source ancestry base is the sibling report commit above. The official
Python linux/arm64 worker image is pinned to immutable local image ID
`sha256:48b13b003dda20b16f9442b8475aa05fe21bf6579a8c881db92ffb4d8fd20f83`,
the local Ollama provider binary to
`sha256:9d8ee8964971c91b4faaa84cf61aac9a9d5a568af6629d8fc1d2cb939f9ce07f`,
and the model manifest to
`sha256:9cda952e5d8f43bd4ddd3954c82e404e6cc286e04ceb77fa536f9f7113d7b28d`.
Private file paths, binary hashes, prompt bytes and controller receipts remain
outside the worker aperture.

## Source-informed, pre-exposure discriminators

`preflight_freeze_schema.py` reads the immutable RC2 freeze, the original
RC2 and newly corrected RC3 runner source, the exact private pin bytes and
an *image inspection only*; it imports neither runner. Its output
`PRE-FREEZE-SCHEMA-CHECK.json` requires old missing freeze key `pins`
to be detected, corrected source to have **no** missing freeze keys, the
correct immutable image ID to compare equal, and a mutated wrong image ID to
compare unequal. It does **not** exercise a Docker worker or count as Q04 pass.

A separate fresh controller-only service check `PRE-FREEZE-SERVICE.json`
confirms existing task-owned Ollama 0.40.0 on literal controller loopback,
with source receipt SHA-256
`4363ccfe37ed1a9a4130af84b2f699341b75cf73b8ac6942aefc1d51ca54514a`.
This is a reachability prerequisite, **not** a Q03 prompt or isolation verdict.

## Frozen Q01–Q13 acceptance and first-stop order

Order: precheck identities/one-attempt ledger, Q03, Q01–Q02,
Q04–Q12, Q13. First failure or unknown is terminal for this frozen candidate;
only externally recorded owned-resource cleanup and custody can follow.

| Gate | Required concrete control |
| --- | --- |
| Q01 | Actually stage the exact two-file public synthetic packet and check paths, bytes, inodes and external receipt with the code-isolated checker. |
| Q02 | Physically copy the complete source including outside-world sentinel and demand `EXTRA_FILE` refusal. |
| Q03 | Capture real Ollama render-only HTTP 200, exactly two approved tools and **full prompt bytes** matching frozen expectation, no inference-shaped content or remote provider. |
| Q04 | Observe actual worker mounts, namespaces, privileges, UID, memory/CPU limits, environment, image identity from validated `self.pins`, and scratch. Unexpected/missing checks stop. |
| Q05 | Exercise both permitted reads through the actual scripted model-call-shaped fixed adapter and compare bytes. No model inference. |
| Q06 | Actual dispatcher authorization refusals for meaningful existing outside paths and traversal, prior to any host process dispatch. |
| Q07 | Permitted scratch write/readback and forbidden writes/oversized multibyte refusals, actual readonly-file-system errors, immutable canaries. |
| Q08 | Same-worker positive accepted socket control, numeric `connect_ex` `ENETUNREACH` on documentation-only 192.0.2.1:9 and `ECONNREFUSED` for container loopback 127.0.0.1:11434, routing/namespace and absent host socket. Silent exit is not a pass. |
| Q09 | Actual malformed/native/MCP/hosted/generated/unknown tool-name pressure with unchanged command/host-process counters before dispatch; compare a weak last-key-wins mock. |
| Q10 | New worker ID, identical bounded config, clean scratch, no first marker, fresh exact input bytes and initial request messages. No provider-cache-erasure claim. |
| Q11 | External raw command, HTTP, tool, stream and receipt-byte/timestamp/hash acceptance plus deliberately mutated checksum negative. |
| Q12 | Observe and remove only exact owned Docker workers, verify absence by full-ID inventory and independent inspect; fresh-reset is distinct from cleanup-only. |
| Q13 | On full required bounded pass **PENDING_EXPLICIT_OWNER_ADMISSION_REVIEW**; any missing/failed/unknown remains BLOCKED. Never automatically admit a model actor or CAL pilot. |

The source-informed code-isolated checker was authored by the same engineering
controller. This is **not** a blind independently authored or scientific-gold
evaluation. Ollama's modified-build provenance, provider internal state,
future model-generated tool-use fitness, and arbitrary network sandbox security
remain out of scope. No amount of green scripted transport controls alone
establishes an admissible scientific agent.

## Freeze, one attempt, publication

After reviewing source, execute prefreeze static checks and obtain exact local
hashes and listener. Commit **preparation only**. Run `prepare_freeze.py`
once with the separate external exact private PINS.json, preparation SHA and
UTC freeze timestamp; review that `FREEZE.json`, then commit **only**
the freeze. Record commit, tree, freeze SHA and operator review in controller-only
custody. Execute `qualify_once.py` **once** with exact candidate SHA, external
freeze hash, reviewer record and fresh attempt directory. The one-shot ledger
reserves that freeze and cannot be reused.

Never repair/retest a first-failed frozen candidate. Publish only a separate
sibling retrospective evidence directory, retaining sensitive raw receipts in
external controller custody. Historical PRs #174–#179, all frozen CAL
experiments and G89 restrictions stay untouched. The user authorized continued
bounded launcher engineering; an actual model inference/agent launch still
requires its own separately qualified profile and authority.
