# Fixed Ollama / Docker CAL launcher qualification RC0

Owner: [Apparatus #173](https://github.com/camerontjs-dot/apparatus-contracts/issues/173).
This is a separate source-informed public-synthetic engineering qualification.
The current operator request authorizes qualification through the existing
Q01-Q13 protocol. No frozen CAL study, G89 operation, production apparatus,
canonical contract, release, consumer pin, or merge is authorized.

The verbatim parent is `PARENT-PROTOCOL.md`, SHA-256
`887ca9978779f75df576e8391c1565e1b746bc3fad69c7b0e0f350785cca7a7c`.
Existing frozen experiment manifests retain authority over their own apertures.

## Exact candidate and aperture

`FREEZE.json` binds all adapter/controller/request/schema/expectation/source
identities before any decisive control. The Git commit containing that freeze
is the candidate. It will never be repaired or rerun after a first stop.

Packet custody code is reused unchanged from Draft #175 exact head
`e626b0669c81006df08a8bc859bc1e5dd14cb5fa`. Its 34/34 macOS result, original freeze
`dd34b1da4923fc6a91a5cecd2152f2cb9154c5a8c355eb04bd999c3925f2018b`, raw external
receipt `c8dfa2d221de400e49d317aa63cb918df608e5bf1dd726c846399659ca466f25` and
stderr `c3307afb3aec3873dca949fb3f22c89eec4976b5db3ff8fbea3114179bd45957`
remain their own historical packet-control evidence. No rerun is planned.
Draft #174 head `7d9df68eff5d83d93aa6f07434d2f2e0d7fc2244` and its 18-pass/1-setup-error
`APPARATUS_INVALID_PLATFORM_CONTROL` remain unchanged.

Only the two files in `MANIFEST.json` are mounted at `/packet`. Source, synthetic
outside-world sentinel, manifest, checker, expected outcomes, receipts, model
files, credentials, private material, prior results, and gold stay outside the
worker. The model request contains only the two authored instruction messages
in `MODEL-REQUEST.json`; it contains no conversation, project, or study history.
The worker has no access to the controller's installed Ollama service or files.

The controller uses the existing Ollama 0.40.0 service at the literal loopback
`http://127.0.0.1:11434/api/chat`; no credentials, proxies, redirects, service
installation, policy change, or MCP attachment. `PROVIDER.json` pins the installed
binary hash and qwen3.5:9b manifest/config/model/params/license blob hashes. Local
model blobs were actually streamed through SHA-256 and all matched their manifest.
Embedding-only models are not chat candidates. qwen3.5:9b is the smallest
already-installed completion/tools-capable model by bytes. Codex is the builder,
not the selected actor. No inference or autonomous model loop is authorized by
this zero-model qualification.

Observed Go build metadata binds the installed Ollama binary to source revision
`0d0720e51fb2fd9aa58781c3d720c06d720c2e7b`, but also says `vcs.modified=true`.
The release binary is exact-hashed; source reproducibility and its unrecorded
build diff are unverified. Source inspection is supporting evidence, not proof
that every installed byte is reproduced by the source checkout. A live rendered
prompt must independently agree with the full frozen expected prompt. Neither
that observation nor this work qualifies arbitrary provider internals, host
privileges, training-data provenance, physical memory erasure, or model fitness.

Ollama's API structs do not retain `additionalProperties` or `maxLength` in their
rendered tool schemas. `MODEL-REQUEST.json` therefore transmits only supported
fields. `TOOL-PROFILE.json` separately preserves the actual adapter enforcement:
exact key sets, fixed enum paths, strict UTF-8 and at most 4096 output bytes.
Generated/hallucinated names have no binding. The qwen3.5 formatter adds its
frozen tool-call-format guide and empty thinking prefix, both included in
`EXPECTED-Q03-PROMPT.txt`; its example name is also a Q09 denial control.

## Freeze, execution, and stops

Before execution, syntax/JSON parsing only; no protocol controls, inference,
or worker creation. A discovery lookup initially found the exact BusyBox
reference unavailable. Preserve that first receipt. A subsequent *exact-digest*
pull succeeded before freeze. No different digest or daemon context was chosen.
That provisioning observation is not a worker control pass.

Run once: `python3 -B qualify_once.py <fresh-external-receipt-directory>`.
The controller refuses an existing directory and checks every frozen file hash
before Q03. Dynamic run-owned IDs and world paths are substitutions in the
otherwise frozen command arrays in `qualify_once.py`.

Q03 runs first, using the maintained `_debug_render_only:true` request. The
actual HTTP request, status/headers/response and complete rendered prompt are
stored externally. This mode may load a model runner but must return the debug
render artifact with no generated message/tool calls/evaluation count. Any
missing artifact, mismatch, inference-shaped response, exception, timeout or
unknown surface blocks before creating a worker. Do not retry or substitute
another transport. Subsequent controls run only after that gate.

| Cell | Frozen positive and negative acceptance |
|---|---|
| Q01 | Stage this exact new manifest with unchanged #175 builder; read paths/directories/bytes/inodes and receipt with its code-isolated checker. Existing 34/34 evidence is reused only for that exact packet implementation's already executed adversarial controls. |
| Q02 | Physically copy all of the fresh synthetic source including an existing outside-world sentinel; require `EXTRA_FILE` for that extra file. |
| Q03 | Capture complete actual debug-render request and effective prompt; exact two-tool semantic inventory and entire rendered bytes must equal the frozen expectation. Inspect both dispatcher entry points and pinned provider source/model metadata. |
| Q04 | Real container ID/image/mount/privilege/network/environment/resource inspection; UID 65532 and zero CapEff / NoNewPrivs observed inside the same worker. Only world bind and scratch tmpfs; no inherited host environment, ports, devices, credentials or host namespaces. |
| Q05 | Both allowed reads through the actual Ollama ToolCall-to-dispatch binding, byte equality with external frozen inputs. |
| Q06 | Absolute/traversal/alias/unknown/source/controller/parent/sentinel requests through the real dispatcher require authorization refusal. External synthetic targets actually exist; nonexistent-file exceptions do not count. |
| Q07 | Actual permitted scratch write/readback; oversized ASCII and multibyte UTF-8 and forbidden paths refused. Direct non-model packet/root writes require read-only-filesystem errors. Source/world/sentinel bytes unchanged. |
| Q08 | Same-worker interface/route inspection plus literal-address connection attempts: kernel `Network is unreachable` and loopback `Connection refused` required. Controller model endpoint stays literal loopback; no host socket/controller mounts. DNS failure/software absence is insufficient. |
| Q09 | Actual dispatcher rejects native/MCP/hosted/generated/nonexistent/example names, extra fields, wrong types and duplicate keys before any dispatch. No server/process attachment or dynamic tool generator. |
| Q10 | Different fresh container ID and empty scratch; first answer absent. Initial request and effective rendered context include only this run's authored messages. Provider internals/cache erasure are outside this bounded claim and cannot be assumed. |
| Q11 | External raw time/argv/stdin/stdout/stderr/exit/timeout and request/response receipts, hashes, tool envelopes, independent readbacks and canary observations; none mounted into the worker. Same-controller custody, not blind independent authorship. |
| Q12 | Second worker shows no first marker; remove only recorded run-owned container IDs and observe their absence; retain inputs/receipts and leave existing services, unrelated resources and G89 untouched. |
| Q13 | Source-informed engineering-owner review of exact freeze, first result, all required cells and scope. No FAIL/UNKNOWN/NOT_RUN may be admitted; actual CAL pilot requires separate authority. |

First FAIL/UNKNOWN/NOT_RUN blocks admission. Record `FIRST-FAILURE.json`, full
raw response/stderr and trace, skip later measurement cells, and perform only
owned cleanup. A tool-safety denial is terminal; no alternate route, syntax,
provider or G89 operation. Any correction must be a separately identified later
candidate and attempt. This task must preserve the first attempt, even if its
failure is an evaluator or platform setup error.

## External receipt procedure and publication

The controller captures actual child process streams; it does not synthesize
engine results. The checker never imports the packet verifier. The controller
exercises the actual adapter and separately reads Docker configuration/runtime,
scratch output and host synthetic sentinel bytes. All are same-controller,
source-informed engineering observations; no blind or independently authored
scientific claim is made.

Write `RESULT.json` and `RECEIPT-INDEX.json` outside the worker. Preserve raw local
bytes. Public projections replace only literal local paths; each projection is
distinctly hashed and must never be presented as the original raw receipt.
Report precise Q01-Q13 dispositions and unknowns in a separate Draft research
PR and append navigation/result comments to #173 and #137. Preserve all original
PR identities and receipts. No merge, release, repin, canonical behavior change,
scientific CAL result, or automatic integration follows.
