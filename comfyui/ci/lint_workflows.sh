#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
WORKFLOW_DIR="$ROOT_DIR/workflows"

python - <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(__file__).resolve().parents[1] / "workflows"
errors = []
for path in sorted(root.glob("*.json")):
    try:
        json.loads(path.read_text())
    except Exception as exc:  # pragma: no cover - validation check
        errors.append((path.name, str(exc)))

if errors:
    for name, err in errors:
        print(f"Invalid JSON: {name}: {err}")
    sys.exit(1)
else:
    print(f"Validated {len(list(root.glob('*.json')))} workflow(s)")
PY
