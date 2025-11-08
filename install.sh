#!/usr/bin/env bash

# LifeLine Installer Entry Point
# Delegates to scripts/install_lifeline.sh (Python/uv installer)

set -euo pipefail

# If we're in the repo, use the local installer
if [ -f "scripts/install_lifeline.sh" ]; then
  exec bash scripts/install_lifeline.sh "$@"
fi

# Otherwise, download and run from GitHub
REPO_URL="${LIFELINE_REPO_URL:-https://github.com/pc-style/lifeline.git}"
REPO_BRANCH="${LIFELINE_BRANCH:-main}"

TEMP_DIR="/tmp/lifeline-install-$$"
cleanup() {
  rm -rf "$TEMP_DIR"
}
trap cleanup EXIT INT TERM

printf "Downloading LifeLine installer...\n"

if command -v git >/dev/null 2>&1; then
  git clone --depth 1 --branch "$REPO_BRANCH" "$REPO_URL" "$TEMP_DIR" 2>/dev/null || {
    printf "git clone failed, trying archive...\n"
    rm -rf "$TEMP_DIR"
  }
fi

if [ ! -d "$TEMP_DIR" ]; then
  ARCHIVE_URL="${REPO_URL%.git}/archive/refs/heads/${REPO_BRANCH}.tar.gz"
  ARCHIVE_FILE="/tmp/lifeline-archive-$$.tar.gz"
  
  if command -v curl >/dev/null 2>&1; then
    curl -sL "$ARCHIVE_URL" -o "$ARCHIVE_FILE" || exit 1
  elif command -v wget >/dev/null 2>&1; then
    wget -q -O "$ARCHIVE_FILE" "$ARCHIVE_URL" || exit 1
  else
    echo "Need curl or wget to download" >&2
    exit 1
  fi
  
  mkdir -p "$TEMP_DIR"
  tar -xzf "$ARCHIVE_FILE" -C "$TEMP_DIR" --strip-components=1
  rm -f "$ARCHIVE_FILE"
fi

if [ -f "$TEMP_DIR/scripts/install_lifeline.sh" ]; then
  chmod +x "$TEMP_DIR/scripts/install_lifeline.sh"
  exec "$TEMP_DIR/scripts/install_lifeline.sh" "$@"
else
  echo "Install script not found" >&2
  exit 1
fi
