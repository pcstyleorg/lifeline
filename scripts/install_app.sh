#!/usr/bin/env bash

# LifeLine macOS App Bundle Installer
# Builds and installs the .app bundle to /Applications

set -euo pipefail

draw_banner() {
  printf "============================================\n"
  printf "  LifeLine :: macOS App Bundle Installer\n"
  printf "============================================\n"
}

die() {
  echo "fatal: $1" >&2
  exit 1
}

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    die "missing required command: $1"
  fi
}

main() {
  if [ "$(uname -s)" != "Darwin" ]; then
    die "this installer is for macOS only"
  fi

  draw_banner

  # check we're in the repo
  if [ ! -f "scripts/build_dmg.sh" ]; then
    die "run this from the LifeLine repository root"
  fi

  need_cmd "python3"
  need_cmd "bash"

  printf "building LifeLine app bundle...\n"
  printf "(this may take a few minutes)\n\n"

  # build the DMG (which creates the app bundle)
  bash scripts/build_dmg.sh || die "build failed"

  # check if app bundle exists
  if [ ! -d "build/dmg-stage/LifeLine.app" ]; then
    die "app bundle not found after build"
  fi

  printf "\ninstalling to /Applications...\n"

  # remove old app if it exists
  if [ -d "/Applications/LifeLine.app" ]; then
    printf "removing old installation...\n"
    sudo rm -rf "/Applications/LifeLine.app" || die "failed to remove old app (need sudo)"
  fi

  # install new app
  sudo cp -R "build/dmg-stage/LifeLine.app" "/Applications/" || die "failed to install app (need sudo)"

  printf "\n✓ LifeLine app bundle installed successfully!\n"
  printf "\nTo use:\n"
  printf "  1. Open /Applications/LifeLine.app\n"
  printf "  2. Or run: open /Applications/LifeLine.app\n"
  printf "\n"
}

main "$@"

