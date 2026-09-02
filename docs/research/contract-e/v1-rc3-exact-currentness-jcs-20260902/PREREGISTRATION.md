# Contract E RC3 Exact-Currentness + JCS Successor Preregistration

Status: **FROZEN RESEARCH PREREGISTRATION — NO PRODUCTION AUTHORITY**

Branch: `research/contract-e-v1-rc3-exact-currentness-jcs-20260902`

Base: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`

## 1. Why a successor is justified

This experiment is a true successor. It does not repair or relabel prior candidates.

### RC1 preserved failure

Fresh independent RC1 was terminal `FALSIFIED` at 48/50 normative exact matches with no false permits or false rejects. The two mismatches exposed an underdetermined single AuthorityState identity field on denial receipts. RC1 remains immutable evidence.

### RC2 preserved advances

Later RC2 work supported several narrower improvements:

- separate claimed and recomputed AuthorityState receipt identities;
- RFC 8785 JCS canonicalization plus exactly one trailing LF for identity-bearing bytes;
- non-amplifying linear authority chains;
- supporting artifacts remain non-conferring;
- external root/trusted-origin boundary remains outside Contract E;
- fresh point-of-use evaluation and immutable execution-intent binding survive downstream pressure.

### RC2 preserved falsification

Frozen RC2 candidate `44c919ea7f571b9a01ccf420ac710822c29476e4` and its sealed evaluator were post-seal falsified by exact fractional-currentness discriminator run `33687111732`.

The exact frozen reference blob `fda14bb18c66c51747b7b506abb8df8a55a8d166` produced 0/3 exact matches on schema-admitted >6-digit fractional timestamps:

- request immediately before `valid_from`: false permit;
- request immediately after `valid_until`: false permit;
- request immediately before `revoked_at`: false reject.

The cause was host microsecond truncation through Python `datetime.fromisoformat`. The sealed evaluator lacked a discriminator in that domain. RC2 remains immutable terminal evidence and must not be repaired in place.

## 2. RC3 scientific question

Can the smallest bounded Contract E authority evaluator preserve the strongest supported RC2 semantics while making timestamp currentness exactly recoverable for every timestamp admitted by its public grammar?

## 3. Frozen semantic delta

RC3 MUST preserve the supported authority predicate unless explicitly changed below.

### 3.1 Canonical bytes

All deterministic Contract E JSON identities/hashes use:

1. the RFC 8785 JCS canonicalization domain;
2. RFC 8785 serialization exactly;
3. UTF-8 bytes;
4. exactly one ASCII LF byte appended.

No implementation-local JSON-number rendering, key-ordering, escaping, whitespace, or fallback serializer may substitute.

Raw JSON duplicate member names must be rejected at ingestion when raw text is available. A decoded-dictionary API cannot claim to prove duplicate-free raw input that was discarded upstream.

### 3.2 Dual AuthorityState receipt identity

The receipt fields are frozen as:

- `claimed_authority_state_id`
- `recomputed_authority_state_id`

`claimed_authority_state_id` preserves the supplied state `authority_state_id` only when syntactically valid SHA-256, otherwise null.

`recomputed_authority_state_id` is independently recomputed from the supplied canonicalizable AuthorityState excluding `authority_state_id`, even when the state later fails structural validation; otherwise null.

Both fields are normative receipt semantic-identity inputs. A valid state requires both non-null and equal. Neither field confers authority.

### 3.3 Exact UTC timestamp grammar and ordering

Accepted timestamp grammar remains:

`YYYY-MM-DDTHH:MM:SS[.fraction]Z`

where `fraction` is one or more decimal digits of arbitrary positive precision.

Timestamps MUST be calendar-valid UTC `Z` timestamps. Leap seconds are rejected.

Chronological comparisons MUST preserve the stated fractional precision exactly. They MUST NOT truncate, round, coerce, or otherwise collapse timestamps to host datetime precision.

A correct implementation may compare normalized date/time components and arbitrary-precision fractional digits without using a host datetime object for the fractional comparison.

Currentness is exactly:

- `evaluation_time >= valid_from`;
- if `valid_until` is present, `evaluation_time <= valid_until`;
- if `revoked_at` is present, `evaluation_time < revoked_at`.

`valid_from` and `valid_until` are inclusive. Revocation is effective at and after `revoked_at`.

### 3.4 AuthorityState and delegation

AuthorityState contains exactly one non-branching chain:

- first record is `grant` or `policy`;
- later records are `delegation` only;
- each child names the immediately preceding record and exact parent subject;
- delegation may change subject only;
- domain, operation, scope, target class, and immutable target remain exact;
- all authority-record IDs are unique.

No peer/surplus conferring alternatives, wildcard, alias, group, union, inheritance, containment, narrowing, widening, partial-record synthesis, or Qualification predicate is defined.

### 3.5 Request-local integrity

Request schema is exact and fail-closed.

- reference `ref_id` values are unique;
- each immutable reference identity is recomputed with RC3 canonical bytes;
- jurisdiction target identity resolves to exactly one validated reference;
- supporting-artifact IDs are unique;
- every supporting-artifact `ref_id` resolves request-locally;
- conflict IDs are unique within conflicts;
- residue IDs are unique within residues;
- unknown fields fail closed.

Supporting artifacts never confer authority or repair an invalid AuthorityState.

### 3.6 Blockers

A relevant `unresolved` or `contested` conflict or residue blocks **every supplied request**, including a `resolution/resolve` request carrying that blocker.

RC3 has no request-side discharge field.

A resolution operation can be separately authorized only when its request itself has no relevant unresolved/contested blocker. Applying or proving resolution remains outside Contract E.

### 3.7 Safe preservation

For a structurally valid request, receipt preserved lists are exact deep copies.

For a structurally invalid request, a preserved list may be copied only when the top-level value is a list and every item independently satisfies that list's item shape. Otherwise that list is emitted empty.

Preservation never repairs an invalid request into authorization.

### 3.8 Pipeline/trust boundary

A-D references remain opaque immutable identities.

Contract A identity, Contract B evidence, Contract C epistemic state, Contract D `candidate_for_authorization`, competence material, prior receipts, or execution reports do not become standing Contract E authority.

AuthorityState content identity proves exact content binding, not root legitimacy. Decision content identity proves exact binding, not trusted producer origin.

Trusted-origin requirements belong to a consuming profile/application outside the core Contract E authorization predicate.

Authorization does not establish execution occurrence or verification.

## 4. Required pre-freeze discriminators

RC3 may not freeze unless all of the following pass against the candidate reference.

### 4.1 RC2 fractional-currentness regression

The exact three terminal RC2 discriminator cases must produce:

- `FRACTION-PRE-VALID-FROM`: deny;
- `FRACTION-POST-VALID-UNTIL`: deny;
- `FRACTION-PRE-REVOCATION`: authorize.

Add adjacent cases at equal fractional boundaries and with trailing-zero-equivalent fractions.

### 4.2 JCS canonicalization regression

Exercise at minimum:

- `1.0`;
- `-0.0`;
- small exponent boundary values;
- large integer-valued floats inside JCS domain;
- non-finite numbers;
- out-of-domain numbers;
- Unicode/object-key ordering;
- raw duplicate member rejection through the raw-text ingestion helper.

### 4.3 Dual identity regression

Exercise at minimum:

- valid state: claimed == recomputed;
- syntactically valid forged claim: both non-null and unequal, deny;
- malformed claimed identity: claimed null, recomputed retained when possible, deny;
- canonicalizable structurally invalid state: recomputed retained;
- both identity fields affect receipt semantic identity.

### 4.4 Authority-boundary regression

Exercise subject, domain, operation, scope, target class, target ref, delegation lineage/bounds, currentness/revocation, blocker, support laundering, reference integrity, request-local uniqueness, unknown fields, malformed preservation, surplus peer rejection, and prior-receipt non-conferral.

## 5. Consumer comparison

Before RC3 freeze, compare both:

1. an unchanged RC1/RC2-style receipt consumer where applicable, demonstrating that incompatible receipt schema changes fail closed rather than silently permit;
2. an explicitly migrated consumer that validates both dual identity fields plus request hash/current point-of-use requirements.

Reuse an already-frozen D→E trusted-origin / point-of-use pressure corpus where possible. Any mechanical migration required for the RC3 receipt field names must be preregistered and isolated from the substantive attack expectations.

## 6. Evaluator requirements

A new evaluator must be qualified and sealed **after candidate freeze and before any fresh independent implementation exists**.

Its hidden corpus must include all three terminal fractional-currentness cases and neighboring metamorphic variants.

Seed at minimum these weak implementations:

- claimed-only receipt identity;
- recomputed-only receipt identity;
- host-microsecond timestamp truncator;
- ordinary sorted compact JSON instead of RFC 8785 JCS;
- subject blind;
- currentness blind;
- blocker blind;
- support launderer;
- reference/state identity blind;
- surplus-peer permitter;
- request-local-uniqueness blind;
- preservation dropper.

A weak currentness implementation must produce a recorded false permit or false reject on a hidden exact-fraction case or the evaluator is not qualified.

## 7. Fresh reproduction requirement

Only after evaluator seal may a clean RSH aperture be created from clean RSH main.

The fresh implementer receives only frozen SPEC, schema, and pre-freeze task. It must freeze its implementation/tests before evaluator/reference reveal.

No post-reveal repair may count as the same reproduction.

## 8. Stop/promotion rule

Normal-context success can establish only `SUPPORTED_FOR_FRESH_REPRODUCTION`.

Fresh independent comparison is `SUPPORTED` only with zero normative mismatch, false permit, false reject, exception, preservation failure, and diagnostic-shape failure under the sealed evaluator's stated gate.

Any authority-critical disagreement terminalizes that frozen run. Do not repair it in place.

Production Contract E promotion, tag, or release remains separately owner-authorized and is not authorized by this preregistration.
