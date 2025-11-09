"""
Cross-platform paths and configuration helpers for LifeLine.

This module centralizes:
- Application name/slug
- User data/config directories
- Optional .env loading from a predictable location

Design goals:
- No secrets baked into binaries.
- Environment variables remain the primary configuration mechanism.
- Consistent behavior for CLI, web backend, and packaged apps.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

APP_NAME = "LifeLine"
APP_SLUG = "lifeline"


def _is_frozen() -> bool:
    """Return True when running from a PyInstaller bundle."""
    return bool(getattr(sys, "frozen", False))


def get_base_dir() -> Path:
    """
    Get the base directory for resolving bundled resources.

    For PyInstaller:
      - sys._MEIPASS points to the temporary extraction dir.
      - In onefile mode, resources should be placed next to the executable.

    For normal execution:
      - Use the repository root-ish location (directory containing this file, up 1).
    """
    if _is_frozen():
        # Executable directory (onefile) is usually where bundled extras live.
        exe_dir = Path(sys.executable).resolve().parent
        return exe_dir

    # When running from source, assume project root is two levels up from this file: lifeline/paths.py
    return Path(__file__).resolve().parent.parent


def get_frontend_dir(
    override: Optional[str] = None,
    env_var: str = "LIFELINE_FRONTEND_DIR",
) -> Optional[Path]:
    """
    Detect the directory containing built frontend assets.

    Resolution order:
    1. Explicit override argument.
    2. Environment variable (LIFELINE_FRONTEND_DIR).
    3. For frozen/bundled builds, ./frontend relative to the executable/base_dir.
    4. For dev/source layout, ../web-ui/.next/standalone or ../web-ui/.next (if present).

    Returns:
        Path if found, else None.
    """
    if override:
        p = Path(override).expanduser()
        return p if p.exists() else None

    env_val = os.getenv(env_var)
    if env_val:
        p = Path(env_val).expanduser()
        if p.exists():
            return p

    base_dir = get_base_dir()

    # Bundled: expect frontend shipped under base_dir / "frontend"
    candidate = base_dir / "frontend"
    if candidate.exists():
        return candidate

    # Dev mode: look for Next.js output
    repo_root = base_dir
    # If running from lifeline package inside repo, adjust (handles editable installs).
    if (repo_root / "web-ui").exists():
        web_ui_dir = repo_root / "web-ui"
    elif (repo_root.parent / "web-ui").exists():
        web_ui_dir = repo_root.parent / "web-ui"
    else:
        web_ui_dir = None

    if web_ui_dir:
        standalone = web_ui_dir / ".next" / "standalone"
        if standalone.exists():
            return standalone
        next_dir = web_ui_dir / ".next"
        if next_dir.exists():
            return next_dir

    return None


def get_data_dir() -> Path:
    """
    Get the user-writable data directory for LifeLine.

    Strategy:
    - macOS:   ~/Library/Application Support/LifeLine
    - Windows: %APPDATA%\\LifeLine
    - Linux:  ${XDG_DATA_HOME:-~/.local/share}/lifeline

    For backward compatibility, if LIFELINE_DATA_DIR is set, it wins.
    """
    # Explicit override
    override = os.getenv("LIFELINE_DATA_DIR")
    if override:
        path = Path(override).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        return path

    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
        data_dir = base / APP_NAME
    elif os.name == "nt" or sys.platform.startswith("win"):
        appdata = os.getenv("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        data_dir = Path(appdata) / APP_NAME
    else:
        xdg = os.getenv("XDG_DATA_HOME")
        if xdg:
            data_dir = Path(xdg) / APP_SLUG
        else:
            data_dir = Path.home() / ".local" / "share" / APP_SLUG

    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_config_dir() -> Path:
    """
    Get the configuration directory for LifeLine.

    Mirrors get_data_dir() but uses config-oriented locations.
    This is where we might keep a .env or config files.

    Strategy:
    - LIFELINE_CONFIG_DIR overrides default.
    - macOS:   ~/Library/Application Support/LifeLine (same as data for simplicity)
    - Windows: %APPDATA%\\LifeLine
    - Linux:  ${XDG_CONFIG_HOME:-~/.config}/lifeline
    """
    override = os.getenv("LIFELINE_CONFIG_DIR")
    if override:
        path = Path(override).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        return path

    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
        config_dir = base / APP_NAME
    elif os.name == "nt" or sys.platform.startswith("win"):
        appdata = os.getenv("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        config_dir = Path(appdata) / APP_NAME
    else:
        xdg = os.getenv("XDG_CONFIG_HOME")
        if xdg:
            config_dir = Path(xdg) / APP_SLUG
        else:
            config_dir = Path.home() / ".config" / APP_SLUG

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def load_dotenv_from_config(filename: str = ".env") -> None:
    """
    Load a dotenv-style file from the config directory if present.

    - Does nothing if the file is missing.
    - Does not override already-set environment variables.
    - Minimal parser; avoids external dependencies.

    Intended for user-level configuration, not for shipping secrets.
    """
    config_dir = get_config_dir()
    env_path = config_dir / filename
    if not env_path.exists():
        return

    try:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
    except Exception:
        # Fail silently; configuration is best-effort.
        return