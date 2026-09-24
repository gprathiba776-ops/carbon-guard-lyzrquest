test-python:
	python -m unittest discover -s tests -p 'test_*.py' -v

lint-python:
	python -m compileall -q backend tests

frontend-install:
	cd frontend && npm install --no-audit --no-fund

frontend-check:
	cd frontend && npm run typecheck && npm run lint && npm test && npm run build

security-scan:
	git grep -nEi 'api[_-]?key|secret|password|token|authorization|bearer' -- ':!*.lock' ':!evaluation/**' || true

quality-gate: lint-python test-python

container-build:
	docker build -t carbonguard-factor-api:local ./backend/factor-api
	docker build -t carbonguard-calculator-api:local ./backend/calculator-api
	docker build -t carbonguard-dashboard:local ./frontend

verify-repo:
	python scripts/verify_repo.py
