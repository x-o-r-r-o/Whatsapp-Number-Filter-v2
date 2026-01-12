#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

[ -d ".venv" ] || { echo "[ERROR] .venv not found."; exit 1; }
# shellcheck disable=SC1091
source ".venv/bin/activate"

THREADS=4

echo "[INFO] Running onedriver mode with $THREADS threads (visible browser)"
echo

whatsapp-filter --mode onedriver --threads "$THREADS"