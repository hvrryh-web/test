#!/usr/bin/env bash
set -euxo pipefail

# Create local virtual environment and install requirements
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Bootstrapped local Python environment in .venv. To use, run: source .venv/bin/activate"
