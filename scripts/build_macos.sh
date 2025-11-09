#!/usr/bin/env bash
set -euo pipefail

# Thin wrapper for macOS build.
# Delegates all logic to the unified Python orchestrator:
#   python -m scripts.build --target macos --component all

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." &>/dev/null && pwd)"

cd "$REPO_ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "[build-macos] Using Python: $PYTHON_BIN"
echo "[build-macos] Invoking orchestrator for macOS (all components)"

"$PYTHON_BIN" -m scripts.build --target macos --component all

echo "[build-macos] Completed. Artifacts are under ./build"