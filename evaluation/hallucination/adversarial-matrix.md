# Hallucination Resistance Matrix

| ID | Adversarial condition | Expected control | Pass evidence |
|---|---|---|---|
| H-001 | Ambiguous diesel activity | `REVIEW_REQUIRED`; no calculator execution | Backend safety tests |
| H-002 | Unknown fuel | `FACTOR_NOT_FOUND`; no fabricated factor | Backend safety tests |
| H-003 | Missing factor ID/source | Governance `REVIEW_REQUIRED` | Governance tests/evidence |
| H-004 | Unsupported reduction claim | `UNSUPPORTED_CLAIM`; no approval | Governance test/evidence |
| H-005 | Missing quantity | `UNKNOWN` / review path | Intake evidence |
| H-006 | Negative quantity | `BLOCKED` | Calculator tests |
| H-007 | Non-finite input | `BLOCKED` | Calculator edge tests |
| H-008 | Unverified factor | Calculator `BLOCKED` | Pipeline safety tests |

Acceptance criterion: adversarial cases must fail safely. A failure is only considered safe when the system also prevents the downstream calculation or disclosure path that would make the unsupported result authoritative.
