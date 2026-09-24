from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md",
    "ARCHITECTURE.md",
    "SECURITY.md",
    "EVALUATION.md",
    "TEST_RESULTS.md",
    "agents/carbonguard-esg-superflow.json",
    "backend/factor-api/factors.json",
    "backend/factor-api/requirements.txt",
    "backend/calculator-api/requirements.txt",
    "frontend/package.json",
    "frontend/src/services/__tests__/superflowMapper.test.ts",
    "tests/backend/test_api_contract.py",
    "tests/backend/test_safety_invariants.py",
    ".github/workflows/ci.yml",
]

missing = [p for p in REQUIRED if not (ROOT / p).exists()]
if missing:
    print("Missing required files:", *missing, sep="\n- ")
    sys.exit(1)

for path in ROOT.rglob("*.json"):
    if any(part in {"node_modules", ".git", "dist", "build"} for part in path.parts):
        continue
    json.loads(path.read_text(encoding="utf-8"))

# Catch common accidental secret assignments in source/config files.
pattern = re.compile(
    r"(?:api[_-]?key|secret|password|token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{20,}['\"]",
    re.I,
)
for path in ROOT.rglob("*"):
    if not path.is_file() or any(part in {".git", "node_modules", "dist", "build", "evaluation"} for part in path.parts):
        continue
    if path.suffix in {".json", ".py", ".ts", ".tsx", ".js", ".yaml", ".yml", ".env"}:
        try:
            if pattern.search(path.read_text(encoding="utf-8")):
                print(f"Potential hard-coded secret assignment: {path.relative_to(ROOT)}")
                sys.exit(1)
        except UnicodeDecodeError:
            pass

print("Repository static verification: PASS")
