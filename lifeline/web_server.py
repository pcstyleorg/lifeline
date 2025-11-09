"""
Web backend entrypoint for LifeLine.

This module provides:
- A stable importable FastAPI `app` for ASGI servers.
- A `main()` function used by the `lifeline-web` console script and PyInstaller.
- Static frontend serving behavior for bundled/packaged builds.

Behavior:
- Reuses the existing FastAPI app defined in web.py.
- On startup, attempts to locate built frontend assets:
    - If a frontend directory is found (see lifeline.paths.get_frontend_dir),
      mount it at "/" to serve the UI.
    - APIs remain under "/api" (as defined in web.py).
- In dev mode (no bundled frontend found), behavior is backward compatible.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi.staticfiles import StaticFiles

from lifeline.paths import get_frontend_dir
import web as legacy_web  # existing FastAPI app and routes

# Reuse the existing FastAPI app from web.py
app = legacy_web.app


def _mount_frontend_if_available() -> None:
    """
    Detect and mount the built frontend if available.

    Mount points:
    - "/" -> static frontend app (index.html, assets, etc.)
    APIs and websockets defined in web.py (e.g. `/api`, `/ws/chat`) remain unchanged.

    This is idempotent and safe to call multiple times.
    """
    # If already mounted under "/", do nothing.
    for route in app.routes:
        # StaticFiles mounts appear as routes with `path` and an `app` attribute.
        if getattr(route, "path", None) == "/" and getattr(route, "app", None):
            return

    frontend_dir: Optional[Path] = get_frontend_dir()
    if not frontend_dir or not frontend_dir.exists():
        return

    app.mount(
        "/",
        StaticFiles(directory=str(frontend_dir), html=True),
        name="frontend",
    )


def main() -> None:
    """
    Run the LifeLine web backend with optional bundled frontend.

    This is the target for:
    - `lifeline-web` console script (configured in pyproject.toml)
    - PyInstaller web backend binary.
    """
    _mount_frontend_if_available()

    host = os.getenv("LIFELINE_WEB_HOST", "0.0.0.0")
    port_str = os.getenv("LIFELINE_WEB_PORT", "8000")
    try:
        port = int(port_str)
    except ValueError:
        port = 8000

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=os.getenv("LIFELINE_WEB_LOG_LEVEL", "info"),
    )


if __name__ == "__main__":
    main()