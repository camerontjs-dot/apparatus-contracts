# RC3 Frozen Integration Pressure Reuse

Status: **preregistered before RC3 integration execution**

RC3 will reuse the strongest later RC2 trusted-origin / point-of-use integration machinery byte-for-byte where it is compatible with the RC3 core interface.

Frozen source candidate: `44c919ea7f571b9a01ccf420ac710822c29476e4`.

Exact source blobs:

- `integration_profile.py`: `6f19875d4f21765e02d51fef50ca53fae3daf177`
- `test_integration_profile.py`: `7c84806033a80b93c08d51492dce265a29dc2b40`
- `run_integration_superset.py`: `8cd53b679f39f6b08a5184eb3133f3c7d610eb2c`

These three blobs will be copied unchanged into the RC3 research directory. They import the colocated candidate `reference.py`, so they will exercise RC3 while preserving the previous attack corpus and consuming-profile logic.

No substantive expected outcome may be rewritten merely because RC3 is a successor.

The reused profile remains a consuming profile, not core Contract E semantics. It tests externally supplied trusted Decision/AuthorityState identities, exact Contract D applicability, fresh point-of-use E evaluation, non-conferring D support, prior-receipt non-conferral, and immutable ExecutionIntent binding.

Acceptance requires the frozen corpus to pass without altering these three source blobs. A failure caused by an intentional RC3 semantic correction must be preserved and classified before any compatibility adaptation is considered.
