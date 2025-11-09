# LifeLine Build & Packaging Guide

This document describes the cross-platform build pipeline implemented for LifeLine.

## Overview

Key components:

- Python package: `lifeline`
- CLI entrypoint: `lifeline` - [`lifeline.cli:main`](lifeline/cli.py:1)
- Web backend entrypoint: `lifeline-web` - [`lifeline.web_server:main`](lifeline/web_server.py:1)
- Next.js frontend: [`web-ui/`](web-ui/README.md)
- Unified build orchestrator: [`scripts.build`](scripts/build.py:1)
- PyInstaller specs:
  - CLI: [`scripts/pyinstaller-cli.spec`](scripts/pyinstaller-cli.spec:1)
  - Web: [`scripts/pyinstaller-web.spec`](scripts/pyinstaller-web.spec:1)
- Thin wrappers:
  - macOS: [`scripts/build_macos.sh`](scripts/build_macos.sh:1)
  - Linux: [`scripts/build_linux.sh`](scripts/build_linux.sh:1)
  - Windows: [`scripts/build_windows.ps1`](scripts/build_windows.ps1:1)

All platform-specific scripts delegate to the Python orchestrator instead of duplicating logic.

## Requirements

- Python 3.10+ (matching project requirements)
- Node.js + pnpm or npm for the frontend
- PyInstaller (resolved automatically via:
  - `uvx pyinstaller` if `uv` is available
  - else `pyinstaller` on PATH
  - else `python -m PyInstaller`)

## Standardized Entry Points

Configured in [`pyproject.toml`](pyproject.toml:1) via `[project.scripts]`:

- `lifeline` → [`lifeline.cli:main`](lifeline/cli.py:1)
- `lifeline-web` → [`lifeline.web_server:main`](lifeline/web_server.py:1)
- `lifeline-mcp` → [`lifeline.mcp_server:main`](lifeline/mcp_server.py:1)

These are the single sources of truth for running from source and for PyInstaller.

## Data and Config Paths

Centralized in [`lifeline.paths`](lifeline/paths.py:1):

- Env overrides:
  - `LIFELINE_DATA_DIR`
  - `LIFELINE_CONFIG_DIR`
- Defaults:
  - macOS: `~/Library/Application Support/LifeLine`
  - Windows: `%APPDATA%\LifeLine`
  - Linux: `${XDG_DATA_HOME:-~/.local/share}/lifeline`
- Optional `.env` loading via `load_dotenv_from_config()` (no override of existing env vars).

No secrets are embedded; API keys (e.g. `OPENAI_API_KEY`) come from env or optional user config.

## Frontend Integration

[`scripts.build`](scripts/build.py:1):

- Detects package manager:
  - `pnpm` if `pnpm-lock.yaml` and `pnpm` available
  - otherwise `npm`
- Builds Next.js app:
  - `pnpm install --frozen-lockfile && pnpm build`
  - or `npm ci`/`npm install` + `npm run build`
- Stages output into:
  - `build/frontend/`

[`lifeline.web_server`](lifeline/web_server.py:1):

- Reuses `app` from [`web.py`](web.py:1).
- On startup:
  - Locates bundled frontend via `get_frontend_dir()`.
  - If found, mounts it at `/` using `StaticFiles`.
  - Existing `/api` + WebSocket endpoints remain unchanged.
- When no frontend is found:
  - Behaves as before for dev/source usage.

## PyInstaller Builds

Spec files:

- CLI: [`scripts/pyinstaller-cli.spec`](scripts/pyinstaller-cli.spec:1)
  - Entry: `-m lifeline.cli`
  - Produces `lifeline` binary.
- Web: [`scripts/pyinstaller-web.spec`](scripts/pyinstaller-web.spec:1)
  - Entry: `-m lifeline.web_server`
  - Produces `lifeline-web` binary.
- Both include `lifeline` package via `collect_submodules("lifeline")`.

Invoked by orchestrator with:

- Custom `--distpath`:
  - `build/stage/{os}/cli`
  - `build/stage/{os}/web`
