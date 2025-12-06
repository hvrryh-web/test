#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODELS_DIR="${COMFYUI_MODELS_DIR:-$(cd "$SCRIPT_DIR/.." && pwd)/models}"
CHECKSUM_FILE="${CHECKSUM_FILE:-$SCRIPT_DIR/checksums.txt}"

mkdir -p "$MODELS_DIR"

while read -r sha path url; do
  [[ -z "$sha" || "$sha" =~ ^# ]] && continue
  target="$MODELS_DIR/$path"
  mkdir -p "$(dirname "$target")"
  echo "Downloading $url -> $target"
  curl -L --retry 3 --retry-delay 2 "$url" -o "$target"
  echo "$sha  $target" | sha256sum --check --status
  echo "✓ Verified $path"
done < "$CHECKSUM_FILE"
