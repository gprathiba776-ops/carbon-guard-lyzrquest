# Automated Test Evidence

CarbonGuard uses executable tests to enforce the numerical safety boundary.

## Coverage areas

- deterministic factor resolution
- ambiguous and unknown factor handling
- exact Scope 1 diesel calculation
- exact Scope 2 electricity calculation
- factor-to-calculator pipeline contract
- provenance preservation before calculation
- fail-closed calculator statuses
- zero quantity
- boolean/non-numeric inputs
- non-finite inputs
- frontend governance-state mapping

Run locally:

```bash
python -m compileall -q backend tests
python -m unittest discover -s tests -p "test_*.py" -v
```

The GitHub Actions workflow repeats the backend suite and adds frontend type-check, tests, build, and repository secret scanning.
