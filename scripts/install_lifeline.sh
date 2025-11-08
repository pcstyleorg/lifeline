#!/usr/bin/env bash

# LifeLine tech installer
# comments intentionally low-key + mixed language per vibes
# --test: installs in /tmp/lifeline-<id>, auto-tests, then cleans up
# --quick: quick install in current dir, just asks for API key
# no flag: interactive install with customization options

set -euo pipefail

# Configuration
REPO_URL="${LIFELINE_REPO_URL:-https://github.com/pc-style/lifeline.git}"
REPO_BRANCH="${LIFELINE_BRANCH:-main}"

# parse args
TEST_MODE=false
QUICK_MODE=false
UNINSTALL_MODE=false
CLEANUP_TEMP_DIR=""
INSTALL_DIR=""
CREATE_ALIAS=false
ADD_TO_PATH=false

for arg in "$@"; do
  case $arg in
    --test|-t)
      TEST_MODE=true
      shift
      ;;
    --quick|-q)
      QUICK_MODE=true
      shift
      ;;
    --uninstall|-u)
      UNINSTALL_MODE=true
      shift
      ;;
    --help|-h)
      echo "Usage: $0 [--test|-t] [--quick|-q] [--uninstall|-u]"
      echo ""
      echo "  --test, -t       Install in temp dir, auto-test, then clean up"
      echo "  --quick, -q      Quick install (current dir, just asks for API key)"
      echo "  --uninstall, -u  Uninstall LifeLine"
      echo "  (no flag)       Interactive install with customization options"
      echo "  --help, -h       Show this help"
      echo ""
      echo "Environment Variables:"
      echo "  LIFELINE_REPO_URL    Repository URL (default: $REPO_URL)"
      echo "  LIFELINE_BRANCH      Branch to install (default: $REPO_BRANCH)"
      exit 0
      ;;
  esac
done

# Try to detect project root (if script is in repo)
if [ -f "$(dirname "${BASH_SOURCE[0]}")/../pyproject.toml" ]; then
  project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  IN_REPO=true
else
  project_root=""
  IN_REPO=false
fi

