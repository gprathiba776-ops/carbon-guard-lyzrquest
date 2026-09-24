# Frontend Dependency Reproducibility

The dashboard uses npm with exact dependency versions in `package.json`. CI installs the declared dependency graph and runs type-checking, lint/type gates, tests and a production build.

## Lockfile status

The final submission should include a generated `package-lock.json` created in an online development environment with: `npm install --package-lock-only`. This build environment did not have access to the npm registry, so a valid lockfile could not be generated without fabricating dependency metadata.

Until the lockfile is committed, CI intentionally uses `npm install` rather than `npm ci`.
