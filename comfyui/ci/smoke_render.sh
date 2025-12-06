#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
COMPOSE_FILE="$ROOT_DIR/docker/docker-compose.yaml"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required for smoke rendering" >&2
  exit 1
fi

pushd "$ROOT_DIR/docker" >/dev/null
COMFYUI_MODELS_DIR="${COMFYUI_MODELS_DIR:-$ROOT_DIR/models}" docker compose -f "$COMPOSE_FILE" up -d --build
trap 'COMFYUI_MODELS_DIR="${COMFYUI_MODELS_DIR:-$ROOT_DIR/models}" docker compose -f "$COMPOSE_FILE" down; popd >/dev/null' EXIT

for _ in {1..30}; do
  if curl -fsS http://localhost:8188/ >/dev/null 2>&1; then
    echo "ComfyUI is responding; ready for workflow smoke tests."
    exit 0
  fi
  sleep 2
done

echo "ComfyUI failed to start in time" >&2
exit 1