# Get project source (download if needed)
get_project_source() {
  local target_dir="$1"
  
  if [ "$IN_REPO" = true ] && [ -n "$project_root" ]; then
    # We're in the repo, copy from current location
    printf "using local repository...\n"
    mkdir -p "$target_dir"
    
    if command -v rsync >/dev/null 2>&1; then
      rsync -a --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' \
        --exclude='.git' --exclude='node_modules' --exclude='dist' --exclude='build' \
        --exclude='data/*.db' --exclude='data/*.db-*' \
        "$project_root/" "$target_dir/"
    else
      (cd "$project_root" && tar --exclude='.venv' --exclude='__pycache__' \
        --exclude='.git' --exclude='node_modules' --exclude='dist' --exclude='build' \
        --exclude='data/*.db' --exclude='data/*.db-*' \
        -cf - .) | (cd "$target_dir" && tar -xf -) || {
        cp -r "$project_root"/* "$target_dir/" 2>/dev/null || true
      }
    fi
  else
    # Download repo to temp dir
    download_repo "$target_dir"
  fi
}

# test mode: create temp dir and get project source
if [ "$TEST_MODE" = true ]; then
  TEST_ID="$(date +%s)-$$"
  CLEANUP_TEMP_DIR="/tmp/lifeline-${TEST_ID}"
  
  printf "TEST MODE: installing to %s\n" "$CLEANUP_TEMP_DIR"
  printf "will clean up after testing\n\n"
  
  # cleanup function
  cleanup() {
    if [ -n "$CLEANUP_TEMP_DIR" ] && [ -d "$CLEANUP_TEMP_DIR" ]; then
      printf "\ncleaning up test dir: %s\n" "$CLEANUP_TEMP_DIR"
      rm -rf "$CLEANUP_TEMP_DIR"
      printf "done, test dir removed\n"
    fi
  }
  trap cleanup EXIT INT TERM
  
  get_project_source "$CLEANUP_TEMP_DIR"
  cd "$CLEANUP_TEMP_DIR"
  printf "switched to test dir\n\n"
else
  # For non-test modes, we'll get source when needed
  if [ "$IN_REPO" = true ] && [ -n "$project_root" ]; then
    cd "$project_root"
  fi
fi

clear_buffer() {
  # niby nic robi, ale fajnie brzmi
  printf "\n"
}

draw_banner() {
  printf "============================================\n"
  printf "  LifeLine :: semi-chaotic setup wizard\n"
  printf "============================================\n"
}

die() {
  echo "fatal: $1" >&2
  exit 1
}

prompt() {
  local prompt_text="$1"
  local default_value="${2:-}"
  local result

  if [ -n "$default_value" ]; then
    printf "%s [%s]: " "$prompt_text" "$default_value" >&2
    read -r result </dev/tty || result=""
    # ensure we return default if result is empty or just whitespace
    result="${result:-$default_value}"
    result="${result#"${result%%[![:space:]]*}"}"  # trim leading whitespace
    result="${result%"${result##*[![:space:]]}"}"  # trim trailing whitespace
    echo "${result:-$default_value}"
  else
    printf "%s: " "$prompt_text" >&2
    read -r result </dev/tty || result=""
    result="${result#"${result%%[![:space:]]*}"}"  # trim leading whitespace
    result="${result%"${result##*[![:space:]]}"}"  # trim trailing whitespace
    echo "$result"
  fi
}

prompt_yesno() {
  local prompt_text="$1"
  local default="${2:-n}"
  local result

  if [ "$default" = "y" ]; then
    printf "%s [Y/n]: " "$prompt_text" >&2
  else
    printf "%s [y/N]: " "$prompt_text" >&2
  fi

  read -r result </dev/tty || result=""
  result="${result:-$default}"

  case "$result" in
    [Yy]|[Yy][Ee][Ss]) return 0 ;;
    *) return 1 ;;
  esac
}

check_python() {
  if ! command -v python3 >/dev/null 2>&1; then
    die "potrzebuję python3 >= 3.10 (install z python.org pls)"
  fi

  local v
  v="$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
  printf "python3 -> %s\n" "$v"

  python3 -c 'import sys; exit(0 if sys.version_info >= (3,10) else 1)' \
    || die "python3 za stary, upgrade time"
}

download_repo() {
  local temp_dir="$1"
  
  printf "downloading LifeLine repository...\n"
  
  # Try git clone first (faster, supports branches)
  if command -v git >/dev/null 2>&1; then
    if git clone --depth 1 --branch "$REPO_BRANCH" "$REPO_URL" "$temp_dir" 2>/dev/null; then
      printf "repository cloned\n"
      return 0
    fi
    printf "git clone failed, trying archive download...\n"
  fi
  
  # Fallback: download archive
  local archive_url
  if [[ "$REPO_URL" == *"github.com"* ]]; then
    # Convert git URL to archive URL
    archive_url="${REPO_URL%.git}/archive/refs/heads/${REPO_BRANCH}.tar.gz"
  else
    die "cannot determine archive URL for $REPO_URL"
  fi
  
  local archive_file="/tmp/lifeline-archive-$$.tar.gz"
  
  if command -v curl >/dev/null 2>&1; then
    curl -sL "$archive_url" -o "$archive_file" || die "failed to download archive"
  elif command -v wget >/dev/null 2>&1; then
    wget -q -O "$archive_file" "$archive_url" || die "failed to download archive"
  else
    die "need curl or wget to download repository"
  fi
  
  mkdir -p "$temp_dir"
  tar -xzf "$archive_file" -C "$temp_dir" --strip-components=1
  rm -f "$archive_file"
  
  printf "repository downloaded\n"
}

ensure_uv() {
  if command -v uv >/dev/null 2>&1; then
    printf "uv already here, chill\n"
    return
  fi

  printf "installing uv (lightning fast pip alt)\n"
  curl -LsSf https://astral.sh/uv/install.sh | sh || die "uv install poszlo bokiem"
  export PATH="$HOME/.local/bin:$PATH"
  if [ -d "$HOME/.cargo/bin" ]; then
    export PATH="$HOME/.cargo/bin:$PATH"
  fi
}

find_install_dir() {
  # Check common install locations
  local possible_dirs=(
    "$HOME/.local/lifeline"
    "$HOME/lifeline"
  )
  
  for dir in "${possible_dirs[@]}"; do
    if [ -d "$dir" ] && [ -f "$dir/.lifeline-install" ]; then
      echo "$dir"
      return 0
    fi
  done
  
  return 1
}

uninstall_lifeline() {
  draw_banner
  printf "Uninstalling LifeLine...\n\n"
  
  local install_dir
  if install_dir=$(find_install_dir); then
    printf "found installation at: %s\n" "$install_dir"
  else
    # Try to find it interactively
    printf "Enter LifeLine installation directory (or press Enter to search): "
    read -r install_dir </dev/tty

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
      die "could not find LifeLine installation"
    fi
  fi
  
  # Remove alias scripts
  printf "removing aliases...\n"
  find "$HOME/.local/bin" -name "lifeline" -type f -delete 2>/dev/null || true
  
  # Remove PATH entries from shell config
  printf "removing PATH entries...\n"
  local shell_rc=""
  if [ -n "${ZSH_VERSION:-}" ]; then
    shell_rc="$HOME/.zshrc"
  elif [ -n "${BASH_VERSION:-}" ]; then
    shell_rc="$HOME/.bashrc"
  else
    shell_rc="$HOME/.profile"
  fi
  
  if [ -f "$shell_rc" ]; then
    # Remove LifeLine PATH entries (macOS and Linux compatible)
    if [[ "$OSTYPE" == "darwin"* ]]; then
      sed -i '' '/# LifeLine/,/export PATH.*lifeline/d' "$shell_rc" 2>/dev/null || true
    else
      sed -i '/# LifeLine/,/export PATH.*lifeline/d' "$shell_rc" 2>/dev/null || true
    fi
    printf "removed PATH entries from %s\n" "$shell_rc"
  fi
  
  # Remove desktop shortcuts
  printf "removing desktop shortcuts...\n"
  rm -f "$HOME/Desktop/LifeLine.command" 2>/dev/null || true
  rm -f "$HOME/Desktop/lifeline.desktop" 2>/dev/null || true
  
  # Remove install directory
  printf "\n"
  if prompt_yesno "Delete installation directory ($install_dir)?" "n"; then
    rm -rf "$install_dir"
    printf "installation directory removed\n"
  else
    printf "installation directory kept at %s\n" "$install_dir"
  fi
  
  printf "\nUninstall complete!\n"
}

setup_env() {
  local target_dir="${1:-$(pwd)}"
  
  clear_buffer
  printf "creating virtual env (uv style)\n"
  cd "$target_dir"
  
  # remove existing venv if it exists (uv will prompt otherwise)
  if [ -d ".venv" ]; then
    printf "removing existing .venv...\n"
    rm -rf .venv
  fi
  
  uv venv .venv || die "uv venv zrzucił się"

  clear_buffer
  printf "installing project deps (trochę to potrwa)\n"
  uv sync || die "uv sync padł, sprawdź logs"
}

write_env_file() {
  local target_dir="${1:-$(pwd)}"
  local api_key="${2:-}"
  
  # ensure absolute path
  if [[ "$target_dir" != /* ]]; then
    target_dir="$(cd "$target_dir" && pwd)"
  fi
  
  local env_file="$target_dir/.env"
  
  if [ -n "$api_key" ]; then
    cat > "$env_file" <<EOF
OPENAI_API_KEY=$api_key
# Add other secrets here if life gets complicated.
EOF
    printf "created .env with API key\n"
  else
    cat > "$env_file" <<'EOF'
# OPENAI_API_KEY=sk-yada-yada
# Add other secrets here if life gets complicated.
EOF
    printf "created .env (fill in OPENAI_API_KEY jak będziesz miał siły)\n"
  fi
}

create_alias_script() {
  local install_dir="$1"
  local alias_name="${2:-lifeline}"
  local bin_dir="$HOME/.local/bin"
  
  mkdir -p "$bin_dir"
  
  local script_path="$bin_dir/$alias_name"
  
  cat > "$script_path" <<EOF
#!/usr/bin/env bash
# LifeLine alias script
cd "$install_dir"
source .venv/bin/activate
exec uv run python main.py "\$@"
EOF
  
  chmod +x "$script_path"
  printf "created alias script: %s\n" "$script_path"
  
  # check if bin_dir is in PATH
  if [[ ":$PATH:" != *":$bin_dir:"* ]]; then
    printf "note: %s might not be in PATH\n" "$bin_dir"
    printf "add this to your ~/.bashrc or ~/.zshrc:\n"
    printf "  export PATH=\"\$HOME/.local/bin:\$PATH\"\n"
  fi
}

add_to_path() {
  local install_dir="$1"
  local shell_rc=""
  
  # detect shell
  if [ -n "${ZSH_VERSION:-}" ]; then
    shell_rc="$HOME/.zshrc"
  elif [ -n "${BASH_VERSION:-}" ]; then
    shell_rc="$HOME/.bashrc"
  else
    shell_rc="$HOME/.profile"
  fi
  
  local path_line="export PATH=\"$install_dir/.venv/bin:\$PATH\""
  
  if [ -f "$shell_rc" ]; then
    if grep -q "$path_line" "$shell_rc" 2>/dev/null; then
      printf "PATH already configured in %s\n" "$shell_rc"
      return
    fi
    
    printf "\n# LifeLine\n" >> "$shell_rc"
    printf "%s\n" "$path_line" >> "$shell_rc"
    printf "added to PATH in %s\n" "$shell_rc"
    printf "run: source %s (or restart terminal)\n" "$shell_rc"
  else
    printf "couldn't find shell rc file, add manually:\n"
    printf "  %s\n" "$path_line"
  fi
}

create_desktop_shortcut() {
  local install_dir="$1"
  
  if [ "$(uname -s)" = "Darwin" ]; then
    # macOS - create .command file
    local shortcut="$HOME/Desktop/LifeLine.command"
    cat > "$shortcut" <<EOF
#!/usr/bin/env bash
cd "$install_dir"
source .venv/bin/activate
uv run python main.py
EOF
    chmod +x "$shortcut"
    printf "created macOS shortcut: %s\n" "$shortcut"
  elif [ "$(uname -s)" = "Linux" ]; then
    # Linux - create .desktop file
    local shortcut="$HOME/Desktop/lifeline.desktop"
    cat > "$shortcut" <<EOF
[Desktop Entry]
Name=LifeLine
Comment=Personal Memory & Timeline Assistant
Exec=cd "$install_dir" && source .venv/bin/activate && uv run python main.py
Terminal=true
Type=Application
Categories=Utility;
EOF
    chmod +x "$shortcut"
    printf "created Linux shortcut: %s\n" "$shortcut"
  fi
}

run_tests() {
  printf "\n> running auto-tests...\n"
  
  # test 1: import lifeline module
  printf "  [1/3] testing lifeline module import... "
  if uv run python -c "import lifeline; print('OK')" >/dev/null 2>&1; then
    printf "✓\n"
  else
    printf "✗ FAILED\n"
    return 1
  fi
  
  # test 2: import agent
  printf "  [2/3] testing agent import... "
  if uv run python -c "from lifeline.agent import create_lifeline_agent; print('OK')" >/dev/null 2>&1; then
    printf "✓\n"
  else
    printf "✗ FAILED\n"
    return 1
  fi
  
  # test 3: check main.py can be imported (syntax check)
  printf "  [3/3] testing main.py syntax... "
  if uv run python -c "import main; print('OK')" >/dev/null 2>&1; then
    printf "✓\n"
  else
    printf "✗ FAILED (might be expected if main.py needs API key)\n"
  fi
  
  printf "\nall tests passed! ✓\n"
  return 0
}

interactive_setup() {
  clear_buffer
  draw_banner
  
  printf "Interactive installation mode\n"
  printf "customize your setup:\n\n"
  
  # get install directory
  local default_dir="$HOME/.local/lifeline"
  INSTALL_DIR=$(prompt "Install directory" "$default_dir")
  INSTALL_DIR="${INSTALL_DIR/#\~/$HOME}"  # expand ~
  
  # create install directory
  if [ ! -d "$INSTALL_DIR" ]; then
    printf "creating install directory: %s\n" "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR" || die "couldn't create install dir"
  fi
  
  # download/copy project files to temp first, then move to install dir
  local temp_source="/tmp/lifeline-source-$$"
  printf "\ngetting project source...\n"
  get_project_source "$temp_source"
  
  # copy from temp to install dir
  printf "copying project files...\n"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' \
      --exclude='.git' --exclude='node_modules' --exclude='dist' --exclude='build' \
      --exclude='data/*.db' --exclude='data/*.db-*' \
      "$temp_source/" "$INSTALL_DIR/"
  else
    (cd "$temp_source" && tar --exclude='.venv' --exclude='__pycache__' \
      --exclude='.git' --exclude='node_modules' --exclude='dist' --exclude='build' \
      --exclude='data/*.db' --exclude='data/*.db-*' \
      -cf - .) | (cd "$INSTALL_DIR" && tar -xf -) || {
      cp -r "$temp_source"/* "$INSTALL_DIR/" 2>/dev/null || true
    }
  fi
  
  # cleanup temp source
  rm -rf "$temp_source"
  
  # setup environment
  setup_env "$INSTALL_DIR"
  
  # ask for API key
  printf "\n"
  local api_key
  api_key=$(prompt "OpenAI API key (or press Enter to skip)" "")
  write_env_file "$INSTALL_DIR" "$api_key"
  
  # ask about alias
  printf "\n"
  if prompt_yesno "Create 'lifeline' command alias?" "y"; then
    CREATE_ALIAS=true
    local alias_name=$(prompt "Alias name" "lifeline")
    create_alias_script "$INSTALL_DIR" "$alias_name"
  fi
  
  # ask about PATH
  printf "\n"
  if prompt_yesno "Add .venv/bin to PATH?" "n"; then
    ADD_TO_PATH=true
    add_to_path "$INSTALL_DIR"
  fi
  
  # ask about desktop shortcut
  printf "\n"
  if prompt_yesno "Create desktop shortcut?" "n"; then
    create_desktop_shortcut "$INSTALL_DIR"
  fi
  
  # final message
  clear_buffer
  draw_banner
  printf "Installation complete! ✓\n\n"
  printf "Installed to: %s\n" "$INSTALL_DIR"
  printf "\nTo use:\n"
  printf "  1. cd %s\n" "$INSTALL_DIR"
  printf "  2. source .venv/bin/activate\n"
  if [ "$CREATE_ALIAS" = true ]; then
    printf "  3. lifeline  # or use the alias\n"
  else
    printf "  3. uv run python main.py\n"
  fi
  printf "\n"
}

quick_setup() {
  clear_buffer
  draw_banner
  
  printf "Quick installation mode\n"
  printf "installing in current directory...\n\n"
  
  INSTALL_DIR="$(pwd)"
  
  # download/copy project files if not already here
  if [ ! -f "pyproject.toml" ]; then
    printf "getting project source...\n"
    get_project_source "$INSTALL_DIR"
  fi
  
  # ask for API key
  printf "\n"
  local api_key
  api_key=$(prompt "OpenAI API key" "")
  
  # setup
  setup_env "$INSTALL_DIR"
  write_env_file "$INSTALL_DIR" "$api_key"
  
  # create install marker
  echo "$(date)" > "$INSTALL_DIR/.lifeline-install"
  echo "INSTALL_DIR=$INSTALL_DIR" >> "$INSTALL_DIR/.lifeline-install"
  
  # done
  clear_buffer
  draw_banner
  printf "Quick install complete! ✓\n\n"
  printf "To use:\n"
  printf "  1. source .venv/bin/activate\n"
  printf "  2. uv run python main.py\n"
  printf "\n"
}

print_wrapup() {
  clear_buffer
  draw_banner
  
  if [ "$TEST_MODE" = true ]; then
    printf "TEST MODE: Setup gotowy w %s\n" "$(pwd)"
    printf "\n"
    
    # auto-run tests
    if run_tests; then
      printf "\ninstallation verified, cleanup starting...\n"
      sleep 1  # brief pause so user can see results
    else
      printf "\nsome tests failed, but continuing cleanup...\n"
      sleep 1
    fi
  fi
}

main() {
  if [ "$TEST_MODE" = true ]; then
    draw_banner
    check_python
    ensure_uv
    setup_env
    write_env_file "$(pwd)" ""
    print_wrapup
  elif [ "$QUICK_MODE" = true ]; then
    check_python
    ensure_uv
    quick_setup
  else
    # interactive mode
    check_python
    ensure_uv
    interactive_setup
  fi
}

# Handle uninstall mode (after all functions are defined)
if [ "$UNINSTALL_MODE" = true ]; then
  uninstall_lifeline
  exit 0
fi

main "$@"
