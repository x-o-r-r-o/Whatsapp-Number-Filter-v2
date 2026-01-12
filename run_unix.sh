#!/usr/bin/env bash
set -euo pipefail

# =====================================================
# whatsapp-filter - macOS/Linux run helper (ALL VARIANTS)
# =====================================================

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo
echo "=========================================="
echo " whatsapp-filter - Run Helper (macOS/Linux)"
echo "=========================================="
echo "Project root: $PROJECT_ROOT"
echo

if [ ! -d ".venv" ]; then
  echo "[ERROR] .venv not found. Create venv and install package first."
  echo "  python3 -m venv .venv"
  echo "  source .venv/bin/activate"
  echo "  pip install -e ."
  exit 1
fi

# shellcheck disable=SC1091
source ".venv/bin/activate"

main_menu() {
  echo
  echo "=========================================="
  echo " MAIN MENU"
  echo "=========================================="
  echo "  1) Use config.yaml (no overrides)"
  echo "  2) Override HEADLESS only"
  echo "  3) Override MODE only"
  echo "  4) Override MODE + HEADLESS"
  echo "  5) Override MODE + THREADS (+ CHUNK for threaded)"
  echo "  6) Override INPUT / OUTPUT paths"
  echo "  7) SHOW EXAMPLES (print commands only)"
  echo "  8) EXIT"
  echo

  read -r -p "Enter choice [1-8]: " MAIN_CHOICE

  case "$MAIN_CHOICE" in
    1) use_config_only ;;
    2) override_headless ;;
    3) override_mode ;;
    4) override_mode_headless ;;
    5) override_mode_threads ;;
    6) override_io ;;
    7) show_examples ;;
    8) echo "[INFO] Exiting."; exit 0 ;;
    *) echo "[WARN] Invalid choice."; main_menu ;;
  esac
}

use_config_only() {
  echo
  echo "[INFO] Running: whatsapp-filter"
  echo
  whatsapp-filter
}

override_headless() {
  echo
  echo "=========================================="
  echo " OVERRIDE HEADLESS"
  echo "=========================================="
  echo "  1) Headless ON   ( --headless )"
  echo "  2) Headless OFF  ( no flag, use config.yaml )"
  echo "  3) Back"
  echo

  read -r -p "Enter choice [1-3]: " H_CHOICE

  case "$H_CHOICE" in
    1)
      echo
      echo "[INFO] Running: whatsapp-filter --headless"
      echo
      whatsapp-filter --headless
      ;;
    2)
      echo
      echo "[INFO] Running: whatsapp-filter (no headless override)"
      echo
      whatsapp-filter
      ;;
    *)
      main_menu
      ;;
  esac
}

override_mode() {
  echo
  echo "=========================================="
  echo " OVERRIDE MODE ONLY"
  echo "=========================================="
  echo "  1) single"
  echo "  2) onedriver"
  echo "  3) threaded"
  echo "  4) Back"
  echo

  read -r -p "Enter choice [1-4]: " M_CHOICE

  case "$M_CHOICE" in
    1)
      echo
      echo "[INFO] Running: whatsapp-filter --mode single"
      echo
      whatsapp-filter --mode single
      ;;
    2)
      echo
      echo "[INFO] Running: whatsapp-filter --mode onedriver"
      echo
      whatsapp-filter --mode onedriver
      ;;
    3)
      echo
      echo "[INFO] Running: whatsapp-filter --mode threaded"
      echo "[NOTE] For best results, run single mode once first to create a logged-in profile."
      echo
      whatsapp-filter --mode threaded
      ;;
    *)
      main_menu
      ;;
  esac
}

override_mode_headless() {
  echo
  echo "=========================================="
  echo " OVERRIDE MODE + HEADLESS"
  echo "=========================================="
  echo "  1) single, headless"
  echo "  2) onedriver, headless"
  echo "  3) threaded, headless"
  echo "  4) Back"
  echo

  read -r -p "Enter choice [1-4]: " MH_CHOICE

  case "$MH_CHOICE" in
    1)
      echo
      echo "[INFO] Running: whatsapp-filter --mode single --headless"
      echo
      whatsapp-filter --mode single --headless
      ;;
    2)
      echo
      echo "[INFO] Running: whatsapp-filter --mode onedriver --headless"
      echo
      whatsapp-filter --mode onedriver --headless
      ;;
    3)
      echo
      echo "[INFO] Running: whatsapp-filter --mode threaded --headless"
      echo "[NOTE] For best results, run single mode once first to create a logged-in profile."
      echo
      whatsapp-filter --mode threaded --headless
      ;;
    *)
      main_menu
      ;;
  esac
}

