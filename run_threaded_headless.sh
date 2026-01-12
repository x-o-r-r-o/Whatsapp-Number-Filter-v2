#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

[ -d ".venv" ] || { echo "[ERROR] .venv not found."; exit 1; }
# shellcheck disable=SC1091
source ".venv/bin/activate"

THREADS=4
CHUNK=50

echo "[INFO] Running threaded + headless (default IO)"
echo "  Threads:    $THREADS"
echo "  Chunk size: $CHUNK"
echo

whatsapp-filter --mode threaded --threads "$THREADS" --chunk-size "$CHUNK" --headless