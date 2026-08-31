# Contract D RC5 hardening change note

RC5 is a research-only successor to frozen RC4. It exists because the Contract-D adversarial harness found canonicalization/interoperability defects outside the previously successful authority-semantic comparison.

## Triggering evidence

Pinned RC4 adversarial run `33354076141` demonstrated:

- escaped unpaired surrogate input could validate and reach `candidate_for_authorization` while canonicalization raised `UnicodeEncodeError`;
- Python and Node disagreed on canonical bytes for multiple finite-number values;
- Python code-point key ordering and JavaScript UTF-16 key ordering disagreed for non-BMP object keys;
- earlier run `33348246947` showed deep finite diagnostics eventually leaking raw `RecursionError` with runtime-dependent boundaries.

## Bounded RC5 change

RC5 preserves Decision authority semantics and changes only the JSON/canonicalization/processing boundary:

1. RFC 8785/JCS canonical payload, plus Contract-D trailing LF framing;
2. valid Unicode scalar strings only; lone surrogates fail closed;
3. safe interoperable integer domain and finite binary64 floats;
4. deterministic maximum container depth 128;
5. runtime/canonicalization failures translated into Contract-D failures rather than raw host exceptions;
6. malformed external applicability expectation containers fail closed rather than acquiring meaning through truthiness or partial-key matching.

## Explicit non-change

No change is intended to:

- CLEAR/HOLD/evaluation-failure semantics;
- upstream/policy/target binding;
- effect registry or stored-effect defaults;
- requested-operation/parameter applicability for conforming callers;
- semantic authority projection except the explicit candidate version token;
- Authorization or execution boundaries.

RC4 remains immutable evidence and is not rewritten by this successor.
