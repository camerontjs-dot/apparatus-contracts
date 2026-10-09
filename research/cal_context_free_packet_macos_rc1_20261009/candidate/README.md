# CAL context-free packet RC0: offline staging only

**Research-infrastructure candidate, not an isolation or model qualification.** This intentionally narrow prototype packages a frozen, explicit file allowlist into a fresh synthetic world and records what was staged. It does **not** run Docker, `sbx`, Codex, any agent, any model, a network operation, or an evaluator. No existing frozen CAL experiment is changed.

## Why this exists

The normal CAL Pipeline project uses [a context-free execution protocol](https://github.com/camerontjs-dot/verbose-engine/blob/main/project-governance/cal-pipeline/CONTEXT-FREE-EXECUTION-PROTOCOL.md): experiment-specific file and information apertures; freeze/reveal controls; and exact run receipts. The first reusable missing subtask is **packet construction**, not a new chat-actor/sandbox authorization method. Distinguish:

1. **File-world custody:** specified bytes are the only bytes copied into `world/`; hidden gold and previous outputs are not staged.
2. **Runtime containment:** what an agent can actually read, invoke, connect to, or mount. **NOT ASSESSED here.** File selection is not proof of read confinement.
3. **Fresh-model context:** what conversation, tools, provider-side memory and external state are actually available to an agent. **NOT ASSESSED here.** A blank working directory cannot clear conversation history.
4. **Scientific qualification:** independent frozen candidate, evaluator, separate observer, and allowed information aperture. **NOT ASSESSED here.**

## Existing evidence used, with limits

- [MainFrame Live #83](https://github.com/camerontjs-dot/mainframe-live/issues/83) narrowly qualified a Docker substrate, but not the whole model-visible launcher/tool surface.
- [#87/#88/#89](https://github.com/camerontjs-dot/mainframe-live/issues/89) exposed or failed to qualify static/dynamic host-MCP reach; #89 stopped at a safety denial, with no decisive MCP probe.
- [#90](https://github.com/camerontjs-dot/mainframe-live/issues/90) identifies checker design hazards, including trusting self-generated allowlists, collapsing missing evidence into empty results, and confusing target failure with authorization denial. #90 is a separate MainFrame design record, **not** permission to bypass its safety stop.
- [#80](https://github.com/camerontjs-dot/mainframe-live/issues/80) now reports the first G90 offline checker failed independent review. Its v2 successor is not independently qualified and no actor was admitted. Preserve those outcomes rather than re-running them under CAL.
- Docker documents `sbx` microVM isolation, but a mountless VM is not sufficient: agents may have full in-VM privileges; direct-mode workspace mounts are read-write; skills can be shared; the MCP gateway is present and local stdio MCP servers execute outside the VM on the host. [Security](https://docs.docker.com/ai/sandboxes/security/), [MCP](https://docs.docker.com/ai/sandboxes/mcp-gateway/), [defaults](https://docs.docker.com/ai/sandboxes/security/defaults/).

The historical Research Scaffold Harness repository is a specific treatment-stage research apparatus, not automatically the owner of a generic agent launcher. The project-wide coordinator in Apparatus Contracts should route this candidate to the appropriate dedicated owner if required; this Draft research tree does not alter any public contract.

## RC0 file protocol

The **controller**, not the candidate agent, creates and freezes a JSON manifest:

```json
{
  "schema": "cal-context-free-packet-rc0",
  "experiment_id": "demo-001",
  "files": [
    {"path": "spec/request.txt", "sha256": "<exact 64 lowercase hex digits>"}
  ]
}
```

`files` must be lexicographically sorted, nonempty, and contain at most 256 exact relative paths. No globs, recursive inclusion, inferred dependencies, duplicate keys, `..`, symlinks, hardlinks, Git object stores, or ambient credential directories. Each listed file must match its exact SHA-256. Source root and output must be disjoint. Input budget is 20 MiB per file, 100 MiB total. Relative paths are POSIX NFC with no control characters. These are conservative **RC0 staging restrictions**, not a new CAL contract or a claim that every valid experiment fits them.

From a trusted controller environment:

```sh
python3 prepare_packet.py prepare \
  --manifest /controller/frozen/MANIFEST.json \
  --source-root /controller/approved-snapshot \
  --output /controller/staged/new-run
python3 prepare_packet.py verify \
  --manifest /controller/frozen/MANIFEST.json \
  --packet /controller/staged/new-run
```

The output tree is:

```text
new-run/
  world/                 # only manifest-approved files, copied as read-only bytes
  scratch/               # empty, writable workspace for an eventual actor
  controller-receipts/
    PREPARE.json          # trusted-controller receipt; MUST NEVER be put in actor aperture
```

**Critical:** A later runtime may receive `world/` mounted read-only and `scratch/` as a separately restricted writable path. It must **not** receive `new-run/` as a whole, the original source root, the manifest/controller receipt, hidden labels, source checkout history, credentials, a host Docker socket, or a privileged host MCP path. Permissions (`0444` files and `0555` world directories) are convenience markers, not a boundary against an agent with `sudo` or a different UID. A true read-only mount and outside-world checks are needed before claiming enforcement.

Receipts carry only relative paths, digests, byte counts, a manifest identity, and explicit `STAGED_BYTES_ONLY_NOT_AN_EXECUTION_OR_ISOLATION_QUALIFICATION`. They do not authenticate a reviewer or prove confidentiality. The verifier in this candidate shares the packager implementation and is **not** an independent consumer. File source is expected to be a controller-owned, non-concurrently-mutated snapshot; no claim is made against a malicious concurrent host writer.

## Local synthetic development checks

```sh
python3 -m unittest discover -s . -p 'test_*.py' -v
```

Tests cover exact allowed reads, retained hidden source outside the packet, digest substitution, symlinks and hardlinks, traversal and ambient stores, duplicate JSON/paths, sorted manifest, output overwrite, source/output overlap, extra world files/directories, mutated copied bytes, receipt-binding, and deterministic two-run copy. The seeded copy-all weak baseline must be rejected for the intended extra-file reason. These tests establish only encoded staging behavior on the observed platform, not macOS, Docker confinement, model isolation, or independent evaluation.

## What the CAL supervisor must do next

1. Obtain an exact **new**, separately scoped public-synthetic candidate information manifest, *not* a frozen CAL/EB/Contract-C experiment packet repurposed without authorization. Bind filenames, immutable source bytes, expected tool/agent capability profile, forbidden information, freeze/reveal order and contamination stop.
2. Assign an owner for the actor-launcher boundary. Prepare an **offline-only** runtime/tool-surface qualification profile first. Do not import or run MainFrame G89's blocked control or use a host MCP workaround to avoid its denial.
3. Select one bounded runtime candidate and test its **complete** effective model-visible tool set, credential/network/host reach, read confinement against seeded in-world/out-of-world markers, and teardown. Use a controller independent of the agent. Required UNKNOWN/NOT RUN blocks admission.
4. Only after that qualification, prepare one separate **CONTEXT-FREE REQUIRED** launch packet for the chosen CAL task. No new prompts/research may expand that already-frozen aperture. Later private/research data and qualification evidence remain outside the actor world until their protocol permits reveal.

**Stop:** At a reported static packet result or an explicit missing authorization/artifact. No model or Docker call, production promotion, contract change, ERS/EB/CAL alteration, or automatic integration is in scope for RC0. Research-only; keep Draft and preserve failures.
