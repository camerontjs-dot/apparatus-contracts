# Contract D RC6 Change Note

RC6 is a research-only successor to RC5. It exists solely to resolve the `PUBLIC_AUTHORITY_AMBIGUITY` preserved by the fresh RC5 independent reproduction at `camerontjs-dot/research-scaffold-harness@39b75abb98b073517c12e08490640facaa764746` (`FINAL_RECORD.md` blob `524c0825e1e8af17bcb79117ab97cdde1e820d51`).

RC5 remains terminal `INCONCLUSIVE` / `INDEPENDENT_REPRODUCTION_INCONCLUSIVE`; this successor does not rewrite that result.

## Smallest change

- research token changes from `0.3.0-rc5` to `0.3.0-rc6`;
- all RC5 public semantics are immutably incorporated by reference from SPEC blob `57fa4ca59efced5e35115551b1aa57dbbc7f6b2c`;
- normalized registered effects are now explicitly required to have exactly `type`, `version`, and `params`;
- for empty parameter schemas, normalized `params` is explicitly `{}` and remains present in semantic projection and identity;
- external requested-parameter semantics are unchanged;
- reference implementation logic is unchanged except exact candidate version identity/documentation because RC5 already returned the total normalized shape;
- focused regression tests lock the clarified representation and identity behavior for `knowledge.cite_as_evidence@1`, `task.dispatch@1`, and the existing defaulted `knowledge.add_verified_tag@1` behavior.

No Authorization, execution, producer, policy, effect-registry, canonicalization, numeric-domain, Unicode, depth, or consumer-outcome semantics are changed.

This candidate is not production authority and does not authorize Contract D `1.0.0` promotion, merge, tag, or release.
