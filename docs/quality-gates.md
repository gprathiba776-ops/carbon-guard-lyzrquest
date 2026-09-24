# CarbonGuard Quality Gates

CarbonGuard separates product behavior from evidence about that behavior. The repository continuously checks the engineering invariants that protect the deterministic control boundary.

## Automated gates

1. **Python correctness** — compilation and deterministic unit/regression tests.
2. **Pipeline safety** — only `VERIFIED` factors can reach authoritative calculation.
3. **Configuration validation** — service settings are validated through Pydantic Settings.
4. **Frontend integrity** — TypeScript checks, Vitest tests and production build.
5. **Container integrity** — CI builds all three production images.
6. **Repository security** — tracked-file secret assignment scan and secret-file tracking check.
7. **Observability** — JSON logs, request IDs and standardized error contracts are implemented at service boundaries.

## CI behavior

GitHub Actions runs on pushes and pull requests to `main`/`master`. It executes backend tests on Python 3.11 and 3.12, frontend checks, then builds the factor API, calculator API and dashboard images.

## Dependency policy

Python service dependencies are pinned in each service's `requirements.txt`. Frontend dependency versions are pinned exactly in `package.json`. A real npm lockfile should be generated and committed from an online development environment before final submission; this archive was prepared in an offline environment where npm registry metadata was unavailable.

## Evidence boundary

These gates prove repository engineering invariants. They do not by themselves establish regulatory compliance or certify an ESG disclosure.
