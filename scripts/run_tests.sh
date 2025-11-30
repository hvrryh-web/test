#!/usr/bin/env bash
set -euxo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

# Activate venv if present
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
fi

# Run tests
pytest -q
