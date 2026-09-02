# RC2 canonicalization probe registration

The probe workflow was added after the first probe-source commit. This no-op research record creates a subsequent branch event so the now-registered workflow executes against the exact branch state containing `canonicalization_probe.py`.

The probe is a discriminator, not a repair. A serializer divergence is preserved as evidence against freezing the current RC2 canonicalization semantics.