override_mode_threads() {
  echo
  echo "=========================================="
  echo " OVERRIDE MODE + THREADS (+ CHUNK)"
  echo "=========================================="
  echo "  1) onedriver, threads=4"
  echo "  2) onedriver, custom threads"
  echo "  3) threaded, threads=4, chunk=50"
  echo "  4) threaded, custom threads + chunk"
  echo "  5) Back"
  echo

  read -r -p "Enter choice [1-5]: " MT_CHOICE

  case "$MT_CHOICE" in
    1)
      echo
      echo "[INFO] Running: whatsapp-filter --mode onedriver --threads 4"
      echo
      whatsapp-filter --mode onedriver --threads 4
      ;;
    2)
      read -r -p "Enter threads (e.g. 4): " T
      echo
      echo "[INFO] Running: whatsapp-filter --mode onedriver --threads $T"
      echo
      whatsapp-filter --mode onedriver --threads "$T"
      ;;
    3)
      echo
      echo "[INFO] Running: whatsapp-filter --mode threaded --threads 4 --chunk-size 50"
      echo "[NOTE] For best results, run single mode once first to create a logged-in profile."
      echo
      whatsapp-filter --mode threaded --threads 4 --chunk-size 50
      ;;
    4)
      read -r -p "Enter threads (e.g. 4): " T
      read -r -p "Enter chunk size (e.g. 50): " C
      echo
      echo "[INFO] Running: whatsapp-filter --mode threaded --threads $T --chunk-size $C"
      echo "[NOTE] For best results, run single mode once first to create a logged-in profile."
      echo
      whatsapp-filter --mode threaded --threads "$T" --chunk-size "$C"
      ;;
    *)
      main_menu
      ;;
  esac
}

override_io() {
  echo
  echo "=========================================="
  echo " OVERRIDE INPUT / OUTPUT"
  echo "=========================================="

  read -r -p "Input file [default: data/input_numbers.txt]: " IN_PATH
  IN_PATH=${IN_PATH:-data/input_numbers.txt}

  read -r -p "Valid output [default: data/valid_numbers.txt]: " OUT_VALID
  OUT_VALID=${OUT_VALID:-data/valid_numbers.txt}

  read -r -p "Invalid output [default: data/invalid_numbers.txt]: " OUT_INVALID
  OUT_INVALID=${OUT_INVALID:-data/invalid_numbers.txt}

  echo
  echo "[INFO] You can also add extra options (headless/mode/etc.)"
  read -r -p "Extra options (e.g. --headless --mode threaded --threads 4 --chunk-size 50): " EXTRA

  echo
  echo "[INFO] Running:"
  echo "  whatsapp-filter -i \"$IN_PATH\" --valid-output \"$OUT_VALID\" --invalid-output \"$OUT_INVALID\" $EXTRA"
  echo

  # shellcheck disable=SC2086
  whatsapp-filter -i "$IN_PATH" --valid-output "$OUT_VALID" --invalid-output "$OUT_INVALID" $EXTRA
}

show_examples() {
  echo
  echo "=========================================="
  echo " COMMAND EXAMPLES"
  echo "=========================================="
  echo
  echo "Normal:"
  echo "  whatsapp-filter"
  echo
  echo "Headless:"
  echo "  whatsapp-filter --headless"
  echo
  echo "Modes:"
  echo "  whatsapp-filter --mode single"
  echo "  whatsapp-filter --mode onedriver"
  echo "  whatsapp-filter --mode threaded"
  echo
  echo "Modes + threads/chunk:"
  echo "  whatsapp-filter --mode onedriver --threads 4"
  echo "  whatsapp-filter --mode threaded --threads 4 --chunk-size 50"
  echo
  echo "Headless + modes:"
  echo "  whatsapp-filter --mode single --headless"
  echo "  whatsapp-filter --mode onedriver --threads 4 --headless"
  echo "  whatsapp-filter --mode threaded --threads 4 --chunk-size 50 --headless"
  echo
  echo "IO overrides:"
  echo "  whatsapp-filter -i data/my_numbers.txt --valid-output data/my_valid.txt --invalid-output data/my_invalid.txt"
  echo "  whatsapp-filter -i data/my_numbers.txt --valid-output data/my_valid.txt --invalid-output data/my_invalid.txt --mode threaded --threads 4 --chunk-size 50 --headless"
  echo
  main_menu
}

main_menu