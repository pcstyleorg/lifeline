#!/usr/bin/env bash

# builds macOS dmg for LifeLine (ish)

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

draw_banner() {
  printf "============================================\n"
  printf "  LifeLine :: dmg kitchen\n"
  printf "============================================\n"
}

die() {
  echo "fatal: $1" >&2
  exit 1
}

need_cmd() {
  local cmd="$1"
  local hint="${2:-}"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    die "missing $cmd $hint"
  fi
}

ensure_uv() {
  if command -v uv >/dev/null 2>&1; then
    return
  fi
  printf "installing uv (bo tak szybciej)\n"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
}

convert_icon() {
  local png_icon="$1"
  local icns_output="$2"
  
  if [ ! -f "$png_icon" ]; then
    printf "warning: icon not found at %s\n" "$png_icon"
    return 1
  fi
  
  printf "converting icon to .icns format...\n"
  
  # create temporary iconset directory
  local iconset_dir="build/LifeLine.iconset"
  rm -rf "$iconset_dir"
  mkdir -p "$iconset_dir"
  
  # macOS requires specific sizes for .icns
  # use sips (built into macOS) to resize
  local sizes=(16 32 64 128 256 512 1024)
  local sizes_2x=(32 64 128 256 512 1024)
  
  for size in "${sizes[@]}"; do
    sips -z "$size" "$size" "$png_icon" --out "$iconset_dir/icon_${size}x${size}.png" >/dev/null 2>&1 || true
  done
  
  for size in "${sizes_2x[@]}"; do
    sips -z "$size" "$size" "$png_icon" --out "$iconset_dir/icon_${size}x${size}@2x.png" >/dev/null 2>&1 || true
  done
  
  # convert iconset to .icns
  iconutil -c icns "$iconset_dir" -o "$icns_output" || {
    printf "warning: iconutil failed, trying alternative method\n"
    # fallback: just copy largest size
    cp "$png_icon" "$icns_output" 2>/dev/null || return 1
  }
  
  rm -rf "$iconset_dir"
  printf "icon converted: %s\n" "$icns_output"
  return 0
}

build_binaries() {
  mkdir -p build
  printf "\n> checking pyinstaller...\n"
  if ! uv run python -c "import PyInstaller" 2>/dev/null; then
    printf "installing pyinstaller...\n"
    uv pip install pyinstaller || die "pyinstaller install failed"
  fi

  printf "\n> bundling CLI with pyinstaller (może chwilę zająć)\n"
  uv run pyinstaller \
    --clean \
    --noconfirm \
    --onefile \
    --name lifeline-cli \
    --add-data "lifeline:lifeline" \
    main.py || die "CLI build failed"

  printf "\n> bundling web server with pyinstaller...\n"
  uv run pyinstaller \
    --clean \
    --noconfirm \
    --onefile \
    --name lifeline-web \
    --add-data "lifeline:lifeline" \
    web.py || die "web server build failed"
}

build_frontend() {
  printf "\n> building Next.js frontend...\n"
  
  if ! command -v npm >/dev/null 2>&1 && ! command -v pnpm >/dev/null 2>&1; then
    printf "warning: npm/pnpm not found, skipping frontend build\n"
    printf "frontend will need to be built separately\n"
    return 0
  fi

  cd web-ui || die "web-ui directory not found"
  
  # use pnpm if available, else npm
  if command -v pnpm >/dev/null 2>&1; then
    printf "using pnpm...\n"
    pnpm install || die "pnpm install failed"
    pnpm build || die "pnpm build failed"
  else
    printf "using npm...\n"
    npm install || die "npm install failed"
    npm run build || die "npm build failed"
  fi
  
  cd ..
  printf "frontend build complete\n"
}

