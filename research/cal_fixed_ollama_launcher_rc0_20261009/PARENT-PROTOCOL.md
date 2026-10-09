---
title: "Separate CAL actor-launcher qualification proposal"
domain: "agent-operations"
type: "project-plan"
status: "parked"
source: "https://github.com/camerontjs-dot/apparatus-contracts/issues/173"
tags: ["cal", "public-synthetic", "qualification", "blocked"]
updated: "2026-10-09"
structural_type: "project-plan"
owner_surface: "Apparatus issue #173"
authority: "project-status"
privacy: "public-safe"
volatility: "active"
source_of_truth: false
update_rule: "append-only"
verification: ["Future independently observed controls Q01-Q13; NOT_RUN"]
do_not_use_for: ["actor admission", "production", "frozen CAL experiment amendment"]
---

# Separate CAL actor-launcher qualification proposal

**DESIGNED_BLOCKED_BEFORE_EXECUTION.** The original PR #174 macOS reproduction
stopped with an apparatus error. This is an inspectable design, not a qualified
launcher, a complete observed tool inventory, or an executable admission packet.
All Q01-Q13 controls are **NOT_RUN**.

The first missing artifact is a separately identified, macOS-capable control
successor. Preserve original head `7d9df68eff5d83d93aa6f07434d2f2e0d7fc2244` and
the first 18-pass/1-error result. No further target execution in this attempt.

## Scope and authority

Apparatus #173 owns this preparation. Its original RC0 publication prohibited
Docker execution; the current operator request authorizes this *separate*
qualification preparation. It does not admit actors or modify frozen CAL studies.

The governing context-free protocol is Verbose Engine commit
`050cd1d5b5a828e9b55e5f503e1573dcb893fdc1`, blob
`acb4282838919a38ce69926e986cb4292c6af954`, SHA-256
`3c97f27922398cb311a122046d89ac443342a48f675ff01faad344cc0890e30d`.
Existing experiment manifests outrank this general protocol for their aperture.

This controller has read the public candidate code, tests and prior narrative.
The present review is source-informed. A later blind CAL pilot must start in its
designated context-free project with a new authorized packet and separate
freeze/reveal custody; this chat cannot become its independent actor.

> **Binds:** a future, separately authorized launcher qualification under #173.
> **Tier:** T0 design proposal; no runtime enforcement is claimed.
> **Check:** actual external Q01-Q13 receipts for an exact future frozen profile.
> **Escape:** missing artifacts, unknown inventory, failed controls or tool-safety
> denial block admission; preserve the result and stop without another route.

## Smallest proposed runtime

Use one disposable **Docker Engine container** and a fixed controller-mediated
function adapter. Propose two model-facing functions only: `read_packet_file`
and `write_result`. Their exact proposed schemas are in
`PROPOSED-TOOL-PROFILE.json`. The complete *observed* inventory remains **UNKNOWN**.
An empty proposed MCP/native/hosted list is not evidence of absence.

The worker has no generic shell/exec function exposed to a model, no host MCP,
extensions, browser, Docker control, hosted search, or generated tool path. The
adapter must be an exact inspectable artifact before any of those absences can
be qualified. It must reject unknown tool names, extra fields and invalid types
before dispatch. No subprocess fallback, shell interpolation or alternate reader.

Docker supplies the isolation mechanism. The only application work contemplated
is the fixed adapter around its supported interfaces, not a new sandbox platform.
This design does not claim Docker Sandboxes microVM equivalence and does not test,
repair, replace or reroute G89's MCP/policy operation. No G89 resource is reused.

Proposed worker settings are fixed in `QUALIFICATION-DESIGN.json`: image by exact
digest; Linux arm64; non-root UID/GID 65532; read-only root; drop all capabilities;
no new privileges; no host PID/IPC/network namespace or published ports; network
`none`; one read-only bind of *world only* at `/packet`; bounded ephemeral tmpfs
at `/scratch`; explicit CPU/memory/PID limits. No parent packet, controller
receipt, source root, host socket, credentials, inherited environment or volume.

