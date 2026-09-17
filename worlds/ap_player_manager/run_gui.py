"""Standalone entry point for testing the Player Manager GUI directly.

Bypasses Launcher.py/ModuleUpdate's Python-version gate (3.11.9-3.13.x only),
which is otherwise hit before the GUI ever gets a chance to run on newer
interpreters. Intended for local dev/testing, not as a replacement for the
registered "Player Manager" LauncherComponents entry.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from worlds.ap_player_manager.gui.app import run

if __name__ == "__main__":
    run()
