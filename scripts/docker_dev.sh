#!/usr/bin/env bash
# Build and run docker-compose for local development
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

# Build and start
docker compose up -d --build

echo "Docker services started."
