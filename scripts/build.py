"""
Unified build orchestrator for LifeLine.

Responsibilities:
- Single source of truth for:
    - Frontend build (Next.js web-ui)
    - PyInstaller binaries (CLI and web)
    - OS-specific bundles/layouts for macOS, Windows, Linux
- Designed to be driven by:
    - `make` targets
    - Thin OS-specific wrappers:
        - scripts/build_macos.sh
        - scripts/build_linux.sh
        - scripts/build_windows.ps1

Key behaviors:
- Uses uv if available (preferred) for Python tooling where needed.
- Uses pnpm if available and lockfile suggests, otherwise falls back to npm.
- Reads project metadata (name, version, description) from pyproject.toml.
- Produces predictable staging layout:
    build/
      frontend/...
      stage/{os}/{component}/...

Usage examples:
- python -m scripts.build --component frontend --target macos
- python -m scripts.build --component cli --target linux
- python -m scripts.build --component all --target windows
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "build"
FRONTEND_BUILD_DIR = BUILD_DIR / "frontend"
STAGE_DIR = BUILD_DIR / "stage"

PYPROJECT_PATH = ROOT / "pyproject.toml"
PYINSTALLER_CLI_SPEC = ROOT / "scripts" / "pyinstaller-cli.spec"
PYINSTALLER_WEB_SPEC = ROOT / "scripts" / "pyinstaller-web.spec"


@dataclass
class ProjectMeta:
    name: str
    version: str
    description: str


def load_project_meta() -> ProjectMeta:
    data = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    proj = data.get("project", {})
    name = proj.get("name", "lifeline")
    version = proj.get("version", "0.0.0")
    description = proj.get("description", "")
    return ProjectMeta(name=name, version=version, description=description)


def which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)


def run(cmd: List[str], cwd: Optional[Path] = None, env: Optional[dict] = None) -> None:
    """Run a command, raising on failure, with simple logging."""
    print(f"[build] Running: {' '.join(cmd)} (cwd={cwd or ROOT})")
    subprocess.run(
        cmd,
        cwd=str(cwd or ROOT),
        env=env or os.environ.copy(),
        check=True,
    )


def ensure_dir(path: Path, clean: bool = False) -> Path:
    if clean and path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def detect_node_pm(web_ui_dir: Path) -> Tuple[str, List[str]]:
    """
    Detect package manager for web-ui.

    Priority:
    - pnpm if pnpm-lock.yaml exists and pnpm is installed.
    - npm (fallback).
    """
    if (web_ui_dir / "pnpm-lock.yaml").exists() and which("pnpm"):
        return "pnpm", ["pnpm"]
    if which("npm"):
        return "npm", ["npm"]
    raise RuntimeError("No supported package manager found (pnpm or npm).")


def build_frontend() -> None:
    """
    Build the Next.js frontend and copy artifacts to build/frontend.

    Strategy:
    - Run `pnpm install` / `npm install` if needed.
    - Run `pnpm build` / `npm run build`.
    - Copy the relevant output into FRONTEND_BUILD_DIR.
      For now, copy the `.next` directory and `public` assets as a bundle.
      This directory is then consumed by lifeline.paths.get_frontend_dir()
      and bundled by PyInstaller for lifeline-web.
    """
    web_ui_dir = ROOT / "web-ui"
    if not web_ui_dir.exists():
        print("[build] web-ui directory not found; skipping frontend build.")
        return

    pm_name, pm = detect_node_pm(web_ui_dir)
    print(f"[build] Using package manager: {pm_name} for web-ui")

    # Install dependencies (non-interactive; rely on lockfiles)
    # Use `install --frozen-lockfile` for pnpm, `ci` for npm if lockfile present.
    if pm_name == "pnpm":
        run(pm + ["install", "--frozen-lockfile"], cwd=web_ui_dir)
        run(pm + ["build"], cwd=web_ui_dir)
    else:  # npm
        lock = web_ui_dir / "package-lock.json"
        if lock.exists():
            run(pm + ["ci"], cwd=web_ui_dir)
        else:
            run(pm + ["install"], cwd=web_ui_dir)
        run(pm + ["run", "build"], cwd=web_ui_dir)

    # Copy artifacts
    ensure_dir(FRONTEND_BUILD_DIR, clean=True)

    # Prefer Next.js standalone if present
    standalone = web_ui_dir / ".next" / "standalone"
    if standalone.exists():
        shutil.copytree(standalone, FRONTEND_BUILD_DIR, dirs_exist_ok=True)
    else:
        # Fallback: copy .next and public
        next_dir = web_ui_dir / ".next"
        if next_dir.exists():
            shutil.copytree(next_dir, FRONTEND_BUILD_DIR / ".next", dirs_exist_ok=True)
        public_dir = web_ui_dir / "public"
        if public_dir.exists():
            shutil.copytree(public_dir, FRONTEND_BUILD_DIR / "public", dirs_exist_ok=True)

    print(f"[build] Frontend assets staged at {FRONTEND_BUILD_DIR}")


def get_pyinstaller_invoker() -> List[str]:
    """
    Return the command prefix to invoke PyInstaller.

    Prefer:
    - `uvx pyinstaller` if uv is available.
    Fallback:
    - `pyinstaller` from PATH
    - `python -m PyInstaller`
    """
    if which("uv"):
        return ["uvx", "pyinstaller"]

    if which("pyinstaller"):
        return ["pyinstaller"]

    # Fallback to python -m if PyInstaller is installed in the current env.
    return [sys.executable, "-m", "PyInstaller"]


def build_cli_binary(target_os: str) -> Path:
    """
    Build lifeline CLI binary via PyInstaller spec.

    Output:
      build/stage/{os}/cli/
    """
    ensure_dir(STAGE_DIR / target_os / "cli", clean=False)
    invoker = get_pyinstaller_invoker()

    cmd = invoker + [
        str(PYINSTALLER_CLI_SPEC),
        "--distpath",
        str(STAGE_DIR / target_os / "cli"),
        "--workpath",
        str(BUILD_DIR / "pyi-work" / target_os / "cli"),
    ]
    run(cmd, cwd=ROOT)

    print(f"[build] CLI binary staged under {STAGE_DIR / target_os / 'cli'}")
    return STAGE_DIR / target_os / "cli"


def build_web_binary(target_os: str) -> Path:
    """
    Build lifeline-web backend binary via PyInstaller spec.

    Output:
      build/stage/{os}/web/
    """
    ensure_dir(STAGE_DIR / target_os / "web", clean=False)
    invoker = get_pyinstaller_invoker()

    cmd = invoker + [
        str(PYINSTALLER_WEB_SPEC),
        "--distpath",
        str(STAGE_DIR / target_os / "web"),
        "--workpath",
        str(BUILD_DIR / "pyi-work" / target_os / "web"),
    ]
    run(cmd, cwd=ROOT)

    print(f"[build] Web binary staged under {STAGE_DIR / target_os / 'web'}")
    return STAGE_DIR / target_os / "web"


def build_macos_bundle(meta: ProjectMeta) -> None:
    """
    Assemble macOS .app and .dmg layout from staged binaries and frontend.

    Layout (inside .app):
      LifeLine.app/
        Contents/
          MacOS/
            LifeLine        (launcher, can be lifeline-web or wrapper)
          Resources/
            lifeline-web    (backend binary)
            frontend/       (copied from build/frontend)
            LifeLine.icns

    The thin wrapper scripts/build_macos.sh will typically call:
      python -m scripts.build --target macos --component all
    """
    target_os = "macos"
    app_name = "LifeLine"
    app_dir = BUILD_DIR / f"{app_name}.app"
    contents_dir = app_dir / "Contents"
    macos_dir = contents_dir / "MacOS"
    resources_dir = contents_dir / "Resources"

    # Ensure binaries exist
    cli_dir = STAGE_DIR / target_os / "cli"
    web_dir = STAGE_DIR / target_os / "web"
    if not cli_dir.exists() or not web_dir.exists():
        print("[build] Missing staged CLI/WEB binaries for macOS; skipping .app assembly.")
        return

    ensure_dir(macos_dir, clean=True)
    ensure_dir(resources_dir, clean=False)

    # Backend binary: assume 'lifeline-web' from PyInstaller
    lifeline_web_bin_candidates = list(web_dir.glob("lifeline-web*"))
    if not lifeline_web_bin_candidates:
        print("[build] lifeline-web binary not found; cannot assemble macOS app.")
        return
    lifeline_web_bin = lifeline_web_bin_candidates[0]
    shutil.copy2(lifeline_web_bin, resources_dir / "lifeline-web")

    # Frontend assets
    if FRONTEND_BUILD_DIR.exists():
        shutil.copytree(FRONTEND_BUILD_DIR, resources_dir / "frontend", dirs_exist_ok=True)

    # CLI binary (optionally bundle for convenience)
    lifeline_cli_candidates = list(cli_dir.glob("lifeline*"))
    if lifeline_cli_candidates:
        shutil.copy2(lifeline_cli_candidates[0], resources_dir / "lifeline")

    # Launcher script/binary (here: small bash wrapper)
    launcher = macos_dir / app_name
    launcher.write_text(
        "#!/bin/bash\n"
        'APP_DIR=\"$(cd \"$(dirname \"${BASH_SOURCE[0]}\")/..\" &>/dev/null && pwd)\"\n'
        'RES_DIR=\"$APP_DIR/Resources\"\n'
        '\"$RES_DIR/lifeline-web\"\n',
        encoding="utf-8",
    )
    launcher.chmod(0o755)

    # Info.plist
    info_plist = contents_dir / "Info.plist"
    info_plist.write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>CFBundleName</key>
    <string>{app_name}</string>
    <key>CFBundleDisplayName</key>
    <string>{app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.example.{meta.name}</string>
    <key>CFBundleVersion</key>
    <string>{meta.version}</string>
    <key>CFBundleShortVersionString</key>
    <string>{meta.version}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleIconFile</key>
    <string>LifeLine.icns</string>
  </dict>
</plist>
""",
        encoding="utf-8",
    )

    # Icon
    icns_src = ROOT / "assets" / "icons" / "LifeLine.icns"
    if icns_src.exists():
        shutil.copy2(icns_src, resources_dir / "LifeLine.icns")

    print(f"[build] macOS app assembled at {app_dir}")
    # .dmg creation left to wrapper or later automation.