create_app_bundle() {
  local stage_dir="$1"
  local app_bundle="$stage_dir/LifeLine.app"
  local icon_path="${2:-}"
  
  # create proper .app bundle structure
  mkdir -p "$app_bundle/Contents/MacOS"
  mkdir -p "$app_bundle/Contents/Resources"
  
  # copy icon if provided
  if [ -n "$icon_path" ] && [ -f "$icon_path" ]; then
    cp "$icon_path" "$app_bundle/Contents/Resources/icon.icns" 2>/dev/null || true
  fi
  
  # copy executables into Resources
  if [ -f "dist/lifeline-cli" ]; then
    cp dist/lifeline-cli "$app_bundle/Contents/Resources/lifeline-cli"
    chmod +x "$app_bundle/Contents/Resources/lifeline-cli"
  fi
  
  if [ -f "dist/lifeline-web" ]; then
    cp dist/lifeline-web "$app_bundle/Contents/Resources/lifeline-web"
    chmod +x "$app_bundle/Contents/Resources/lifeline-web"
  fi
  
  # copy frontend if built
  if [ -d "web-ui/.next" ]; then
    printf "bundling frontend into app...\n"
    cp -r web-ui/.next "$app_bundle/Contents/Resources/frontend" 2>/dev/null || true
    cp -r web-ui/public "$app_bundle/Contents/Resources/frontend-public" 2>/dev/null || true
  fi
  
  # create launcher script that references Resources
  cat > "$app_bundle/Contents/MacOS/LifeLine" <<'LAUNCHER'
#!/usr/bin/env bash
# LifeLine launcher - starts web interface

set -u  # exit on undefined variable

# better path resolution - works from Finder
# script is at: LifeLine.app/Contents/MacOS/LifeLine
# we need to go up 2 levels to get to .app root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_BUNDLE="$(cd "$SCRIPT_DIR/../.." && pwd)"
RESOURCES_DIR="$APP_BUNDLE/Contents/Resources"
WEB_BIN="$RESOURCES_DIR/lifeline-web"

# logging setup
DATA_DIR="$HOME/.lifeline"
LOG_FILE="$DATA_DIR/lifeline.log"
mkdir -p "$DATA_DIR"

# log function
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE" 2>&1
}

# error dialog function
show_error() {
  osascript -e "display dialog \"$1\" buttons {\"OK\"} default button \"OK\" with icon stop" 2>/dev/null || true
  log "ERROR: $1"
}

# check if web binary exists
if [ ! -f "$WEB_BIN" ]; then
  show_error "LifeLine web server not found at: $WEB_BIN"
  log "App bundle path: $APP_BUNDLE"
  log "Resources dir: $RESOURCES_DIR"
  log "Contents of Resources: $(ls -la "$RESOURCES_DIR" 2>&1)"
  exit 1
fi

# make sure it's executable
chmod +x "$WEB_BIN" 2>/dev/null || true

log "Starting LifeLine..."
log "App bundle: $APP_BUNDLE"
log "Resources: $RESOURCES_DIR"
log "Web binary: $WEB_BIN"

# source .env if it exists (check both app bundle and data dir)
if [ -f "$RESOURCES_DIR/.env" ]; then
  log "Loading .env from Resources"
  set -a
  source "$RESOURCES_DIR/.env" 2>> "$LOG_FILE" || true
  set +a
elif [ -f "$DATA_DIR/.env" ]; then
  log "Loading .env from data dir"
  set -a
  source "$DATA_DIR/.env" 2>> "$LOG_FILE" || true
  set +a
fi

# change to resources dir
cd "$RESOURCES_DIR" || {
  show_error "Cannot change to Resources directory: $RESOURCES_DIR"
  exit 1
}

# start web server in background
log "Starting web server..."
"$WEB_BIN" >> "$LOG_FILE" 2>&1 &
WEB_PID=$!

# wait a bit for server to start
sleep 3

# check if process is still running
if ! kill -0 "$WEB_PID" 2>/dev/null; then
  show_error "Web server crashed. Check log: $LOG_FILE"
  log "Web server process died immediately"
  exit 1
fi

log "Web server started (PID: $WEB_PID)"

# open browser
log "Opening browser..."
open "http://localhost:8000" || {
  log "Failed to open browser"
  show_error "Started server but couldn't open browser. Go to http://localhost:8000"
}

# wait for web server to exit
log "Waiting for web server..."
wait $WEB_PID || {
  EXIT_CODE=$?
  log "Web server exited with code: $EXIT_CODE"
  show_error "Web server stopped unexpectedly. Check log: $LOG_FILE"
  exit $EXIT_CODE
}

log "LifeLine stopped"
LAUNCHER

  chmod +x "$app_bundle/Contents/MacOS/LifeLine"
  
  # create CLI wrapper script in Resources
  cat > "$app_bundle/Contents/Resources/lifeline" <<'CLI_SCRIPT'
#!/usr/bin/env bash
# LifeLine CLI wrapper

# script is at: LifeLine.app/Contents/Resources/lifeline
# go up 2 levels to get to .app root
APP_BUNDLE="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RESOURCES_DIR="$APP_BUNDLE/Contents/Resources"
CLI_BIN="$RESOURCES_DIR/lifeline-cli"

DATA_DIR="$HOME/.lifeline"
mkdir -p "$DATA_DIR"

