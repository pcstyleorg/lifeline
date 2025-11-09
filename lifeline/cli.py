# ... existing code ...
"""
LifeLine CLI entrypoint.

Thin wrapper around the interactive CLI implemented in main.py.
This module exists so that the `lifeline` console_script entrypoint can be
stable and PyInstaller-friendly.
"""

from __future__ import annotations

import asyncio
import sys
from typing import NoReturn

from main import main as _async_main


def main() -> NoReturn:
    """
    Synchronous entrypoint for the LifeLine CLI.

    Runs the async main() defined in main.py and exits with its status code.
    """
    try:
        asyncio.run(_async_main())
    except KeyboardInterrupt:
        # Match existing behavior from main.py when interrupted.
        sys.exit(0)