These are supported Docker mechanisms, not empirical confinement evidence:
[container execution](https://docs.docker.com/engine/containers/run/),
[none networking](https://docs.docker.com/engine/network/drivers/none/), and
[read-only bind mounts](https://docs.docker.com/engine/storage/bind-mounts/).
Read-only bind propagation and any submounts must be inspected; configuration
must not be assumed to cover unexpected descendants.

The current Docker preflight returned a client but no server at its configured
endpoint. No daemon was started, image selected/pulled, container created, or
policy changed. Exact actor adapter, image digest and model/provider binding
are also missing. A future manifest must resolve them before execution.

## Exact proposed information aperture

`MANIFEST.json` binds only `data/marker.txt` and `instructions/request.txt`, with
their exact SHA-256 values. Both files in `public-synthetic-source/` are newly
authored public synthetic material. They have **not** been passed through RC0
after the first stop or delivered to any actor.

`read_packet_file.path` is an enum of those two paths. `write_result.path` is the
sole `answer.txt` scratch output. Enforce 4096 UTF-8 bytes for its content in the
adapter; JSON character length alone does not impose this byte bound. Result
bytes return to the controller through the recorded response channel. The
controller stores receipts outside the worker aperture.

Before design freeze, add exact public synthetic outside-world sentinels and
the independent checker/control bytes to the controller manifest. Do not put
oracle or checker bytes in the actor world. No private material, scientific
gold, previous CAL outputs, conversation history or project memory.

## Required zero-model controls

Freeze the corrected candidate, adapter, full request builder, provider binding,
image digest, complete inventories, fixtures, independent checker, expected
outcomes and command arrays **before** measurements. Qualification uses a
scripted non-model client exercising the *real* adapter and Docker boundary.
Never substitute canned results for unavailable engines or invocations.

1. **Q01 — independent packet custody.** Inspect staged paths, directories,
   bytes, inodes and source/receipt separation with a checker that does not import
   RC0's verifier. Test positive bytes and bounded regular-file refusal. Include
   macOS case-folded ambient-store paths and FIFOs as unrun adversarial controls;
   neither has a behavioral verdict in this attempt.
2. **Q02 — actual weak baseline.** Physically copy all of a fresh synthetic source,
   including outside-world markers, and require rejection for the intended extra
   material reason. Wrong target, unreadable fixture or unrelated setup failure
   is not a successful refusal.
3. **Q03 — complete effective inventory.** Independently capture the exact model
   request construction, every system/input/tool field and every dispatch binding.
   Account for native, MCP, extension, hosted and generated surfaces. Validate
   actual inventory against the separately frozen approved profile. If the chosen
   provider/runtime has an uninspectable or implicit tool surface, stop UNKNOWN;
   no model call is permitted merely to discover it before admission.
4. **Q04 — effective Docker configuration.** Observe the real container ID,
   image/config digests, mounts, UID, capabilities, namespaces, environment,
   resource limits and network state from the external controller. Unexpected
   mounts, credentials or host integration stop the attempt.
5. **Q05 — allowed reads.** Exercise both actual function bindings and compare
   returned bytes to the controller's frozen public inputs by SHA-256.
6. **Q06 — forbidden reads.** Submit absolute paths, traversal, aliases, unknown
   paths, parent packet/receipt/source paths and synthetic outside-world markers.
   Require a recorded authorization refusal, not a nonexistent-target exception.
7. **Q07 — writes.** Observe the permitted scratch output independently. Require
   refusal of packet/root/host writes, malformed names and oversized UTF-8 output.
   Verify before/after hashes of source, world and external synthetic sentinels.
8. **Q08 — host/network boundary.** Use exact frozen non-model probes inside the
   *same worker* plus external observations. Check interfaces/routes and actual
   bounded connection attempts. Do not equate DNS failure or missing software
   with egress denial. Inspect the controller's separately approved model-endpoint
   transport; no broad host network, credentials or local MCP exposure to tools.
9. **Q09 — hidden dispatch.** Submit nonexistent, native, MCP and generated tool
   names through the real dispatcher. They must fail closed without attaching a
   server, starting a host process, modifying a profile or generating another tool.
10. **Q10 — fresh state.** New container/run IDs and empty scratch for every attempt;
    no reuse of restarted VM state, volumes, shared skills, SSH forwarding or
    histories. Require exact stateless provider request binding and no prior
    conversation/memory. Provider-side freshness that cannot be observed stays
    UNKNOWN. Qualify only the bounded request/context claim actually supported.
11. **Q11 — receipt custody.** External timestamps, argv, stdout/stderr, exit/timeout,
    request/response bytes, tool bindings, read/write observations and their hashes.
    Frozen expected inputs are controller-authored; actual observations must not
    be substituted with agent declarations or receipts writable by the worker.
12. **Q12 — reset/teardown.** A second fresh worker must not see the first scratch
    marker. Teardown only run-owned resources, check their removal, preserve world
    and failure receipts, and leave unrelated containers, G89 and global settings
    untouched. Use a new attempt identity for any change after exposure.
13. **Q13 — admission.** Return all exact identities and raw receipts to #173.
    Required FAIL, UNKNOWN or NOT_RUN blocks admission. Owner review must admit
    that exact surface; a later CAL pilot remains a separate authorized launch.

## Completed preparation and stop

The proposed manifest, schemas and design are inspectable but have no execution
receipts. Preserve them as a proposal, not as a launcher candidate pass. Resume
first with a separate macOS-capable control artifact and explicit identity;
resolve the unavailable engine and exact adapter/inventory bindings afterward.

No model actor, global host permission change, G89 retry, frozen CAL amendment,
canonical contract change, merge, release or consumer repin occurred.
