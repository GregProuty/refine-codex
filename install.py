#!/usr/bin/env python3
"""Install this skill into the current user's Codex skill directory."""
from pathlib import Path
import os
import shutil
import sys

SOURCE = Path(__file__).resolve().parent
HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
TARGETS = {"codex": HOME / "skills" / "refine", "claude": Path.home() / ".claude" / "skills" / "refine"}
selected = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--target=")), "both")
if selected not in ("codex", "claude", "both"):
    print("Usage: python install.py [--update] [--target=codex|claude|both]", file=sys.stderr)
    sys.exit(2)
DESTINATIONS = [TARGETS[k] for k in (("codex", "claude") if selected == "both" else (selected,))]

for DEST in DESTINATIONS:
    if DEST.is_symlink():
        print(f"Refusing to write through symlink: {DEST}", file=sys.stderr)
        sys.exit(1)
    if DEST.exists() and "--update" not in sys.argv[1:]:
        print(f"Refusing to replace existing skill: {DEST} (pass --update to refresh)", file=sys.stderr)
        sys.exit(1)

for DEST in DESTINATIONS:
    shutil.copytree(SOURCE, DEST, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(".git", ".tmp", "__pycache__", "*.pyc"))
    print(f"Installed: {DEST}")
