# CarbonGuard Adversarial Evaluation

These cases intentionally provide ambiguous, incomplete, unsupported, or invalid inputs.
CarbonGuard must fail closed rather than inventing evidence or numerical values.

| Case | Expected outcome |
|---|---|
| Ambiguous diesel factor | `REVIEW_REQUIRED` |
| Unknown factor | `FACTOR_NOT_FOUND` |
| Missing audit evidence | `REVIEW_REQUIRED` |
| Unsupported reduction claim | `UNSUPPORTED_CLAIM` / blocked disclosure |
| Missing quantity | `UNKNOWN` / review path |
| Invalid numerical input | `BLOCKED` |
| Unverified factor | Calculator must not execute |

## Core invariants

1. No unverified factor can produce an authoritative calculation.
2. No unsupported sustainability claim can become disclosure-ready.
3. Missing evidence cannot be silently replaced with an assumption.
4. Source record identifiers must remain unchanged through the pipeline.
