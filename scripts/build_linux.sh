#!/usr/bin/env bash
set -euo pipefail

# Thin wrapper for Linux build.
# Delegates all logic to the unified Python orchestrator:
#   python -m scripts.build --target linux --component all

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." &>/dev/null && pwd)"

cd "$REPO_ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "[build-linux] Using Python: $PYTHON_BIN"
echo "[build-linux] Invoking orchestrator for Linux (all components)"

"$PYTHON_BIN" -m scripts.build --target linux --component all

echo "[build-linux] Completed. Artifacts are under ./build"