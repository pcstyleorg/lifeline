#!/usr/bin/env bash

# LifeLine Standalone Installer
# Downloads repo, installs, supports uninstall
# Works without needing the repo cloned locally

set -euo pipefail

# Configuration
REPO_URL="${LIFELINE_REPO_URL:-https://github.com/pc-style/lifeline.git}"
REPO_BRANCH="${LIFELINE_BRANCH:-main}"
INSTALL_SCRIPT_URL="${LIFELINE_INSTALL_SCRIPT_URL:-}"

# Colors for output (optional)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

die() {
  echo -e "${RED}fatal: $1${NC}" >&2
  exit 1
}

info() {
  echo -e "${GREEN}info: $1${NC}"
}

warn() {
  echo -e "${YELLOW}warning: $1${NC}"
}

download_repo() {
  local temp_dir="$1"
  
  info "Downloading LifeLine repository..."
  
  # Try git clone first (faster, supports branches)
  if command -v git >/dev/null 2>&1; then
    git clone --depth 1 --branch "$REPO_BRANCH" "$REPO_URL" "$temp_dir" 2>/dev/null && return 0
    warn "git clone failed, trying archive download..."
  fi
  
  # Fallback: download archive
  local archive_url
  if [[ "$REPO_URL" == *"github.com"* ]]; then
    # Convert git URL to archive URL
    archive_url="${REPO_URL%.git}/archive/refs/heads/${REPO_BRANCH}.tar.gz"
  else
    die "Cannot determine archive URL for $REPO_URL"
  fi
  
  local archive_file="/tmp/lifeline-archive-$$.tar.gz"
  
  if command -v curl >/dev/null 2>&1; then
    curl -sL "$archive_url" -o "$archive_file" || die "Failed to download archive"
  elif command -v wget >/dev/null 2>&1; then
    wget -q -O "$archive_file" "$archive_url" || die "Failed to download archive"
  else
    die "Need curl or wget to download repository"
  fi
  
  mkdir -p "$temp_dir"
  tar -xzf "$archive_file" -C "$temp_dir" --strip-components=1
  rm -f "$archive_file"
  
  info "Repository downloaded"
}

find_install_dir() {
  # Check common install locations
  local possible_dirs=(
    "$HOME/.local/lifeline"
    "$HOME/lifeline"
    "/opt/lifeline"
  )
  
  for dir in "${possible_dirs[@]}"; do
    if [ -d "$dir" ] && [ -f "$dir/.lifeline-install" ]; then
      echo "$dir"
      return 0
    fi
  done
  
  return 1
}

uninstall() {
  info "Uninstalling LifeLine..."
  
  local install_dir
  if install_dir=$(find_install_dir); then
    info "Found installation at: $install_dir"
  else
    # Try to find it interactively
    echo "Enter LifeLine installation directory (or press Enter to search):"
    read -r install_dir
    
    if [ -z "$install_dir" ]; then
      # Search common locations
      for dir in "$HOME/.local/lifeline" "$HOME/lifeline"; do
        if [ -d "$dir" ]; then
          install_dir="$dir"
          break
        fi
      done
    fi
    
    if [ -z "$install_dir" ] || [ ! -d "$install_dir" ]; then
      die "Could not find LifeLine installation"
    fi
  fi
  
  # Remove alias scripts
  info "Removing aliases..."
  find "$HOME/.local/bin" -name "lifeline" -type f -delete 2>/dev/null || true
  
  # Remove PATH entries from shell config
  info "Removing PATH entries..."
  local shell_rc=""
  if [ -n "${ZSH_VERSION:-}" ]; then
    shell_rc="$HOME/.zshrc"
  elif [ -n "${BASH_VERSION:-}" ]; then
    shell_rc="$HOME/.bashrc"
  else
    shell_rc="$HOME/.profile"
  fi
  
  if [ -f "$shell_rc" ]; then
    # Remove LifeLine PATH entries
    sed -i.bak '/# LifeLine/,/export PATH.*lifeline/d' "$shell_rc" 2>/dev/null || \
    sed -i '' '/# LifeLine/,/export PATH.*lifeline/d' "$shell_rc" 2>/dev/null || true
    info "Removed PATH entries from $shell_rc"
  fi
  
  # Remove desktop shortcuts
  info "Removing desktop shortcuts..."
  rm -f "$HOME/Desktop/LifeLine.command" 2>/dev/null || true
  rm -f "$HOME/Desktop/lifeline.desktop" 2>/dev/null || true
  
  # Remove install directory
  info "Removing installation directory..."
  read -p "Delete $install_dir? [y/N]: " -r </dev/tty
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$install_dir"
    info "Installation directory removed"
  else
    warn "Installation directory kept at $install_dir"
  fi
  
  info "Uninstall complete!"
}

main() {
  # Parse arguments
  case "${1:-}" in
    --uninstall|-u)
      uninstall
      exit 0
      ;;
    --help|-h)
      cat <<EOF
LifeLine Standalone Installer

Usage: $0 [options]

Options:
  --uninstall, -u    Uninstall LifeLine
  --help, -h         Show this help

Environment Variables:
  LIFELINE_REPO_URL     Repository URL (default: $REPO_URL)
  LIFELINE_BRANCH       Branch to install (default: $REPO_BRANCH)

Examples:
  # Install from default repo
  curl -fsSL https://raw.githubusercontent.com/pc-style/lifeline/main/install.sh | bash

  # Install from custom repo
  LIFELINE_REPO_URL=https://github.com/user/repo.git bash install.sh

  # Uninstall
  $0 --uninstall

EOF
      exit 0
      ;;
  esac
  
  # Check if we're in a repo directory (for development)
  if [ -f "scripts/install_lifeline.sh" ]; then
    info "Running local install script..."
    exec ./scripts/install_lifeline.sh "$@"
  fi
  
  # Standalone mode: download repo and run installer
  local temp_dir="/tmp/lifeline-install-$$"
  local cleanup_temp=true
  
  cleanup() {
    if [ "$cleanup_temp" = true ] && [ -d "$temp_dir" ]; then
      rm -rf "$temp_dir"
    fi
  }
  trap cleanup EXIT INT TERM
  
  download_repo "$temp_dir"
  
  # Run the install script from downloaded repo
  if [ -f "$temp_dir/scripts/install_lifeline.sh" ]; then
    info "Running installer..."
    chmod +x "$temp_dir/scripts/install_lifeline.sh"
    cleanup_temp=false  # Let install script handle cleanup if it needs the files
    exec "$temp_dir/scripts/install_lifeline.sh" "$@"
  else
    die "Install script not found in repository"
  fi
}

main "$@"

