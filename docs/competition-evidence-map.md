# Competition Evidence Map

This document maps the implemented CarbonGuard controls to the four judging pillars without claiming regulatory certification or guaranteed results.

| Judging pillar | Evidence in repository | Demonstration |
|---|---|---|
| Lyzr Architecture & Tool Calling | `agents/`, `LYZR_USAGE.md`, `ARCHITECTURE.md` | Show five-agent SuperFlow and deterministic OpenAPI handoff |
| Emission Calculation Accuracy | `backend/factor-api/`, `backend/calculator-api/`, `tests/backend/` | Run exact diesel and electricity cases; show calculator is blocked for unresolved factors |
| Auditability & Traceability | `docs/audit-lineage.md`, governance/disclosure agent configs, dashboard audit trail | Trace source record → factor → formula → result → governance |
| Sustainability Dashboard UX | `frontend/`, dashboard screenshots/demo | Submit an activity and show governance state plus audit evidence |

## High-value failure demonstration

Use an intentionally ambiguous activity such as `Diesel` without enough context. The expected path is:

`REVIEW_REQUIRED → calculator not authorized → disclosure not approved`

This demonstrates the fail-closed boundary directly.

## Verified positive demonstration

Use the exact tested 2026 diesel record:

- Scope 1
- Diesel (100% mineral diesel)
- 2500 litres
- 2026
- Liquid fuels
- diesel subtype

Expected deterministic factor: `2.66155 kg CO2e/litre`.
Expected result: `6.653875 tCO2e`.

## Claim discipline

Do not describe the application as certified or regulator-compliant unless the competition specifically requires and independently substantiates such a claim. Use `ISO 14064-3 aligned` where the dashboard needs a concise methodology label.