def build_windows_layout(meta: ProjectMeta) -> None:
    """
    Prepare Windows layout with:
      - lifeline.exe (CLI)
      - lifeline-web.exe (backend)
      - LifeLine.exe (launcher stub or copy of lifeline-web)

    The wrapper scripts/build_windows.ps1 can consume this layout
    and feed it to an installer system (NSIS/Inno Setup/etc.).
    """
    target_os = "windows"
    out_dir = BUILD_DIR / "windows"
    ensure_dir(out_dir, clean=True)

    cli_dir = STAGE_DIR / target_os / "cli"
    web_dir = STAGE_DIR / target_os / "web"

    lifeline_cli = next(cli_dir.glob("lifeline*.exe"), None) if cli_dir.exists() else None
    lifeline_web = next(web_dir.glob("lifeline-web*.exe"), None) if web_dir.exists() else None

    if lifeline_cli:
        shutil.copy2(lifeline_cli, out_dir / "lifeline.exe")
    if lifeline_web:
        shutil.copy2(lifeline_web, out_dir / "lifeline-web.exe")

    # Launcher (simple wrapper: run lifeline-web.exe)
    launcher = out_dir / "LifeLine.cmd"
    launcher.write_text(
        "@echo off\r\n"
        "setlocal\r\n"
        "set SCRIPT_DIR=%~dp0\r\n"
        "\"%SCRIPT_DIR%lifeline-web.exe\"\r\n",
        encoding="utf-8",
    )

    # Copy frontend if available
    if FRONTEND_BUILD_DIR.exists():
        shutil.copytree(FRONTEND_BUILD_DIR, out_dir / "frontend", dirs_exist_ok=True)

    # Icon wiring for installer is left to external tooling; we only stage assets.
    ico_src = ROOT / "assets" / "icons" / "lifeline.ico"
    if ico_src.exists():
        shutil.copy2(ico_src, out_dir / "lifeline.ico")

    print(f"[build] Windows layout staged at {out_dir}")


