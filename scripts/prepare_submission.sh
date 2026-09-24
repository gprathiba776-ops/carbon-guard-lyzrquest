#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

command -v python >/dev/null || { echo "Python is required." >&2; exit 1; }
command -v npm >/dev/null || { echo "npm is required." >&2; exit 1; }

cd "$ROOT"

if [[ ! -f frontend/package-lock.json ]]; then
  echo "Generating frontend/package-lock.json..."
  (cd frontend && npm install --package-lock-only --ignore-scripts --no-audit --no-fund)
fi

[[ -s frontend/package-lock.json ]] || { echo "frontend/package-lock.json was not generated." >&2; exit 1; }

python scripts/verify_repo.py
python -m compileall -q backend tests
python -m unittest discover -s tests -p 'test_*.py' -v

(cd frontend && npm install --no-audit --no-fund)
(cd frontend && npm run typecheck)
(cd frontend && npm test -- --run)
(cd frontend && npm run build)

echo "CarbonGuard submission verification: PASS"