# source .env if it exists
if [ -f "$RESOURCES_DIR/.env" ]; then
  set -a
  source "$RESOURCES_DIR/.env"
  set +a
elif [ -f "$DATA_DIR/.env" ]; then
  set -a
  source "$DATA_DIR/.env"
  set +a
fi

cd "$RESOURCES_DIR"
exec "$CLI_BIN" "$@"
CLI_SCRIPT

  chmod +x "$app_bundle/Contents/Resources/lifeline"
  
  # create Info.plist
  cat > "$app_bundle/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>LifeLine</string>
  <key>CFBundleIdentifier</key>
  <string>com.lifeline.app</string>
  <key>CFBundleName</key>
  <string>LifeLine</string>
  <key>CFBundleVersion</key>
  <string>1.0</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>LSMinimumSystemVersion</key>
  <string>10.13</string>
PLIST

  # add icon reference if icon exists
  if [ -f "$app_bundle/Contents/Resources/icon.icns" ]; then
    cat >> "$app_bundle/Contents/Info.plist" <<PLIST
  <key>CFBundleIconFile</key>
  <string>icon</string>
PLIST
  fi

  cat >> "$app_bundle/Contents/Info.plist" <<PLIST
</dict>
</plist>
PLIST

  # set icon using fileicon (if available)
  if [ -f "$app_bundle/Contents/Resources/icon.icns" ]; then
    if command -v fileicon >/dev/null 2>&1; then
      fileicon set "$app_bundle" "$app_bundle/Contents/Resources/icon.icns" 2>/dev/null || true
    fi
  fi

  printf "created macOS app bundle with all resources\n"
}

stage_payload() {
  local stage_dir="build/dmg-stage"
  local icon_icns="${1:-}"
  
  rm -rf "$stage_dir"
  mkdir -p "$stage_dir"

  # create the app bundle with everything inside
  create_app_bundle "$stage_dir" "$icon_icns"
  
  # create Applications symlink for easy drag-and-drop
  ln -s /Applications "$stage_dir/Applications"
  
  printf "staged app bundle for DMG\n"
}

make_dmg() {
  local stage_dir="build/dmg-stage"
  local dmg_name="LifeLine.dmg"
  local out="dist/$dmg_name"
  local icon_icns="${1:-}"
  
  rm -f "$out"
  mkdir -p dist
  
  if [ -n "$icon_icns" ] && [ -f "$icon_icns" ]; then
    printf "using icon: %s\n" "$icon_icns"
    cp "$icon_icns" "$stage_dir/.VolumeIcon.icns" 2>/dev/null || true
    if command -v SetFile >/dev/null 2>&1; then
      SetFile -a C "$stage_dir" 2>/dev/null || printf "// SetFile marudzi, ale ikona i tak się skopiuje\n"
    else
      printf "// SetFile brak, Finder sam ogarnie kiedyś indykator\n"
    fi
  else
    printf "warning: brak icon.icns, jadę bez custom ikony\n"
  fi
  
  printf "spinning dmg via hdiutil (klasyka)\n"
  hdiutil create \
    -volname "LifeLine" \
    -srcfolder "$stage_dir" \
    -ov \
    -format UDZO \
    "$out" >/dev/null
  
  printf "\nDMG ready -> %s\n" "$out"
}

main() {
  if [ "$(uname -s)" != "Darwin" ]; then
    printf "sorry, dmg build tylko na macOS\n"
    exit 1
  fi

  draw_banner
  ensure_uv
  need_cmd "python3"
  need_cmd "hdiutil"

  # convert icon (albo użyj gotowca bo życie jest za krótkie)
  local icon_png="$project_root/icon.png"
  local icon_icns="build/LifeLine.icns"
  local icon_prebuilt="$project_root/assets/icons/LifeLine.icns"
  
  if [ -f "$icon_prebuilt" ]; then
    mkdir -p "$(dirname "$icon_icns")"
    cp "$icon_prebuilt" "$icon_icns"
    printf "using prebuilt icns (ktoś już nie spał nad tym)\n"
  elif [ -f "$icon_png" ]; then
    convert_icon "$icon_png" "$icon_icns" || icon_icns=""
  else
    printf "warning: icon.png not found, skipping icon conversion\n"
    icon_icns=""
  fi

  build_binaries
  build_frontend
  stage_payload "$icon_icns"
  make_dmg "$icon_icns"

  printf "\nDone. Drag DMG to friends, post na slacku, etc.\n"
}

main "$@"