def build_linux_layout(meta: ProjectMeta) -> None:
    """
    Prepare Linux layout:
      - lifeline (CLI binary)
      - lifeline-web (backend binary)
      - frontend/ assets
      - .desktop file
      - icon

    Consumers can package this as tarball or AppImage.
    """
    target_os = "linux"
    out_dir = BUILD_DIR / "linux"
    ensure_dir(out_dir, clean=True)

    cli_dir = STAGE_DIR / target_os / "cli"
    web_dir = STAGE_DIR / target_os / "web"

    lifeline_cli = next((p for p in cli_dir.glob("lifeline*") if p.is_file()), None) if cli_dir.exists() else None
    lifeline_web = next((p for p in web_dir.glob("lifeline-web*") if p.is_file()), None) if web_dir.exists() else None

    if lifeline_cli:
        shutil.copy2(lifeline_cli, out_dir / "lifeline")
    if lifeline_web:
        shutil.copy2(lifeline_web, out_dir / "lifeline-web")

    if FRONTEND_BUILD_DIR.exists():
        shutil.copytree(FRONTEND_BUILD_DIR, out_dir / "frontend", dirs_exist_ok=True)

    # Icon
    icon_src = ROOT / "lifeline.png"
    if not icon_src.exists():
        icon_src = ROOT / "icon.png"
    if icon_src.exists():
        shutil.copy2(icon_src, out_dir / "lifeline.png")

    # .desktop file
    desktop = out_dir / "lifeline.desktop"
    desktop.write_text(
        f"""[Desktop Entry]
Type=Application
Name=LifeLine
Comment={meta.description}
Exec={out_dir}/lifeline-web
Icon={out_dir}/lifeline.png
Terminal=false
Categories=Utility;
""",
        encoding="utf-8",
    )

    print(f"[build] Linux layout staged at {out_dir}")


