# CarbonGuard Submission Checklist

## Lyzr

- [ ] Five agents are present in Lyzr Agent Studio.
- [ ] SuperFlow uses the intended production workflow.
- [ ] Agent/tool permissions match the repository documentation.
- [ ] Any exposed webhook secret has been regenerated.
- [ ] No Lyzr API key or webhook secret is committed.

## Deterministic accounting

- [ ] Factor source/version is identified.
- [ ] Factor lookup requires deterministic compatibility constraints.
- [ ] Ambiguous factors return `REVIEW_REQUIRED`.
- [ ] Unknown factors return `FACTOR_NOT_FOUND`.
- [ ] Calculator requires `VERIFIED`.
- [ ] Formula and factor provenance are retained.

## Governance

- [ ] Missing evidence cannot become disclosure-ready.
- [ ] Unsupported reduction claims are blocked/reviewed.
- [ ] Source record IDs are preserved.
- [ ] Scope 3 is not presented as zero when no Scope 3 activity was reported.
- [ ] "ISO 14064-3 aligned" is not represented as formal certification/compliance.

## Repository

- [ ] Backend tests pass locally.
- [ ] Python compilation passes.
- [ ] GitHub Actions CI is green.
- [ ] Frontend typecheck/tests/build pass in CI.
- [ ] No secrets are present in tracked files or screenshots.
- [ ] README claims are supported by repository evidence.
- [ ] Demo shows one approved path and one fail-closed path.
