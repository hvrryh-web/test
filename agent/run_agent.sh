#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

VENV_PATH="/home/agent/venv"
if [ -d "$VENV_PATH" ]; then
  source "$VENV_PATH/bin/activate"
elif [ -d "$PROJECT_DIR/.venv" ]; then
  source "$PROJECT_DIR/.venv/bin/activate"
fi

python "$PROJECT_DIR/agent/agent_runner.py" --process-tasks