def parse_args(argv: Optional[list] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LifeLine build orchestrator")
    parser.add_argument(
        "--component",
        choices=["cli", "web", "frontend", "all"],
        default="all",
        help="Component to build",
    )
    parser.add_argument(
        "--target",
        choices=["macos", "windows", "linux"],
        default=None,
        help="Target OS; defaults to current platform",
    )
    return parser.parse_args(argv)


def detect_target_os(explicit: Optional[str]) -> str:
    if explicit:
        return explicit
    sysplat = sys.platform
    if sysplat == "darwin":
        return "macos"
    if sysplat.startswith("win"):
        return "windows"
    return "linux"


def main(argv: Optional[list] = None) -> None:
    args = parse_args(argv)
    target_os = detect_target_os(args.target)
    meta = load_project_meta()

    print(f"[build] Target OS: {target_os}")
    print(f"[build] Component: {args.component}")
    print(f"[build] Project: {meta.name} {meta.version}")

    # Frontend
    if args.component in ("frontend", "all"):
        build_frontend()

    # CLI
    if args.component in ("cli", "all"):
        build_cli_binary(target_os)

    # Web
    if args.component in ("web", "all"):
        build_web_binary(target_os)

    # OS-specific bundle/layout
    if args.component == "all":
        if target_os == "macos":
            build_macos_bundle(meta)
        elif target_os == "windows":
            build_windows_layout(meta)
        elif target_os == "linux":
            build_linux_layout(meta)


if __name__ == "__main__":
    main()