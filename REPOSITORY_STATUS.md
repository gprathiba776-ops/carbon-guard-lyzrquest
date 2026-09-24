# Repository Status

## Submission-oriented engineering state

CarbonGuard is intentionally kept as a hybrid Lyzr + deterministic-tool architecture. No redesign is required for the current competition target.

### Implemented controls

- Five specialized Lyzr agents.
- Lyzr SuperFlow orchestration.
- Deterministic emission-factor lookup.
- Deterministic emissions calculator.
- Fail-closed unresolved-factor behavior.
- Governance and disclosure gates.
- Audit lineage documentation.
- Pydantic-validated environment configuration.
- Health/readiness endpoints.
- Request IDs and structured JSON logging.
- Standardized API error contracts.
- Backend safety and edge-case regression tests.
- Frontend governance-mapping tests.
- GitHub Actions backend/frontend/container quality gates.
- Repository secret-assignment scan.
- Docker health checks and non-root runtime users.
- Server-controlled SuperFlow workflow routing.

### Verification boundary

Locally verified in the preparation environment: Python compilation, deterministic backend test suite and repository static checks. Docker images and frontend production build are configured in CI but were not claimed as locally executed because Docker/npm registry access was unavailable in the preparation environment.

### Final submission requirements

1. Generate and commit `frontend/package-lock.json` from an online environment.
2. Run GitHub Actions successfully and retain the successful CI run as evidence.
3. Regenerate any Lyzr SuperFlow webhook secret that was previously exposed.
4. Never commit Lyzr/model-provider secrets or webhook secrets.
