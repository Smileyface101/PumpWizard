"""Stable locations for local application state."""
from __future__ import annotations

import os
import sys
from pathlib import Path


def default_data_dir() -> Path:
    if sys.platform == "win32":
        root = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        return Path(root) / "PumpWizard" if root else Path.home() / "AppData" / "Local" / "PumpWizard"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "PumpWizard"
    root = os.environ.get("XDG_DATA_HOME")
    return Path(root) / "pumpwizard" if root else Path.home() / ".local" / "share" / "pumpwizard"

