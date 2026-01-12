#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Activate venv
if [ ! -d ".venv" ]; then
  echo "[ERROR] .venv not found."
  exit 1
fi
# shellcheck disable=SC1091
source ".venv/bin/activate"

# Customize these paths if you want:
IN="data/input_numbers.txt"
OUT_VALID="data/valid_numbers.txt"
OUT_INVALID="data/invalid_numbers.txt"

# Customize these performance settings:
THREADS=4
CHUNK=50

echo "[INFO] Running threaded + headless with custom IO"
echo "  Input:          $IN"
echo "  Valid output:   $OUT_VALID"
echo "  Invalid output: $OUT_INVALID"
echo "  Threads:        $THREADS"
echo "  Chunk size:     $CHUNK"
echo

whatsapp-filter \
  -i "$IN" \
  --valid-output "$OUT_VALID" \
  --invalid-output "$OUT_INVALID" \
  --mode threaded \
  --threads "$THREADS" \
  --chunk-size "$CHUNK" \
  --headless