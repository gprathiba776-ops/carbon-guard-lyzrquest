# CarbonGuard — Competition Repository Hardening Report

This archive is the submission-oriented hardened repository built from the CarbonGuard main repository.

## Engineering controls strengthened

### Testing
- Expanded deterministic backend suite to **32 locally passing tests**.
- Factor boundary/regression coverage.
- Calculator numerical edge cases.
- Configuration validation tests.
- Factor → calculator pipeline contract tests.
- Fail-closed safety invariant tests.

### CI/CD
- GitHub Actions backend matrix for Python 3.11/3.12.
- Frontend type-check, lint/type gate, tests and production build.
- Docker image builds for factor API, calculator API and dashboard.
- Tracked-file secret scan and secret-file tracking check.
- Read-only workflow permissions.

### Configuration management
- Pydantic Settings validates ports, log levels, registry path and factor year.
- Environment aliases support local and deployment platforms.
- Python dependencies are pinned exactly.

### Observability
- Dependency-free JSON structured logging for both Python microservices.
- Request IDs are generated/propagated and returned in `X-Request-ID`.
- Request duration, route and status are logged.
- Standardized error codes are returned for invalid JSON, missing fields, payload size, missing routes and internal errors.
- Frontend SuperFlow proxy emits structured JSON logs and exposes health/readiness endpoints.

### Production readiness
- Health/readiness endpoints.
- Docker health checks.
- Non-root container users.
- Request size limits.
- Upstream timeout handling.
- Server-controlled workflow routing so clients cannot override `WORKFLOW_ID`.
- Render start commands bind to the platform-provided `$PORT`.

### Code quality
- Factor matching remains decomposed into deterministic stages.
- Calculator validation remains centralized and fail-closed.
- The core Lyzr → deterministic-tool control boundary is unchanged.

## Locally verified in this preparation environment

```text
Python compilation: PASS
Backend tests: 32/32 PASS
JSON validation: PASS
YAML validation: PASS
Previously exposed webhook secret search: PASS
```

Docker image builds and the frontend production build are configured in CI but were not claimed as locally executed because this preparation environment did not provide Docker and could not reach the npm registry.

## Final submission actions

1. From an online environment, generate and commit a real `frontend/package-lock.json` using `npm install --package-lock-only`.
2. Run GitHub Actions and retain a successful CI run as evidence.
3. Regenerate any Lyzr SuperFlow webhook secret that was previously exposed.
4. Never commit Lyzr/model-provider secrets or webhook secrets.
5. Confirm the live dashboard still reaches the existing SuperFlow webhook after deployment.