- Custom `--workpath`:
  - `build/pyi-work/{os}/{component}`

## Unified Build Orchestrator

[`scripts.build`](scripts/build.py:1) (run as `python -m scripts.build`):

Arguments:

- `--component`:
  - `cli`, `web`, `frontend`, `all` (default: `all`)
- `--target`:
  - `macos`, `windows`, `linux`
  - If omitted, auto-detects from `sys.platform`.

Behavior:

1. Loads metadata from [`pyproject.toml`](pyproject.toml:1) for consistent naming.
2. Builds frontend when `component` is `frontend` or `all`.
3. Builds PyInstaller binaries for `cli` and/or `web`.
4. For `--component all`, assembles OS-specific layouts:

### macOS

- Stages into:
  - `build/stage/macos/cli`
  - `build/stage/macos/web`
- Assembles:
  - `build/LifeLine.app`:
    - `Contents/MacOS/LifeLine` launcher script.
    - `Contents/Resources/lifeline-web` backend binary.
    - `Contents/Resources/frontend/` (bundled assets).
    - `Contents/Resources/LifeLine.icns` (from [`assets/icons/LifeLine.icns`](assets/icons/LifeLine.icns:1)).
    - `Contents/Info.plist` using project name/version.
- `.dmg` creation is intentionally left to wrappers/CI tooling.

### Windows

- Stages PyInstaller outputs:
  - `build/stage/windows/cli`
  - `build/stage/windows/web`
- Produces layout:
  - `build/windows/lifeline.exe`
  - `build/windows/lifeline-web.exe`
  - `build/windows/LifeLine.cmd` launcher (runs `lifeline-web.exe`)
  - `build/windows/frontend/` (if built)
  - `build/windows/lifeline.ico` (from [`assets/icons/lifeline.ico`](assets/icons/lifeline.ico:1) if present)
- Installer (NSIS/Inno/etc.) is expected to consume this layout; not bundled here.

### Linux

- Stages PyInstaller outputs:
  - `build/stage/linux/cli`
  - `build/stage/linux/web`
- Produces layout:
  - `build/linux/lifeline`
  - `build/linux/lifeline-web`
  - `build/linux/frontend/` (if built)
  - `build/linux/lifeline.png` (from `lifeline.png` or fallback [`icon.png`](icon.png:1))
  - `build/linux/lifeline.desktop` referencing `lifeline-web`
- Consumers can tarball this or wrap into an AppImage externally.

## OS-specific Thin Wrappers

All wrappers are non-interactive and delegate to the orchestrator.

- macOS:
  - [`scripts/build_macos.sh`](scripts/build_macos.sh:1)
  - Runs:
    - `python3 -m scripts.build --target macos --component all`
- Linux:
  - [`scripts/build_linux.sh`](scripts/build_linux.sh:1)
  - Runs:
    - `python3 -m scripts.build --target linux --component all`
- Windows:
  - [`scripts/build_windows.ps1`](scripts/build_windows.ps1:1)
  - Runs:
    - `python -m scripts.build --target windows --component all`

## Makefile Integration (expected)

Make targets should be thin wrappers (examples):

- `build-cli` → `python -m scripts.build --component cli`
- `build-web` → `python -m scripts.build --component web`
- `build-frontend` → `python -m scripts.build --component frontend`
- `build-macos` → `python -m scripts.build --target macos --component all`
- `build-windows` → `python -m scripts.build --target windows --component all`
- `build-linux` → `python -m scripts.build --target linux --component all`
- `build-all` → run for all supported targets.

(If not yet wired, these targets can be added without changing orchestrator logic.)

## CI Usage

Non-interactive commands suitable for CI:

- macOS:
  - `scripts/build_macos.sh`
  - or `python -m scripts.build --target macos --component all`
- Windows:
  - `powershell -File scripts/build_windows.ps1`
  - or `python -m scripts.build --target windows --component all`
- Linux:
  - `scripts/build_linux.sh`
  - or `python -m scripts.build --target linux --component all`

All outputs are under `build/` in predictable subdirectories for upload/signing/notarization.