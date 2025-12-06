#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$SCRIPT_DIR"
export COMFYUI_API_URL="${COMFYUI_API_URL:-http://localhost:8188}"
PORT="${FACADE_PORT:-8000}"

if ! command -v uvicorn >/dev/null 2>&1; then
  echo "uvicorn not found. Install dependencies: pip install fastapi httpx uvicorn" >&2
  exit 1
fi

cd "$SCRIPT_DIR"
uvicorn api_facade:app --host 0.0.0.0 --port "$PORT"
