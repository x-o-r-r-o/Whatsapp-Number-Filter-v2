#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

[ -d ".venv" ] || { echo "[ERROR] .venv not found."; exit 1; }
# shellcheck disable=SC1091
source ".venv/bin/activate"

echo "[INFO] Running single mode (visible browser, config IO)"
echo

whatsapp-filter --mode single